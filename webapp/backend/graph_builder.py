from __future__ import annotations

from typing import Dict, Iterable

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, XSD

from .ontology import OntologyService
from .storage import BehaviorEntry


class UnknownPrefixError(ValueError):
    pass


def _expand_identifier(value: str, prefixes: Dict[str, str]) -> URIRef:
    if "://" in value:
        return URIRef(value)
    if ":" in value:
        prefix, local = value.split(":", 1)
        base = prefixes.get(prefix)
        if not base:
            raise UnknownPrefixError(f"Unknown prefix: {prefix}")
        return URIRef(base + local)
    raise UnknownPrefixError(f"Value '{value}' must be a CURIE or absolute IRI")


def build_behavior_graph(
    behaviors: Iterable[BehaviorEntry],
    prefixes: Dict[str, str],
    ontology: OntologyService,
) -> Graph:
    graph = Graph()
    for prefix, iri in prefixes.items():
        graph.bind(prefix, iri)
    graph.bind("rdf", str(RDF))
    graph.bind("xsd", str(XSD))

    for entry in behaviors:
        subject = _expand_identifier(entry.identifier, prefixes)
        behavior_class = _expand_identifier(entry.behavior_class, prefixes)
        graph.add((subject, RDF.type, behavior_class))

        graph.add((subject, _expand_identifier("mbo:hasStart", prefixes), Literal(entry.has_start, datatype=XSD.dateTime)))

        if entry.has_end:
            graph.add((subject, _expand_identifier("mbo:hasEnd", prefixes), Literal(entry.has_end, datatype=XSD.dateTime)))
        if entry.has_target:
            graph.add((subject, _expand_identifier("mbo:hasTarget", prefixes), _expand_identifier(entry.has_target, prefixes)))
        if entry.has_duration is not None:
            graph.add((subject, _expand_identifier("mbo:hasDuration", prefixes), Literal(entry.has_duration, datatype=XSD.decimal)))
        if entry.confidence is not None:
            graph.add((subject, _expand_identifier("mbo:confidence", prefixes), Literal(entry.confidence, datatype=XSD.decimal)))
        if entry.distance_to_target is not None:
            graph.add((subject, _expand_identifier("mbo:distanceToTarget", prefixes), Literal(entry.distance_to_target, datatype=XSD.decimal)))
        if entry.heading_to_target is not None:
            graph.add((subject, _expand_identifier("mbo:headingToTarget", prefixes), Literal(entry.heading_to_target, datatype=XSD.decimal)))
        if entry.performed_by:
            graph.add((subject, _expand_identifier("mbo:performedBy", prefixes), _expand_identifier(entry.performed_by, prefixes)))
        if entry.evidence:
            graph.add((subject, _expand_identifier("mbo:evidence", prefixes), Literal(entry.evidence)))

    # Carry over ontology prefixes for serialization convenience
    for alias, iri in ontology.list_prefixes().items():
        graph.bind(alias, iri)

    return graph
