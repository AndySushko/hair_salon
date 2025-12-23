# observer.py
from __future__ import annotations
import json
import threading
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional


class Observer:
    def update(self, event: str, data: dict) -> None:
        raise NotImplementedError


class Subject:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._observers_by_key: Dict[str, List[Observer]] = {}

    def attach(self, key: str, obs: Observer) -> None:
        with self._lock:
            self._observers_by_key.setdefault(key, []).append(obs)

    def detach(self, key: str, obs: Observer) -> None:
        with self._lock:
            if key in self._observers_by_key:
                self._observers_by_key[key] = [o for o in self._observers_by_key[key] if o is not obs]

    def notify(self, key: str, event: str, data: dict) -> None:
        with self._lock:
            observers = list(self._observers_by_key.get(key, []))
        for obs in observers:
            obs.update(event, data)


@dataclass
class SseObserver(Observer):
    """
    SSE “наблюдатель” пишет события в открытое HTTP соединение.
    writer: функция, которая делает handler.wfile.write(...)
    """
    writer: Callable[[bytes], None]
    on_close: Optional[Callable[[], None]] = None

    def update(self, event: str, data: dict) -> None:
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        msg = b"event: " + event.encode("utf-8") + b"\n" + b"data: " + payload + b"\n\n"
        try:
            self.writer(msg)
        except Exception:
            if self.on_close:
                self.on_close()
