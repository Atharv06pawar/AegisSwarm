"""
FastAPI Router for Telemetry, Monitoring & Observability Platform endpoints.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query

from observability.models import TelemetryEvent, TraceModel
from observability.collector import TelemetryCollector
from observability.dashboard import TelemetryDashboard
from api.dependencies import get_telemetry_collector, get_telemetry_dashboard

telemetry_router = APIRouter(prefix="/telemetry", tags=["Observability Subsystem"])


@telemetry_router.get("")
def get_telemetry_overview(
    dashboard: TelemetryDashboard = Depends(get_telemetry_dashboard)
):
    """Retrieves high-level telemetry overview and operational status."""
    return dashboard.get_dashboard_data()


@telemetry_router.get("/events", response_model=List[TelemetryEvent])
def get_telemetry_events(
    collector: TelemetryCollector = Depends(get_telemetry_collector)
):
    """Retrieves replayed history list of TelemetryEvents."""
    return collector.event_bus.replay()


@telemetry_router.get("/metrics")
def get_telemetry_metrics(
    collector: TelemetryCollector = Depends(get_telemetry_collector)
):
    """Retrieves aggregated metrics summary."""
    return collector.metrics_collector.summary()


@telemetry_router.get("/traces", response_model=List[TraceModel])
def get_telemetry_traces(
    collector: TelemetryCollector = Depends(get_telemetry_collector)
):
    """Retrieves distributed trace models."""
    return collector.tracer.list_traces()


@telemetry_router.get("/dashboard")
def get_telemetry_dashboard_endpoint(
    dashboard: TelemetryDashboard = Depends(get_telemetry_dashboard)
):
    """Retrieves live monitoring command center metrics."""
    return dashboard.get_dashboard_data()


@telemetry_router.get("/providers")
def get_provider_telemetry(
    dashboard: TelemetryDashboard = Depends(get_telemetry_dashboard)
):
    """Retrieves provider utilization and latency status."""
    data = dashboard.get_dashboard_data()
    return {
        "providers": data["provider_status"],
        "provider_utilization": data["provider_utilization"]
    }


@telemetry_router.get("/campaigns")
def get_campaign_telemetry(
    dashboard: TelemetryDashboard = Depends(get_telemetry_dashboard)
):
    """Retrieves campaign operational telemetry."""
    data = dashboard.get_dashboard_data()
    return {
        "active_campaigns": data["active_campaigns"],
        "running_workers": data["running_workers"],
        "attacks_per_min": data["attacks_per_min"]
    }


@telemetry_router.post("/reset")
def reset_telemetry(
    collector: TelemetryCollector = Depends(get_telemetry_collector)
):
    """Resets all in-memory event, metrics, and trace accumulators."""
    collector.event_bus.clear()
    collector.metrics_collector.reset()
    return {"status": "reset_completed", "message": "Telemetry state successfully reset."}
