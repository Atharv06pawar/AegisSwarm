"""
HeartbeatMonitor module checking worker node health and evicting stale or unresponsive workers.
"""

import threading
from datetime import datetime, timezone
from typing import Dict, List, Optional

from cluster.worker_pool import WorkerPool
from cluster.models import WorkerState, HeartbeatPayload
from cluster.config import ClusterConfig
from cluster.exceptions import HeartbeatError


class HeartbeatMonitor:
    """
    Heartbeat monitor verifying periodic worker heartbeats and updating node status.
    """

    def __init__(self, pool: WorkerPool, config: Optional[ClusterConfig] = None):
        self.pool = pool
        self.config = config or ClusterConfig()
        self._lock = threading.RLock()
        self._latest_payloads: Dict[str, HeartbeatPayload] = {}

    def record_heartbeat(self, payload: HeartbeatPayload) -> None:
        """Records a heartbeat payload from a worker node."""
        with self._lock:
            wid_str = str(payload.worker_id)
            self._latest_payloads[wid_str] = payload
            
            worker = self.pool.find_worker(payload.worker_id)
            if worker:
                worker.node.last_heartbeat = payload.timestamp
                if worker.node.status == WorkerState.OFFLINE:
                    worker.node.status = WorkerState.ONLINE

    def check_health(self) -> Dict[str, List[str]]:
        """
        Scans registered workers and identifies healthy, stale, or dead workers based on timeout threshold.
        """
        with self._lock:
            now = datetime.now(timezone.utc)
            healthy: List[str] = []
            dead: List[str] = []

            for w in self.pool.list_workers():
                try:
                    hb_time = datetime.fromisoformat(w.node.last_heartbeat)
                    delta_sec = (now - hb_time).total_seconds()
                    if delta_sec > self.config.heartbeat_timeout_seconds:
                        w.node.status = WorkerState.OFFLINE
                        dead.append(str(w.node.worker_id))
                    else:
                        healthy.append(str(w.node.worker_id))
                except Exception:
                    w.node.status = WorkerState.FAILED
                    dead.append(str(w.node.worker_id))

            return {"healthy": healthy, "dead": dead}
