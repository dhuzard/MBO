Here’s a **comprehensive README.md** you can drop into the root of your repo.
It explains *what MBO is*, *why ontologies matter*, the *repo structure*, and how to *use/validate/extend it*.

---

```markdown
# 🐭 Mouse Behavior Ontology (MBO)

**MBO** is an open ontology for describing mouse behaviors in preclinical and neuroscience research.  
It is designed to capture **observable actions** (e.g. locomotion, rearing, sniffing) in a **machine-readable, interoperable** way, with traceable definitions from experimental literature.

This repository provides:

- A **core ontology** (`src/mbo-core.ttl`) defining the backbone concepts (behaviors, states, events, transitions, metrics).
- **Vocabulary files** (`vocab/`) for categories, measures, and SKOS groupings.
- **SHACL profiles** (`shapes/`) that specify **validation rules** (e.g. state behaviors need start+end times, events should not have end times).
- **CSV templates** (`templates/`) so you can **add new behaviors or measures** without writing RDF manually.
- A **generator script** (`generate_ttl.py`) to turn CSVs into proper RDF/OWL.
- **Examples** (`examples/`) to test behaviors and validation.
- **Build artifacts** (`build/`) with generated TTLs.

---

## 🌱 Why Ontologies?

In behavioral neuroscience, the same behavior can be described in many ways:
- “rearing”, “vertical exploration”, “standing on hindlimbs”…  
- or measured differently: counts, duration, supported vs unsupported.

An ontology:
- Provides **shared definitions** with clear semantics.  
- Links to **external standards** (GO, NBO, CMO, etc.) where possible.  
- Makes data **interoperable**: your “rearing” is the same as mine if both point to `mbo:Rearing`.  
- Supports **validation**: SHACL ensures your data instances conform to definitions.

---

## 📂 Folder Structure

```

MBO/
├─ src/                # Core ontology files
│   └─ mbo-core.ttl
├─ vocab/              # Controlled vocabularies (SKOS)
│   ├─ mbo-behaviors.ttl
│   └─ mbo-measures.ttl
├─ shapes/             # SHACL validation shapes
│   └─ mbo-profile.shacl.ttl
├─ templates/          # CSV templates for generating ontology content
│   └─ mbo-behaviors.csv
├─ build/              # Auto-generated TTL files (from CSVs)
│   └─ mbo-generated.ttl
├─ examples/           # Example data instances
│   └─ mbo-newbehaviors.ttl
├─ generate\_ttl.py     # CSV → TTL generator script
└─ README.md

````

---

## ⚙️ Workflow

1. **Define new behaviors in CSV**  
   Edit `templates/mbo-behaviors.csv` and add rows with:
   - IRI (`mbo:Approach`),  
   - label,  
   - parent types (StateBehavior/EventBehavior, Primitive/Composite),  
   - definition, category, evidence, external xrefs.

2. **Generate TTL**  
   Run the script:

   ```powershell
   python generate_ttl.py
````

→ Creates/updates `build/mbo-generated.ttl`.

3. **Validate with SHACL**
   Test your ontology + vocab + instances:

   ```powershell
   pyshacl -s shapes/mbo-profile.shacl.ttl -m -f human -e src/mbo-core.ttl -e vocab/mbo-behaviors.ttl -e vocab/mbo-measures.ttl -e build/mbo-generated.ttl examples/mbo-newbehaviors.ttl
   ```

   Expected output:

   ```
   Validation Report
   Conforms: True
   ```

   If `Conforms: False`, SHACL will print the violations (e.g., missing `hasEnd` for a state behavior).

---

## 🧩 Components Explained

* **Core ontology (`src/mbo-core.ttl`)**
  The backbone: defines `mbo:Behavior`, `mbo:StateBehavior`, `mbo:EventBehavior`, properties like `mbo:hasStart`, `mbo:hasEnd`, `mbo:performedBy`.

* **Vocabularies (`vocab/`)**
  SKOS lists of categories and measures, e.g.:

  * `mbo:Cat_Exploratory` (Exploratory category).
  * `mbo:TotalDistance`, `mbo:RearingCount`, `mbo:PathCircuity` (common measures).

* **Shapes (`shapes/`)**
  SHACL constraints ensure data consistency. Examples:

  * `StateBehavior` must have an `mbo:hasEnd`.
  * `EventBehavior` must **not** have an end.
  * `Approach` and `Avoidance` must reference a `mbo:hasTarget`.

* **Templates (`templates/`)**
  CSVs you can edit in Excel/Google Sheets. The generator script will turn them into TTL.

* **Build (`build/`)**
  Output of the generator. Treated as artifacts—don’t edit by hand.

* **Examples (`examples/`)**
  Ready-to-validate Turtle data with sample behaviors (Approach, Avoidance, Orienting, etc.).

---

## 🔎 Results

* **Reusable ontology**: behavior terms with operational definitions, grounded in PubMed evidence.
* **Validation**: pySHACL confirms whether behavior data files match the ontology rules.
* **Interoperability**: SKOS mappings link to existing ontologies (e.g., NBO, GO, CMO).
* **Extensibility**: add new behaviors/measures in CSV, regenerate, validate—no RDF knowledge required.

---

## 🏃 Quickstart

```powershell
# Setup
python -m venv .venv
.venv\Scripts\activate
pip install pyshacl rdflib

# Generate TTL from CSV
python generate_ttl.py

# Validate example
pyshacl -s shapes/mbo-profile.shacl.ttl -m -f human `
  -e src/mbo-core.ttl `
  -e vocab/mbo-behaviors.ttl `
  -e vocab/mbo-measures.ttl `
  -e build/mbo-generated.ttl `
  examples/mbo-newbehaviors.ttl
```

---

## 📚 Learn More

* [SKOS Primer (W3C)](https://www.w3.org/TR/skos-primer/) — controlled vocabularies.
* [SHACL Primer (W3C)](https://www.w3.org/TR/shacl/) — validation of RDF data.
* [pySHACL docs](https://github.com/RDFLib/pySHACL) — Python SHACL validator.
* [OBO Foundry](http://obofoundry.org/) — ecosystem of biomedical ontologies.

---

## 🤝 Contributions

* Add behaviors via `templates/mbo-behaviors.csv`.
* Provide PubMed/PMC evidence where possible (`Evidence` column).
* Use `skos:closeMatch` or `skos:relatedMatch` for external ontology mappings (avoid `exactMatch` unless truly identical).
* Open pull requests with new terms, categories, or measures.

---

## 📜 License

TBD — consider **CC-BY 4.0** for ontology terms and code.


