from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS

from .config import CORE_TTL, MEASURES_TTL, GENERATED_TTL, DEFAULT_PREFIXES


@dataclass
class BehaviorClass:
    iri: str
    label: Optional[str]
    comment: Optional[str]
    description: Optional[str]
    parents: List[str]
    category: Optional[str]


class OntologyService:
    """Utility to expose ontology metadata to the web application."""

    def __init__(self) -> None:
        self.graph = Graph()
        for path in (CORE_TTL, MEASURES_TTL, GENERATED_TTL):
            if path.exists():
                self.graph.parse(path)
        for prefix, iri in DEFAULT_PREFIXES.items():
            self.graph.bind(prefix, iri)
        self.mbo = Namespace(DEFAULT_PREFIXES["mbo"])

    def _literal(self, subject: URIRef, predicate: URIRef) -> Optional[str]:
        for literal in self.graph.objects(subject, predicate):
            if literal.language in (None, "", "en"):
                return str(literal)
        return None

    def _is_behavior_class(self, class_ref: URIRef) -> bool:
        if class_ref == self.mbo.Behavior:
            return True
        for parent in self.graph.transitive_objects(class_ref, RDFS.subClassOf):
            if parent == self.mbo.Behavior:
                return True
        return False

    def _parents(self, class_ref: URIRef) -> List[str]:
        return [str(parent) for parent in self.graph.objects(class_ref, RDFS.subClassOf)]

    def _category(self, class_ref: URIRef) -> Optional[str]:
        for category in self.graph.objects(class_ref, SKOS.broader):
            return str(category)
        return None

    def list_behavior_classes(self) -> List[BehaviorClass]:
        classes: List[BehaviorClass] = []
        for class_ref in set(self.graph.subjects(RDF.type, OWL.Class)):
            if not isinstance(class_ref, URIRef):
                continue
            if not self._is_behavior_class(class_ref):
                continue
            classes.append(
                BehaviorClass(
                    iri=str(class_ref),
                    label=self._literal(class_ref, RDFS.label),
                    comment=self._literal(class_ref, RDFS.comment),
                    description=self._literal(class_ref, DCTERMS.description),
                    parents=self._parents(class_ref),
                    category=self._category(class_ref),
                )
            )
        classes.sort(key=lambda item: item.label or item.iri)
        return classes

    def get_behavior_class(self, iri: str) -> Optional[BehaviorClass]:
        class_ref = URIRef(iri)
        if (class_ref, RDF.type, OWL.Class) not in self.graph:
            return None
        if not self._is_behavior_class(class_ref):
            return None
        return BehaviorClass(
            iri=str(class_ref),
            label=self._literal(class_ref, RDFS.label),
            comment=self._literal(class_ref, RDFS.comment),
            description=self._literal(class_ref, DCTERMS.description),
            parents=self._parents(class_ref),
            category=self._category(class_ref),
        )

    def list_prefixes(self) -> Dict[str, str]:
        prefixes: Dict[str, str] = {}
        for prefix, iri in self.graph.namespace_manager.namespaces():
            prefixes[prefix] = str(iri)
        return prefixes
