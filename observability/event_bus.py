"""
Thread-Safe EventBus for publishing, subscribing, broadcasting, replaying, and persisting TelemetryEvents.
"""

import json
import copy
import threading
import logging
from pathlib import Path
from typing import Dict, List, Callable, Optional, Set
from observability.models import TelemetryEvent
from observability.exceptions import EventBusError

logger = logging.getLogger(__name__)

# Type alias for subscribers
SubscriberCallback = Callable[[TelemetryEvent], None]


class EventBus:
    """
    Thread-safe EventBus providing publish/subscribe semantics, wildcard listeners,
    in-memory event replay history, and atomic disk persistence to outputs/telemetry/events.jsonl.
    """

    def __init__(self, base_dir: Path = Path("outputs/telemetry")):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._subscribers: Dict[str, List[SubscriberCallback]] = {}
        self._global_subscribers: List[SubscriberCallback] = []
        self._event_history: List[TelemetryEvent] = []

    def subscribe(self, event_type: str, callback: SubscriberCallback) -> None:
        """
        Subscribes a callback listener to a specific event type or wildcard '*'.
        """
        with self._lock:
            if event_type == "*":
                if callback not in self._global_subscribers:
                    self._global_subscribers.append(callback)
            else:
                if event_type not in self._subscribers:
                    self._subscribers[event_type] = []
                if callback not in self._subscribers[event_type]:
                    self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: SubscriberCallback) -> None:
        """
        Unsubscribes a callback listener.
        """
        with self._lock:
            if event_type == "*" and callback in self._global_subscribers:
                self._global_subscribers.remove(callback)
            elif event_type in self._subscribers and callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)

    def publish(self, event: TelemetryEvent) -> None:
        """
        Publishes a TelemetryEvent: appends to history and dispatches to subscribers.
        """
        with self._lock:
            self._event_history.append(event)
            listeners = list(self._subscribers.get(event.event_type, [])) + list(self._global_subscribers)

        for callback in listeners:
            try:
                callback(event)
            except Exception as err:
                logger.error(f"Error in EventBus subscriber callback for '{event.event_type}': {err}")

    def broadcast(self, event: TelemetryEvent) -> None:
        """
        Broadcasts an event to all subscribers (alias to publish).
        """
        self.publish(event)

    def replay(self) -> List[TelemetryEvent]:
        """
        Returns a copy snapshot of all recorded telemetry events in history.
        """
        with self._lock:
            return copy.deepcopy(self._event_history)

    def clear(self) -> None:
        """
        Clears event history.
        """
        with self._lock:
            self._event_history.clear()

    def persist(self, base_dir: Optional[Path] = None) -> Path:
        """
        Persists event history into outputs/telemetry/events.jsonl.
        """
        with self._lock:
            target_dir = Path(base_dir) if base_dir else self.base_dir
            target_dir.mkdir(parents=True, exist_ok=True)
            file_path = target_dir / "events.jsonl"
            tmp_path = target_dir / "events.jsonl.tmp"

            try:
                with open(tmp_path, "w", encoding="utf-8") as f:
                    for ev in self._event_history:
                        f.write(ev.model_dump_json() + "\n")
                
                tmp_path.replace(file_path)
                logger.info(f"Persisted {len(self._event_history)} events to {file_path}")
                return file_path
            except Exception as err:
                raise EventBusError(f"Failed to persist events: {err}") from err
