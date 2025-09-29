from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .config import DEFAULT_PREFIXES, WORKSPACE_PATH


@dataclass
class BehaviorEntry:
    uid: str
    identifier: str
    behavior_class: str
    performed_by: str
    has_start: str
    has_end: Optional[str] = None
    has_target: Optional[str] = None
    has_duration: Optional[float] = None
    confidence: Optional[float] = None
    distance_to_target: Optional[float] = None
    heading_to_target: Optional[float] = None
    evidence: Optional[str] = None


class WorkspaceStorage:
    """Persists user-created behavior instances for the web app."""

    def __init__(self, path: Path = WORKSPACE_PATH) -> None:
        self.path = path
        self.prefixes: Dict[str, str] = dict(DEFAULT_PREFIXES)
        self.behaviors: List[BehaviorEntry] = []
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.prefixes.update(data.get("prefixes", {}))
        behaviors = data.get("behaviors", [])
        self.behaviors = [BehaviorEntry(**item) for item in behaviors]

    def _save(self) -> None:
        payload = {
            "prefixes": self.prefixes,
            "behaviors": [asdict(entry) for entry in self.behaviors],
        }
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def list_behaviors(self) -> List[BehaviorEntry]:
        return list(self.behaviors)

    def get_behavior(self, uid: str) -> Optional[BehaviorEntry]:
        return next((entry for entry in self.behaviors if entry.uid == uid), None)

    def upsert_behavior(
        self,
        *,
        uid: Optional[str],
        identifier: str,
        behavior_class: str,
        performed_by: str,
        has_start: str,
        has_end: Optional[str] = None,
        has_target: Optional[str] = None,
        has_duration: Optional[float] = None,
        confidence: Optional[float] = None,
        distance_to_target: Optional[float] = None,
        heading_to_target: Optional[float] = None,
        evidence: Optional[str] = None,
    ) -> BehaviorEntry:
        if uid:
            entry = self.get_behavior(uid)
            if not entry:
                raise KeyError(f"Behavior uid not found: {uid}")
            entry.identifier = identifier
            entry.behavior_class = behavior_class
            entry.performed_by = performed_by
            entry.has_start = has_start
            entry.has_end = has_end
            entry.has_target = has_target
            entry.has_duration = has_duration
            entry.confidence = confidence
            entry.distance_to_target = distance_to_target
            entry.heading_to_target = heading_to_target
            entry.evidence = evidence
        else:
            entry = BehaviorEntry(
                uid=str(uuid.uuid4()),
                identifier=identifier,
                behavior_class=behavior_class,
                performed_by=performed_by,
                has_start=has_start,
                has_end=has_end,
                has_target=has_target,
                has_duration=has_duration,
                confidence=confidence,
                distance_to_target=distance_to_target,
                heading_to_target=heading_to_target,
                evidence=evidence,
            )
            self.behaviors.append(entry)
        self._save()
        return entry

    def delete_behavior(self, uid: str) -> None:
        original_len = len(self.behaviors)
        self.behaviors = [entry for entry in self.behaviors if entry.uid != uid]
        if len(self.behaviors) == original_len:
            raise KeyError(f"Behavior uid not found: {uid}")
        self._save()

    def set_prefix(self, prefix: str, iri: str) -> None:
        if not prefix:
            raise ValueError("Prefix cannot be empty")
        if ":" in prefix:
            raise ValueError("Prefix must not contain colon")
        if not iri:
            raise ValueError("IRI cannot be empty")
        self.prefixes[prefix] = iri
        self._save()

    def remove_prefix(self, prefix: str) -> None:
        if prefix in DEFAULT_PREFIXES:
            raise ValueError("Cannot remove default prefix")
        if prefix not in self.prefixes:
            raise ValueError("Prefix not defined")
        self.prefixes.pop(prefix, None)
        self._save()
