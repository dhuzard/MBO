import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest
from rdflib import Literal, URIRef
from rdflib.namespace import RDF, XSD

from webapp.backend.config import DEFAULT_PREFIXES
from webapp.backend.graph_builder import UnknownPrefixError, build_behavior_graph
from webapp.backend.ontology import OntologyService
from webapp.backend.storage import BehaviorEntry
from webapp.backend.validation import run_shacl_validation


@pytest.fixture(scope="module")
def ontology():
    return OntologyService()


def test_build_behavior_graph_contains_expected_triples(ontology):
    entry = BehaviorEntry(
        uid="test",
        identifier="ex:approach1",
        behavior_class="mbo:Approach",
        performed_by="ex:mouseA",
        has_start="2025-09-23T14:05:00Z",
        has_end="2025-09-23T14:05:02Z",
        has_target="ex:novelObject1",
        has_duration=2.0,
        confidence=0.9,
        distance_to_target=12.3,
        heading_to_target=5.0,
        evidence="Example evidence",
    )

    graph = build_behavior_graph([entry], DEFAULT_PREFIXES, ontology)

    subject = URIRef(DEFAULT_PREFIXES["ex"] + "approach1")
    approach = URIRef(DEFAULT_PREFIXES["mbo"] + "Approach")

    assert (subject, RDF.type, approach) in graph
    assert (
        subject,
        URIRef(DEFAULT_PREFIXES["mbo"] + "hasStart"),
        Literal("2025-09-23T14:05:00Z", datatype=XSD.dateTime),
    ) in graph
    assert (
        subject,
        URIRef(DEFAULT_PREFIXES["mbo"] + "hasTarget"),
        URIRef(DEFAULT_PREFIXES["ex"] + "novelObject1"),
    ) in graph


def test_build_behavior_graph_unknown_prefix_raises(ontology):
    entry = BehaviorEntry(
        uid="test",
        identifier="badprefix:item",
        behavior_class="mbo:Approach",
        performed_by="ex:mouseA",
        has_start="2025-01-01T00:00:00Z",
    )
    with pytest.raises(UnknownPrefixError):
        build_behavior_graph([entry], DEFAULT_PREFIXES, ontology)


def test_run_shacl_validation_conforms(ontology):
    entry = BehaviorEntry(
        uid="test",
        identifier="ex:approach2",
        behavior_class="mbo:Approach",
        performed_by="ex:mouseB",
        has_start="2025-09-23T14:05:00Z",
        has_end="2025-09-23T14:05:02Z",
        has_target="ex:novelObject1",
    )

    conforms, report = run_shacl_validation([entry], DEFAULT_PREFIXES, ontology)
    assert conforms, report
