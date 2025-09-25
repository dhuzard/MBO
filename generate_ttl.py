import argparse
from collections import OrderedDict
from pathlib import Path
from typing import Iterable, List, Optional

import yaml

YAML_PATH = Path("ontology/mbo.yaml")
CORE_OUT = Path("src/mbo-core.ttl")
MEASURES_OUT = Path("vocab/mbo-measures.ttl")
SHAPES_OUT = Path("shapes/mbo-profile.shacl.ttl")


def escape_literal(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def quote_literal(text: str, lang: Optional[str] = None) -> str:
    if lang:
        return f'"{escape_literal(text)}"@{lang}'
    return f'"{escape_literal(text)}"'


def format_resource(value: str) -> str:
    if value.startswith("http://") or value.startswith("https://"):
        return f"<{value}>"
    return value


def format_prefixes(prefixes: dict, selected: Optional[Iterable[str]] = None) -> List[str]:
    keys = list(selected) if selected else list(prefixes.keys())
    return [f"@prefix {key}: <{prefixes[key]}> ." for key in keys]


def format_triples(subject: str, triples: List[str]) -> str:
    body = " ;\n  ".join(triples)
    return f"{subject} {body} ."


def build_metadata_block(metadata: dict) -> str:
    triples = ["a owl:Ontology"]
    if label := metadata.get("label"):
        triples.append(f"rdfs:label {quote_literal(label, 'en')}")
    if comment := metadata.get("comment"):
        triples.append(f"rdfs:comment {quote_literal(comment, 'en')}")
    if version_iri := metadata.get("version_iri"):
        triples.append(f"owl:versionIRI <{version_iri}>")
    return format_triples(f"<{metadata['ontology_iri']}>", triples)


def build_concept_scheme(scheme: dict) -> List[str]:
    lines = []
    triples = ["a skos:ConceptScheme"]
    if label := scheme.get("label"):
        triples.append(f"skos:prefLabel {quote_literal(label, 'en')}")
    lines.append(format_triples(scheme["id"], triples))
    lines.append("")
    for concept in scheme.get("concepts", []):
        c_triples = ["a skos:Concept", f"skos:inScheme {scheme['id']}"]
        if concept.get("pref_label"):
            c_triples.append(f"skos:prefLabel {quote_literal(concept['pref_label'], 'en')}")
        if concept.get("related_match"):
            c_triples.append(f"skos:relatedMatch {format_resource(concept['related_match'])}")
        if concept.get("close_matches"):
            for match in concept["close_matches"]:
                c_triples.append(f"skos:closeMatch {format_resource(match)}")
        for note in concept.get("notes", []):
            c_triples.append(f"skos:note {quote_literal(note, 'en')}")
        lines.append(format_triples(concept["id"], c_triples))
        lines.append("")
    return lines


def build_class_block(entry: dict) -> str:
    triples: List[str] = ["a owl:Class"]
    if parents := entry.get("parents", []):
        for parent in parents:
            triples.append(f"rdfs:subClassOf {format_resource(parent)}")
    if label := entry.get("label"):
        triples.append(f"rdfs:label {quote_literal(label, 'en')}")
    if comment := entry.get("comment"):
        triples.append(f"rdfs:comment {quote_literal(comment, 'en')}")
    if description := entry.get("description"):
        triples.append(f"dct:description {quote_literal(description, 'en')}")
    if category := entry.get("category"):
        triples.append(f"skos:broader {format_resource(category)}")
    if parts := entry.get("has_parts", []):
        for part in parts:
            triples.append(f"mbo:hasPart {format_resource(part)}")
    if close_matches := entry.get("close_matches", []):
        for match in close_matches:
            triples.append(f"skos:closeMatch {format_resource(match)}")
    if sources := entry.get("sources", []):
        for source in sources:
            triples.append(f"dct:source {quote_literal(source)}")
    return format_triples(entry["id"], triples)


def build_object_property(entry: dict) -> str:
    triples: List[str] = ["a owl:ObjectProperty"]
    if domain := entry.get("domain"):
        triples.append(f"rdfs:domain {format_resource(domain)}")
    if range_ := entry.get("range"):
        triples.append(f"rdfs:range {format_resource(range_)}")
    if label := entry.get("label"):
        triples.append(f"rdfs:label {quote_literal(label, 'en')}")
    if description := entry.get("description"):
        triples.append(f"dct:description {quote_literal(description, 'en')}")
    return format_triples(entry["id"], triples)


def build_datatype_property(entry: dict) -> str:
    triples: List[str] = ["a owl:DatatypeProperty"]
    if domain := entry.get("domain"):
        triples.append(f"rdfs:domain {format_resource(domain)}")
    if range_ := entry.get("range"):
        triples.append(f"rdfs:range {format_resource(range_)}")
    if label := entry.get("label"):
        triples.append(f"rdfs:label {quote_literal(label, 'en')}")
    if comment := entry.get("comment"):
        triples.append(f"rdfs:comment {quote_literal(comment, 'en')}")
    return format_triples(entry["id"], triples)


def build_shape(entry: dict) -> str:
    triples: List[str] = ["a sh:NodeShape", f"sh:targetClass {format_resource(entry['target_class'])}"]
    for prop in entry.get("property_shapes", []):
        parts = [f"sh:path {format_resource(prop['path'])}"]
        if "datatype" in prop:
            parts.append(f"sh:datatype {format_resource(prop['datatype'])}")
        if "min_count" in prop:
            parts.append(f"sh:minCount {prop['min_count']}")
        if "max_count" in prop:
            parts.append(f"sh:maxCount {prop['max_count']}")
        if "message" in prop:
            parts.append(f"sh:message {quote_literal(prop['message'])}")
        block = "[ " + " ; ".join(parts) + " ]"
        triples.append(f"sh:property {block}")
    return format_triples(entry["id"], triples)


def build_core_ttl(data: dict) -> str:
    prefixes = format_prefixes(data["prefixes"])
    lines: List[str] = prefixes + ["", f"# Auto-generated from {YAML_PATH.as_posix()}", "", build_metadata_block(data["metadata"]), ""]

    core_schemes = [scheme for scheme in data.get("concept_schemes", []) if scheme.get("scope") == "core"]
    for scheme in core_schemes:
        lines.extend(build_concept_scheme(scheme))

    classes = data.get("classes", [])
    sections = OrderedDict()
    for entry in classes:
        section = entry.get("section", "")
        sections.setdefault(section, []).append(entry)

    for section, entries in sections.items():
        if section:
            lines.append(f"# {section.title()}")
        for entry in entries:
            lines.append(build_class_block(entry))
            lines.append("")

    if object_properties := data.get("object_properties", []):
        lines.append("# Object properties")
        for entry in object_properties:
            lines.append(build_object_property(entry))
            lines.append("")

    if datatype_properties := data.get("datatype_properties", []):
        lines.append("# Datatype properties")
        for entry in datatype_properties:
            lines.append(build_datatype_property(entry))
            lines.append("")

    return "\n".join(line for line in lines if line is not None)


def build_measures_ttl(data: dict) -> str:
    prefixes = data["prefixes"]
    selected = [key for key in ("mbo", "skos", "obo") if key in prefixes]
    lines: List[str] = format_prefixes(prefixes, selected)
    lines.append("")
    lines.append(f"# Auto-generated from {YAML_PATH.as_posix()}")
    lines.append("")

    measure_schemes = [scheme for scheme in data.get("concept_schemes", []) if scheme.get("scope") == "measures"]
    for scheme in measure_schemes:
        lines.extend(build_concept_scheme(scheme))

    return "\n".join(line for line in lines if line is not None)


def build_shapes_ttl(data: dict) -> str:
    prefixes = data["prefixes"]
    selected = [key for key in ("sh", "mbo", "xsd") if key in prefixes]
    lines: List[str] = format_prefixes(prefixes, selected)
    lines.append("")
    lines.append(f"# Auto-generated from {YAML_PATH.as_posix()}")
    lines.append("")

    for shape in data.get("shapes", []):
        lines.append(build_shape(shape))
        lines.append("")

    return "\n".join(line for line in lines if line is not None)


def main(path: Path = YAML_PATH) -> None:
    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    CORE_OUT.write_text(build_core_ttl(data) + "\n", encoding="utf-8")
    MEASURES_OUT.write_text(build_measures_ttl(data) + "\n", encoding="utf-8")
    SHAPES_OUT.write_text(build_shapes_ttl(data) + "\n", encoding="utf-8")
    print(f"Wrote {CORE_OUT}, {MEASURES_OUT}, and {SHAPES_OUT}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate TTL artifacts from ontology YAML definition.")
    parser.add_argument("--source", type=Path, default=YAML_PATH, help="Path to ontology YAML definition.")
    args = parser.parse_args()
    main(args.source)
