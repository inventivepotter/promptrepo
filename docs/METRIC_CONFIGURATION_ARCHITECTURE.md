# Metric Configuration Architecture

## Overview

This document describes the new SOLID-compliant metric configuration system that addresses scalability and maintainability issues in the test evaluation framework.

## Problems Solved

### Previous Issues

1. **Single Responsibility Principle (SRP) Violation**
   - `ExpectedEvaluationFieldsModel` was a "god object" with 20+ fields
   - Single model serving all metric types with different requirements

2. **Open/Closed Principle (OCP) Violation**
   - Adding new metrics required modifying multiple locations
   - Giant switch statements in `get_required_fields_for_metric()`

3. **Frontend Coupling Issues**
   - No clear way for frontend to know which fields to show for each metric
   - No type-safe validation of metric-specific configurations

4. **Runtime Field Requirements**
   - Unclear distinction between expected fields (user-provided) and actual fields (execution results)
   - Metrics using `getattr()` with defaults (code smell)

## New Architecture

### 1. Strategy Pattern with Metric-Specific Configs

Each metric type now has its own configuration class that extends `BaseMetricConfig`:

```python
class BaseMetricConfig(BaseModel, ABC):
    """Base configuration for all metrics."""
    
    @classmethod
    @abstractmethod
    def get_metric_type_name(cls) -> str:
        """Return the metric type name this config is for."""
        pass
    
    @classmethod
    @abstractmethod
    def get_category(cls) -> MetricCategory:
        """Return whether this metric is deterministic or non-deterministic."""
        pass
    
    @classmethod
    @abstractmethod
    def get_description(cls) -> str:
        """Return human-readable description of what this metric evaluates."""
        pass
    
    @classmethod
    @abstractmethod
    def get_required_actual_fields(cls) -> List[str]:
        """Return list of required ACTUAL fields from test execution."""
        pass
    
    @classmethod
    def get_required_expected_field_names(cls) -> List[str]:
        """Get list of required EXPECTED field names for this metric."""
        # Auto-derived from Pydantic model fields
        pass
```

### 2. Metric Registry for Centralized Management

The `MetricRegistry` class provides a single source of truth for all metrics:

```python
class MetricRegistry:
    """Registry for all metric configurations."""
    
    @classmethod
    def get_config_class(cls, metric_type: str) -> Type[BaseMetricConfig]:
        """Get the configuration class for a metric type."""
        pass
    
    @classmethod
    def get_metric_metadata(cls, metric_type: str) -> Dict[str, Any]:
        """Get metadata about a metric type for frontend consumption."""
        return {
            "type": metric_type,
            "category": config_class.get_category().value,
            "description": config_class.get_description(),
            "required_expected_fields": config_class.get_required_expected_field_names(),
            "required_actual_fields": config_class.get_required_actual_fields(),
            "field_schema": config_class.get_field_schema()
        }
    
    @classmethod
    def get_all_metrics_metadata(cls) -> Dict[str, Dict[str, Any]]:
        """Get metadata for all registered metrics."""
        pass
```

### 3. Expected vs Actual Fields Distinction

**Expected Fields** (User-Provided in Test Definition):
- Fields that users configure when creating a test case
- Example: `expected_output`, `retrieval_context`, `min_length`
- Obtained via `get_required_expected_field_names()`

**Actual Fields** (Runtime Execution Results):
- Fields that must be present from test execution to evaluate
- Example: `actual_output`, `tools_called`, `execution_time_ms`
- Obtained via `get_required_actual_fields()`

### 4. Refactored ExpectedEvaluationFieldsModel

Uses composition instead of inheritance:

```python
class ExpectedEvaluationFieldsModel(BaseModel):
    """Expected evaluation fields for test definition."""
    
    metric_type: Optional[MetricType] = None
    config: Optional[Dict[str, Any]] = None  # Metric-specific config
    
    @classmethod
    def from_metric_config(cls, metric_type: MetricType, config: BaseMetricConfig):
        """Create from a metric-specific config."""
        return cls(
            metric_type=metric_type,
            config=config.model_dump(exclude_none=True)
        )
    
    def to_metric_config(self) -> Optional[BaseMetricConfig]:
        """Convert to metric-specific configuration object."""
        if not self.metric_type or not self.config:
            return None
        
        config_class = MetricType.get_config_class(self.metric_type)
        return config_class(**self.config)
```

## Example Metric Configurations

### Deterministic Metric Example: ExactMatchConfig

```python
class ExactMatchConfig(BaseMetricConfig):
    """Configuration for exact match metric."""
    
    expected_output: str = Field(
        description="Expected output for exact comparison"
    )
    
    @classmethod
    def get_metric_type_name(cls) -> str:
        return "exact_match"
    
    @classmethod
    def get_category(cls) -> MetricCategory:
        return MetricCategory.DETERMINISTIC
    
    @classmethod
    def get_description(cls) -> str:
        return "Compares the actual output exactly against the expected output"
    
    @classmethod
    def get_required_actual_fields(cls) -> List[str]:
        return ["actual_output"]
```

### Non-Deterministic Metric Example: FaithfulnessConfig

```python
class FaithfulnessConfig(BaseMetricConfig):
    """Configuration for faithfulness metric."""
    
    retrieval_context: List[str] = Field(
        description="Context for RAG evaluation metrics"
    )
    
    @classmethod
    def get_metric_type_name(cls) -> str:
        return "faithfulness"
    
    @classmethod
    def get_category(cls) -> MetricCategory:
        return MetricCategory.NON_DETERMINISTIC
    
    @classmethod
    def get_description(cls) -> str:
        return "Evaluates whether the answer is factually consistent with the context"
    
    @classmethod
    def get_required_actual_fields(cls) -> List[str]:
        return ["actual_output"]
```

### Complex Metric Example: KeywordPatternPresenceConfig

```python
class KeywordPatternPresenceConfig(BaseMetricConfig):
    """Configuration for keyword/pattern presence metric."""
    
    expected_keywords: Optional[List[str]] = Field(
        default=None,
        description="Expected keywords that must be present in output"
    )
    expected_patterns: Optional[List[str]] = Field(
        default=None,
        description="Expected regex patterns that must be present in output"
    )
    forbidden_keywords: Optional[List[str]] = Field(
        default=None,
        description="Keywords that must NOT be present in output"
    )
    
    @classmethod
    def get_metric_type_name(cls) -> str:
        return "keyword_pattern_presence"
    
    @classmethod
    def get_category(cls) -> MetricCategory:
        return MetricCategory.DETERMINISTIC
    
    @classmethod
    def get_description(cls) -> str:
        return "Checks for the presence of required keywords or patterns"
    
    @classmethod
    def get_required_actual_fields(cls) -> List[str]:
        return ["actual_output"]
```

## Usage Examples

### Frontend: Getting Available Metrics

```python
# Get all metrics with their metadata for UI
all_metrics = MetricRegistry.get_all_metrics_metadata()

# Result:
{
    "exact_match": {
        "type": "exact_match",
        "category": "deterministic",
        "description": "Compares the actual output exactly...",
        "required_expected_fields": ["expected_output"],
        "required_actual_fields": ["actual_output"],
        "field_schema": {
            "properties": {
                "expected_output": {"type": "string", ...}
            },
            "required": ["expected_output"]
        }
    },
    ...
}
```

### Backend: Creating Test Configuration

```python
# Create metric-specific config
exact_match_config = ExactMatchConfig(
    expected_output="Hello world"
)

# Create test evaluation fields
eval_fields = ExpectedEvaluationFieldsModel.from_metric_config(
    MetricType.EXACT_MATCH,
    exact_match_config
)

# Use in test definition
test = UnitTestDefinition(
    name="test_greeting",
    prompt_reference="prompts/greeting.txt",
    template_variables={"name": "Alice"},
    evaluation_fields=eval_fields
)
```

### Backend: Runtime Metric Instantiation

```python
# During test execution, convert back to metric config
metric_config = eval_fields.to_metric_config()

# Instantiate the actual metric for evaluation
if isinstance(metric_config, ExactMatchConfig):
    metric = ExactMatchMetric()
    # Use metric_config.expected_output for evaluation
    
# Or get specific values
expected_output = eval_fields.get_config_value("expected_output")
```

### Adding a New Metric

1. **Create configuration class** in `metric_config.py`:

```python
class NewMetricConfig(BaseMetricConfig):
    """Configuration for new metric."""
    
    custom_field: str = Field(description="Custom field")
    
    @classmethod
    def get_metric_type_name(cls) -> str:
        return "new_metric"
    
    @classmethod
    def get_category(cls) -> MetricCategory:
        return MetricCategory.DETERMINISTIC
    
    @classmethod
    def get_description(cls) -> str:
        return "Description of new metric"
    
    @classmethod
    def get_required_actual_fields(cls) -> List[str]:
        return ["actual_output"]
```

2. **Register in MetricRegistry**:

```python
_registry: Dict[str, Type[BaseMetricConfig]] = {
    ...
    "new_metric": NewMetricConfig,
}
```

3. **Add to MetricType enum** in `models.py`:

```python
class MetricType(str, Enum):
    ...
    NEW_METRIC = "new_metric"
```

4. **Implement the metric class** in `deepeval/custom_metrics/`:

```python
class NewMetric(BaseMetric):
    def __init__(self):
        self.score = 0.0
        self.reason = ""
        self.success = False
        self.error = None
    
    def measure(self, test_case: LLMTestCase) -> float:
        # Implementation
        pass
```

That's it! The frontend automatically gets:
- Field schema for form generation
- Required fields list
- Description for UI
- Validation rules

## Benefits

### 1. **Single Responsibility**
- Each metric config class has one job: define configuration for that metric
- No more giant models with fields for every possible metric

### 2. **Open/Closed Principle**
- Adding new metrics doesn't require modifying existing code
- Just create a new config class and register it

### 3. **Type Safety**
- Pydantic validates metric-specific configurations
- Frontend gets JSON schema for dynamic form generation

### 4. **Clear Separation of Concerns**
- Expected fields (user input) vs Actual fields (execution results)
- Configuration vs Evaluation logic

### 5. **Easy Frontend Integration**
- Single API call to get all metric metadata
- JSON schemas for dynamic form generation
- Clear validation rules

### 6. **Testability**
- Each metric config can be tested independently
- Easy to mock and verify

### 7. **Extensibility**
- Custom metrics can be registered at runtime
- Plugin architecture for third-party metrics

## Migration Guide

### For Existing Tests

The new system maintains backward compatibility. Existing test definitions will need to be migrated to use metric-specific configurations, but the core structure remains the same.

### For Frontend

Frontend should:
1. Call `MetricRegistry.get_all_metrics_metadata()` on initialization
2. Use the `field_schema` to generate dynamic forms
3. Use `required_expected_fields` to validate user input
4. Send metric-specific config in the format expected by the new models

### For Backend Services

Services that execute tests should:
1. Use `eval_fields.to_metric_config()` to get typed configuration
2. Use `get_required_actual_fields()` to validate execution results
3. Pass configuration to metric classes appropriately

## File Structure

```
backend/services/test/
├── metric_config.py          # NEW: Metric configuration system
├── models.py                  # UPDATED: Uses MetricRegistry
├── test_metric_config.py      # NEW: Tests for configuration system
├── test_custom_metrics.py     # UPDATED: Tests for metric implementations
└── deepeval/
    └── custom_metrics/
        ├── __init__.py
        ├── exact_match_metric.py
        ├── fuzzy_match_metric.py
        ├── professionalism_metric.py
        └── ... (other metrics)
```

## Next Steps

1. ✅ Create metric configuration system
2. ✅ Update models to use MetricRegistry
3. ✅ Add comprehensive tests
4. ⏳ Update metric execution in test service
5. ⏳ Create API endpoint for getting metric metadata
6. ⏳ Update frontend to use new metadata API
7. ⏳ Migrate existing test definitions

## Conclusion

This new architecture follows SOLID principles, provides clear separation between expected and actual fields, and makes it easy to add new metrics without modifying existing code. The frontend gets all the information it needs through a single API, and the backend has type-safe, validated configurations for each metric type.