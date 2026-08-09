"""
FastAPI Router for Distributed Campaign Engine endpoints.
"""

from uuid import UUID
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response

from campaign.models import CampaignConfig, CampaignMetrics, CampaignResult, CampaignSummary
from campaign.manager import CampaignManager
from campaign.exceptions import CampaignNotFound, CampaignStateError, CampaignError
from api.dependencies import get_campaign_manager

campaigns_router = APIRouter(prefix="/campaigns", tags=["Campaign Subsystem"])


@campaigns_router.post("", response_model=CampaignConfig, status_code=201)
def create_campaign(
    config: CampaignConfig,
    manager: CampaignManager = Depends(get_campaign_manager)
):
    """Creates a new distributed campaign specification."""
    try:
        return manager.create_campaign(config)
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


@campaigns_router.get("", response_model=List[CampaignConfig])
def list_campaigns(
    manager: CampaignManager = Depends(get_campaign_manager)
):
    """Lists all registered campaign specifications."""
    return manager.list_campaigns()


@campaigns_router.get("/{campaign_id}", response_model=CampaignConfig)
def get_campaign(
    campaign_id: UUID,
    manager: CampaignManager = Depends(get_campaign_manager)
):
    """Retrieves a campaign specification by UUID."""
    try:
        return manager.load_campaign(campaign_id)
    except CampaignNotFound:
        raise HTTPException(status_code=404, detail=f"Campaign '{campaign_id}' not found.")


@campaigns_router.post("/{campaign_id}/start")
def start_campaign(
    campaign_id: UUID,
    manager: CampaignManager = Depends(get_campaign_manager)
):
    """Starts execution of a campaign."""
    try:
        # For API execution, if no custom records provided, run baseline schedule
        from tests.test_execution_models import create_sample_attack_record
        sample_record = create_sample_attack_record()
        result = manager.start_campaign(campaign_id, [sample_record])
        return result
    except CampaignNotFound:
        raise HTTPException(status_code=404, detail=f"Campaign '{campaign_id}' not found.")
    except CampaignStateError as e:
        raise HTTPException(status_code=409, detail=str(e))


@campaigns_router.post("/{campaign_id}/pause", response_model=CampaignConfig)
def pause_campaign(
    campaign_id: UUID,
    manager: CampaignManager = Depends(get_campaign_manager)
):
    """Pauses a running campaign."""
    try:
        return manager.pause_campaign(campaign_id)
    except CampaignNotFound:
        raise HTTPException(status_code=404, detail=f"Campaign '{campaign_id}' not found.")


@campaigns_router.post("/{campaign_id}/resume")
def resume_campaign(
    campaign_id: UUID,
    manager: CampaignManager = Depends(get_campaign_manager)
):
    """Resumes a paused campaign."""
    try:
        return manager.resume_campaign(campaign_id)
    except CampaignNotFound:
        raise HTTPException(status_code=404, detail=f"Campaign '{campaign_id}' not found.")


@campaigns_router.post("/{campaign_id}/cancel", response_model=CampaignConfig)
def cancel_campaign(
    campaign_id: UUID,
    manager: CampaignManager = Depends(get_campaign_manager)
):
    """Cancels a campaign."""
    try:
        return manager.cancel_campaign(campaign_id)
    except CampaignNotFound:
        raise HTTPException(status_code=404, detail=f"Campaign '{campaign_id}' not found.")


@campaigns_router.get("/{campaign_id}/metrics", response_model=CampaignMetrics)
def get_campaign_metrics(
    campaign_id: UUID,
    manager: CampaignManager = Depends(get_campaign_manager)
):
    """Retrieves live metrics for a campaign."""
    return manager.get_metrics(campaign_id)


@campaigns_router.get("/{campaign_id}/report")
def get_campaign_report(
    campaign_id: UUID,
    format: str = Query("markdown", description="Report format: 'markdown', 'json', or 'csv'"),
    manager: CampaignManager = Depends(get_campaign_manager)
):
    """Generates an audit report for a campaign."""
    try:
        report_str = manager.get_report(campaign_id, format_type=format)
        media_type = "text/markdown"
        if format.lower() == "json":
            media_type = "application/json"
        elif format.lower() == "csv":
            media_type = "text/csv"
        return Response(content=report_str, media_type=media_type)
    except CampaignNotFound:
        raise HTTPException(status_code=404, detail=f"Campaign '{campaign_id}' not found.")
