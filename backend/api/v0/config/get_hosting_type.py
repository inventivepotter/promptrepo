"""
Get hosting type endpoint without authentication.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from services.config_service import config_service

router = APIRouter()


class HostingTypeResponse(BaseModel):
    """Response for hosting type endpoint"""
    hosting_type: str


@router.get("/hosting-type", response_model=HostingTypeResponse)
async def get_hosting_type():
    """
    Get current hosting type without authentication.
    This endpoint is publicly accessible to determine UI behavior.
    """
    try:
        hosting_type = config_service.get_hosting_type()
        return HostingTypeResponse(hosting_type=hosting_type)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get hosting type: {str(e)}"
        )