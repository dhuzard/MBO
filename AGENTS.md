# Agent guidance — Mouse Behavior Ontology (MBO)

## Status
**Early, preliminary draft; development is currently paused (October 2026).** This repository is not an endorsed, stable or production-qualified behavioral ontology. Do not infer scientific validity, consensus, or conformance from the existence of RDF/SHACL files or examples.

## Scientific ownership
Scope: operational descriptions of mouse behavior and measurement vocabulary. This is not a replacement for the Home Cage Monitoring Ontology (HCMO), NBO, GO, CMO or other external vocabularies. Proposed crosswalks are hypotheses until justified; only use `skos:exactMatch` for fully substitutable concepts. Keep evidence, definitions, behavioral granularity and measurement meaning explicit.

## Repository layout
- `ontology/mbo.yaml`: generator inputs.
- `generate_ttl.py`: CSV/YAML-to-RDF generation.
- `src/mbo-core.ttl`, `vocab/mbo-measures.ttl`, `shapes/mbo-profile.shacl.ttl`: RDF vocabulary and validation artifacts.
- `templates/`, `examples/`, `build/`: proposed source tables, fixtures and generated outputs.

## Change policy
Default to read-only review and documentation. Do not silently activate or expand the ontology. Before implementing a new term, require an operational definition, behavior/event/state distinction, references, scope and evidence for proposed external mappings. Record uncertainties instead of inventing alignments. Do not declare a stable release without scientific review and reproducible checks. Avoid modifying generated output without the corresponding source change.

## Checks (when development resumes)
```bash
python -m pip install PyYAML rdflib pyshacl
python3 generate_ttl.py
pyshacl -s shapes/mbo-profile.shacl.ttl -m -f human -e src/mbo-core.ttl -e vocab/mbo-measures.ttl -e build/mbo-generated.ttl examples/mbo-newbehaviors.ttl
```
These are structural examples, not proof of semantic accuracy. No automated CI qualification is implied.
