"""
Metrics metadata endpoint for eval framework.

Provides information about available metrics for frontend consumption.
"""
import logging
from fastapi import APIRouter, Request, status

from services.artifacts.evals.models import MetricsMetadataResponse
from lib.deepeval.metric_config import MetricRegistry
from middlewares.rest import StandardResponse, success_response, AppException

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/metadata",
    response_model=StandardResponse[MetricsMetadataResponse],
    status_code=status.HTTP_200_OK,
    responses={
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/internal-server-error",
                        "title": "Internal Server Error",
                        "detail": "Failed to retrieve metrics metadata"
                    }
                }
            }
        }
    },
    summary="Get all metrics metadata",
    description="Retrieve metadata for all registered eval metrics including field schemas, descriptions, and requirements.",
)
async def get_metrics_metadata(
    request: Request
) -> StandardResponse[MetricsMetadataResponse]:
    """
    Get metadata for all registered metrics.
    
    Returns information about:
    - Metric type and category (deterministic/non-deterministic)
    - Description of what the metric evaluates
    - Required expected fields (user must provide)
    - Required actual fields (from eval execution)
    - JSON schema for dynamic form generation
    
    Returns:
        StandardResponse containing metrics metadata
    
    Raises:
        AppException: When metadata retrieval fails
    """
    request_id = request.state.request_id
    
    try:
        logger.info(
            "Fetching metrics metadata",
            extra={"request_id": request_id}
        )
        
        # Get all metrics metadata from registry
        metrics_metadata = MetricRegistry.get_all_metrics_metadata()
        
        logger.info(
            f"Retrieved metadata for {len(metrics_metadata)} metrics",
            extra={"request_id": request_id}
        )
        
        return success_response(
            data=metrics_metadata,
            message=f"Successfully retrieved metadata for {len(metrics_metadata)} metrics",
            meta={"request_id": request_id}
        )
        
    except AppException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to retrieve metrics metadata: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise AppException(
            message="Failed to retrieve metrics metadata",
            detail=str(e)
        )