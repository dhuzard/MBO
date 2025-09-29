from __future__ import annotations

from pathlib import Path

from .config import EXPORT_DIR
from .graph_builder import build_behavior_graph
from .ontology import OntologyService
from .storage import BehaviorEntry


EXPORT_FILENAME = "mbo-webapp-output.ttl"


def export_ttl(behaviors, prefixes, ontology: OntologyService) -> str:
    graph = build_behavior_graph(behaviors, prefixes, ontology)
    return graph.serialize(format="turtle")


def export_to_file(behaviors, prefixes, ontology: OntologyService, path: Path | None = None) -> Path:
    ttl = export_ttl(behaviors, prefixes, ontology)
    destination = path or (EXPORT_DIR / EXPORT_FILENAME)
    destination.write_text(ttl, encoding="utf-8")
    return destination
