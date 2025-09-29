# Mouse Behavior Ontology (MBO)

MBO is an ontology for describing mouse behaviors with operational (lab) definitions and clear mappings to external standards. It focuses on observable actions and states (for example locomotion, rearing, sniffing) grounded in literature.

## What's here
- Core ontology: `src/mbo-core.ttl`
- Measures vocabulary (SKOS): `vocab/mbo-measures.ttl`
- SHACL shapes: `shapes/mbo-profile.shacl.ttl`
- CSV templates: `templates/`
- CSV + TTL generator: `generate_ttl.py`
- Examples: `examples/`
- Generated output: `build/mbo-generated.ttl`

## Why this matters
- Shared definitions enable comparable, interoperable datasets.
- SHACL shapes enforce consistent annotations (for example states have end time, events do not).
- SKOS mappings connect to NBO/GO/CMO when appropriate.

## Repository structure
```
src/                 core ontology (OWL plus some SKOS categories)
vocab/               SKOS vocabularies (measures)
shapes/              SHACL constraints
templates/           CSV templates for behaviors/measures
examples/            sample instance data
build/               generated TTL files (artifacts)
generate_ttl.py      CSV + TTL generator for behaviors
```

## Workflow
1. Define or edit behaviors in `templates/mbo-behaviors.csv`:
   - Behavior IRI, label
   - Parent types (for example `mbo:StateBehavior|mbo:PrimitiveBehavior`)
   - Definition, category, evidence
   - External xrefs (CURIEs such as `NBO:0000009|GO:0071965`)

2. Generate TTL
   - `python3 generate_ttl.py` (writes `build/mbo-generated.ttl`)

3. Validate with SHACL (recommended)
   - Install tools: `pip install rdflib pyshacl`
   - Validate examples against shapes and ontologies:
     - `pyshacl -s shapes/mbo-profile.shacl.ttl -m -f human -e src/mbo-core.ttl -e vocab/mbo-measures.ttl -e build/mbo-generated.ttl examples/mbo-newbehaviors.ttl`

Expected: `Conforms: True`. If not, the report explains violations (for example missing `mbo:hasEnd` for a state behavior).

## SKOS mapping guidance
- `skos:exactMatch`: only when IRIs are fully substitutable (rare across modeling layers).
- `skos:closeMatch`: near-equivalent meaning with different modeling scope.
  - Example: `mbo:Locomotion` closeMatch `NBO:0000009`, `GO:0071965`.
  - Example: `mbo:ExploratoryBehavior` closeMatch `GO:0035640`.
- `skos:relatedMatch`: helpful pointer across layers (for example measurement type vs feature term).
  - Example: `mbo:TimeMoving` relatedMatch `CMO:0000954`.

## Quality check summary
- CSV + TTL generation runs: `build/mbo-generated.ttl` is produced and syntactically tidy (no trailing semicolons).
- Ontology consistency: classes and properties referenced by shapes/examples are defined in `src/mbo-core.ttl`.
- Measures vocab: added `obo:` prefix and `skos:relatedMatch` to CMO where appropriate.
- Note: If you run pySHACL locally, use the command above to fully validate.

## Roadmap / suggestions
- Generator enhancements:
  - Add `MappingProperty` column per xref (for example `closeMatch`, `relatedMatch`) instead of defaulting to `closeMatch`.
  - Add a `templates/mbo-measures.csv` generator to produce a measures TTL (parallel to `vocab/mbo-measures.ttl`).
  - Escape and datatype handling (units): consider QUDT/OM for measures and add SHACL unit constraints.
- Ontology refinements:
  - Define supported/unsupported rearing explicitly (classes exist in core, can add to CSV when needed).
  - Consider `mbo:TransitionBehavior` if you later model transitions or bouts.
  - Introduce controlled individuals for experimental zones/objects to standardize `mbo:hasTarget`.
- Validation/automation:
  - Add a GitHub Actions workflow to run CSV + TTL generation, RDF parse (rdflib), SHACL validation (pySHACL), and diff on build artifacts.
  - Add a small `tests/` directory with sample graphs and expected SHACL conformance.
- Documentation:
  - Add a short "data modeling examples" section showing typical annotations for each primitive behavior.
  - Add license (suggested: CC-BY 4.0 for ontology; Apache-2.0 or MIT for code).

## Contributing
- Propose new behaviors/measures via CSVs; include PubMed/PMC evidence.
- Use SKOS mappings conservatively (`closeMatch` vs `relatedMatch` per guidance above).
- Open PRs with clear rationale and references.

## Web app: MBO behavior builder
- Install dependencies (one time): `python -m pip install -r webapp/requirements.txt`
- Run locally: `uvicorn webapp.backend.main:app --reload` and open `http://localhost:8000/app/`
- Features:
  - Browse ontology classes, including labels, comments, descriptions, and categories.
  - Capture behaviors through a guided form with prefix-aware fields.
  - Maintain custom prefixes for CURIE expansion.
  - Run SHACL validation (`shapes/mbo-profile.shacl.ttl`) against captured instances.
  - Export data to Turtle in-browser or write to `build/mbo-webapp-output.ttl` for downstream tooling.
- Data persistence: form entries and prefixes are stored in `webapp/state/workspace.json` (created on first save).
- Testing: `pytest tests/webapp/test_graph_builder.py`
- API surface (for scripting or integration):
  - `GET /api/behavior-classes` – ontology metadata
  - `GET/POST/PUT/DELETE /api/behaviors` – captured behaviors
  - `GET/POST/DELETE /api/prefixes` – prefix manager
  - `POST /api/validate` – SHACL validation report
  - `GET|POST /api/export` and `GET /api/export/file` – Turtle exports
