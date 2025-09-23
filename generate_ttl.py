import csv
from pathlib import Path

# Paths
csv_path = Path("templates/mbo-behaviors.csv")
out_path = Path("build/mbo-generated.ttl")
out_path.parent.mkdir(exist_ok=True)

prefixes = """@prefix mbo:   <http://purl.org/mapp/mbo#> .
@prefix skos:  <http://www.w3.org/2004/02/skos/core#> .
@prefix dct:   <http://purl.org/dc/terms/> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:   <http://www.w3.org/2002/07/owl#> .

"""

def esc(s: str) -> str:
    return s.replace('"', '\\"')

with csv_path.open(newline='', encoding="utf-8") as f, out_path.open("w", encoding="utf-8") as out:
    reader = csv.DictReader(f)
    out.write(prefixes)
    out.write("# Auto-generated from {}\n\n".format(csv_path.name))

    for row in reader:
        iri = row["Behavior IRI"].strip()
        if not iri:
            continue
        label = row["Label"].strip()
        parents = [p.strip() for p in row["Parent Types (|)"].split("|") if p.strip()]
        definition = row["Definition"].strip()
        category = row["Category"].strip()
        evidence = row["Evidence (PMIDs/PMCIDs)"].strip()
        xrefs = [x.strip() for x in row["External xref (CURIEs)"].split("|") if row["External xref (CURIEs)"].strip()]

        po_list = []
        po_list.append('a owl:Class')
        if label:
            po_list.append(f'rdfs:label "{esc(label)}"@en')
        for parent in parents:
            po_list.append(f"rdfs:subClassOf {parent}")
        if definition:
            po_list.append(f'dct:description "{esc(definition)}"@en')
        if category:
            po_list.append(f"skos:broader mbo:{category}")
        if evidence:
            po_list.append(f'dct:source "{esc(evidence)}"')
        for x in xrefs:
            if ":" in x:
                prefix, local = x.split(":", 1)
                url = f"http://purl.obolibrary.org/obo/{prefix}_{local}"
                po_list.append(f"skos:closeMatch <{url}>")

        out.write(f"{iri} ")
        out.write(" ;\n  ".join(po_list))
        out.write(" .\n\n")

print(f"✅ Wrote {out_path}")
