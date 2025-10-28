"""
Unit tests for metric configuration system.

Tests the new SOLID-compliant metric configuration architecture.
"""

import pytest
from pydantic import ValidationError

from services.test.metric_config import (
    MetricRegistry,
    MetricCategory,
    BaseMetricConfig,
    ExactMatchConfig,
    FuzzyMatchConfig,
    SemanticSimilarityConfig,
    KeywordPatternPresenceConfig,
    OutputLengthConfig,
    ToolsCalledConfig,
    JsonSchemaVerificationConfig,
    AnswerRelevancyConfig,
    FaithfulnessConfig,
    ProfessionalismConfig,
    ConcisenessConfig,
)
from services.test.models import MetricType, ExpectedEvaluationFieldsModel


class TestMetricConfigClasses:
    """Test individual metric configuration classes."""
    
    def test_exact_match_config(self):
        """Test ExactMatchConfig creation and validation."""
        config = ExactMatchConfig(expected_output="Hello world")
        
        assert config.expected_output == "Hello world"
        assert config.get_metric_type_name() == "exact_match"
        assert config.get_category() == MetricCategory.DETERMINISTIC
        assert "exact" in config.get_description().lower()
        assert config.get_required_actual_fields() == ["actual_output"]
        assert "expected_output" in config.get_required_expected_field_names()
    
    def test_exact_match_config_validation_error(self):
        """Test ExactMatchConfig raises error when required field missing."""
        with pytest.raises(ValidationError):
            ExactMatchConfig(expected_output=None)  # type: ignore - Testing validation error
    
    def test_fuzzy_match_config(self):
        """Test FuzzyMatchConfig with optional json_field."""
        config = FuzzyMatchConfig(
            expected_output="Test output",
            json_field="data.result"
        )
        
        assert config.expected_output == "Test output"
        assert config.json_field == "data.result"
        assert config.get_category() == MetricCategory.DETERMINISTIC
    
    def test_keyword_pattern_config(self):
        """Test KeywordPatternPresenceConfig with multiple field types."""
        config = KeywordPatternPresenceConfig(
            expected_keywords=["hello", "world"],
            expected_patterns=[r"\d+"],
            forbidden_keywords=["bad"]
        )
        
        assert config.expected_keywords is not None and len(config.expected_keywords) == 2
        assert config.expected_patterns is not None and len(config.expected_patterns) == 1
        assert config.forbidden_keywords is not None and len(config.forbidden_keywords) == 1
    
    def test_output_length_config(self):
        """Test OutputLengthConfig with min/max constraints."""
        config = OutputLengthConfig(
            min_length=10,
            max_length=100,
            length_unit="words"
        )
        
        assert config.min_length == 10
        assert config.max_length == 100
        assert config.length_unit == "words"
    
    def test_tools_called_config(self):
        """Test ToolsCalledConfig with tool list."""
        config = ToolsCalledConfig(
            expected_tools=[
                {"name": "search", "args": {}},
                {"name": "calculate", "args": {}}
            ]
        )
        
        assert len(config.expected_tools) == 2
        assert config.get_required_actual_fields() == ["actual_output", "tools_called"]
    
    def test_json_schema_config(self):
        """Test JsonSchemaVerificationConfig."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            }
        }
        config = JsonSchemaVerificationConfig(expected_schema=schema)
        
        assert config.expected_schema == schema
    
    def test_faithfulness_config(self):
        """Test FaithfulnessConfig for RAG metrics."""
        config = FaithfulnessConfig(
            retrieval_context=["Context 1", "Context 2"]
        )
        
        assert len(config.retrieval_context) == 2
        assert config.get_category() == MetricCategory.NON_DETERMINISTIC
    
    def test_professionalism_config(self):
        """Test ProfessionalismConfig with no required fields."""
        config = ProfessionalismConfig()
        
        assert config.get_category() == MetricCategory.NON_DETERMINISTIC
        assert len(config.get_required_expected_field_names()) == 0
        assert config.get_required_actual_fields() == ["actual_output"]


class TestMetricRegistry:
    """Test MetricRegistry functionality."""
    
    def test_get_config_class(self):
        """Test getting configuration class by metric type."""
        config_class = MetricRegistry.get_config_class("exact_match")
        assert config_class == ExactMatchConfig
        
        config_class = MetricRegistry.get_config_class("professionalism")
        assert config_class == ProfessionalismConfig
    
    def test_get_config_class_invalid_type(self):
        """Test error handling for invalid metric type."""
        with pytest.raises(ValueError, match="Unknown metric type"):
            MetricRegistry.get_config_class("invalid_metric")
    
    def test_get_all_metric_types(self):
        """Test retrieving all registered metric types."""
        types = MetricRegistry.get_all_metric_types()
        
        assert "exact_match" in types
        assert "fuzzy_match" in types
        assert "professionalism" in types
        assert "conciseness" in types
        assert len(types) >= 17  # Should have all metrics
    
    def test_get_metric_metadata(self):
        """Test retrieving metadata for a metric type."""
        metadata = MetricRegistry.get_metric_metadata("exact_match")
        
        assert metadata["type"] == "exact_match"
        assert metadata["category"] == "deterministic"
        assert "description" in metadata
        assert "required_expected_fields" in metadata
        assert "required_actual_fields" in metadata
        assert "field_schema" in metadata
        assert "expected_output" in metadata["required_expected_fields"]
        assert "actual_output" in metadata["required_actual_fields"]
    
    def test_get_all_metrics_metadata(self):
        """Test retrieving metadata for all metrics."""
        all_metadata = MetricRegistry.get_all_metrics_metadata()
        
        assert isinstance(all_metadata, dict)
        assert "exact_match" in all_metadata
        assert "professionalism" in all_metadata
        
        # Verify each entry has required keys
        for metric_type, metadata in all_metadata.items():
            assert "type" in metadata
            assert "category" in metadata
            assert "description" in metadata
            assert "required_expected_fields" in metadata
            assert "required_actual_fields" in metadata
    
    def test_register_custom_metric(self):
        """Test registering a custom metric at runtime."""
        
        class CustomTestConfig(BaseMetricConfig):
            custom_field: str
            
            @classmethod
            def get_metric_type_name(cls) -> str:
                return "custom_test"
            
            @classmethod
            def get_category(cls) -> MetricCategory:
                return MetricCategory.DETERMINISTIC
            
            @classmethod
            def get_description(cls) -> str:
                return "Custom test metric"
            
            @classmethod
            def get_required_actual_fields(cls) -> list:
                return ["actual_output"]
        
        MetricRegistry.register_metric("custom_test", CustomTestConfig)
        
        # Verify registration
        config_class = MetricRegistry.get_config_class("custom_test")
        assert config_class == CustomTestConfig
        
        # Verify it appears in metadata
        metadata = MetricRegistry.get_metric_metadata("custom_test")
        assert metadata["type"] == "custom_test"


class TestMetricTypeIntegration:
    """Test MetricType enum integration with MetricRegistry."""
    
    def test_metric_type_description(self):
        """Test that MetricType.description delegates to config."""
        desc = MetricType.EXACT_MATCH.description
        
        assert "exact" in desc.lower()
        assert isinstance(desc, str)
    
    def test_metric_type_category(self):
        """Test that MetricType.category works correctly."""
        assert MetricType.EXACT_MATCH.category == MetricCategory.DETERMINISTIC
        assert MetricType.PROFESSIONALISM.category == MetricCategory.NON_DETERMINISTIC
    
    def test_is_deterministic(self):
        """Test is_deterministic classification."""
        assert MetricType.is_deterministic(MetricType.EXACT_MATCH) is True
        assert MetricType.is_deterministic(MetricType.FUZZY_MATCH) is True
        assert MetricType.is_deterministic(MetricType.PROFESSIONALISM) is False
    
    def test_is_non_deterministic(self):
        """Test is_non_deterministic classification."""
        assert MetricType.is_non_deterministic(MetricType.PROFESSIONALISM) is True
        assert MetricType.is_non_deterministic(MetricType.EXACT_MATCH) is False
    
    def test_get_required_expected_fields(self):
        """Test getting required expected fields for metric types."""
        fields = MetricType.get_required_expected_fields(MetricType.EXACT_MATCH)
        assert "expected_output" in fields
        
        fields = MetricType.get_required_expected_fields(MetricType.FAITHFULNESS)
        assert "retrieval_context" in fields
    
    def test_get_required_actual_fields(self):
        """Test getting required actual fields for metric types."""
        fields = MetricType.get_required_actual_fields(MetricType.EXACT_MATCH)
        assert "actual_output" in fields
        
        fields = MetricType.get_required_actual_fields(MetricType.TOOLS_CALLED)
        assert "actual_output" in fields
        assert "tools_called" in fields


class TestExpectedEvaluationFieldsModel:
    """Test ExpectedEvaluationFieldsModel with new architecture."""
    
    def test_from_metric_config(self):
        """Test creating ExpectedEvaluationFieldsModel from config."""
        config = ExactMatchConfig(expected_output="Test output")
        model = ExpectedEvaluationFieldsModel.from_metric_config(
            MetricType.EXACT_MATCH,
            config
        )
        
        assert model.metric_type == MetricType.EXACT_MATCH
        assert model.config is not None
        assert model.config["expected_output"] == "Test output"
    
    def test_to_metric_config(self):
        """Test converting back to metric-specific config."""
        original_config = FuzzyMatchConfig(
            expected_output="Test",
            json_field="data.result"
        )
        model = ExpectedEvaluationFieldsModel.from_metric_config(
            MetricType.FUZZY_MATCH,
            original_config
        )
        
        restored_config = model.to_metric_config()
        
        assert isinstance(restored_config, FuzzyMatchConfig)
        assert restored_config.expected_output == "Test"
        assert restored_config.json_field == "data.result"
    
    def test_get_config_value(self):
        """Test retrieving specific config values."""
        config = OutputLengthConfig(
            min_length=10,
            max_length=100,
            length_unit="words"
        )
        model = ExpectedEvaluationFieldsModel.from_metric_config(
            MetricType.OUTPUT_LENGTH,
            config
        )
        
        assert model.get_config_value("min_length") == 10
        assert model.get_config_value("max_length") == 100
        assert model.get_config_value("length_unit") == "words"
        assert model.get_config_value("nonexistent") is None
    
    def test_validation_with_invalid_config(self):
        """Test that validation catches invalid configurations."""
        with pytest.raises(ValueError, match="Invalid configuration"):
            ExpectedEvaluationFieldsModel(
                metric_type=MetricType.EXACT_MATCH,
                config={}  # Missing required expected_output
            )
    
    def test_empty_model(self):
        """Test creating empty model."""
        model = ExpectedEvaluationFieldsModel()
        
        assert model.metric_type is None
        assert model.config is None
        assert model.to_metric_config() is None


class TestFieldSchemaGeneration:
    """Test JSON schema generation for frontend consumption."""
    
    def test_exact_match_schema(self):
        """Test schema generation for ExactMatchConfig."""
        schema = ExactMatchConfig.get_field_schema()
        
        assert "properties" in schema
        assert "expected_output" in schema["properties"]
        assert "required" in schema
        assert "expected_output" in schema["required"]
    
    def test_keyword_pattern_schema(self):
        """Test schema for complex config with optional fields."""
        schema = KeywordPatternPresenceConfig.get_field_schema()
        
        assert "properties" in schema
        assert "expected_keywords" in schema["properties"]
        assert "expected_patterns" in schema["properties"]
        assert "forbidden_keywords" in schema["properties"]
        
        # All fields are optional for this metric
        assert schema.get("required", []) == []
    
    def test_metadata_includes_schema(self):
        """Test that metadata includes field schema."""
        metadata = MetricRegistry.get_metric_metadata("exact_match")
        
        assert "field_schema" in metadata
        assert "properties" in metadata["field_schema"]