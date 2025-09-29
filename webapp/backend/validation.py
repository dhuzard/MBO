from __future__ import annotations

from typing import Dict, Iterable, Tuple

from rdflib import Graph
from pyshacl import validate

from .config import SHACL_PATH
from .graph_builder import build_behavior_graph
from .ontology import OntologyService
from .storage import BehaviorEntry


def run_shacl_validation(
    behaviors: Iterable[BehaviorEntry],
    prefixes: Dict[str, str],
    ontology: OntologyService,
) -> Tuple[bool, str]:
    data_graph = build_behavior_graph(behaviors, prefixes, ontology)
    shapes_graph = Graph()
    shapes_graph.parse(SHACL_PATH)

    conforms, _results_graph, results_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        ont_graph=ontology.graph,
        inference="rdfs",
        allow_infos=True,
        allow_warnings=True,
    )
    return bool(conforms), str(results_text)
