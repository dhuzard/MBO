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

with csv_path.open(newline='', encoding="utf-8") as f, out_path.open("w", encoding="utf-8") as out:
    reader = csv.DictReader(f)
    out.write(prefixes)
    out.write("# Auto-generated from {}\n\n".format(csv_path.name))

    for row in reader:
        iri = row["Behavior IRI"].strip()
        label = row["Label"].strip()
        parents = [p.strip() for p in row["Parent Types (|)"].split("|") if p.strip()]
        definition = row["Definition"].strip()
        category = row["Category"].strip()
        evidence = row["Evidence (PMIDs/PMCIDs)"].strip()
        xrefs = [x.strip() for x in row["External xref (CURIEs)"].split("|") if row["External xref (CURIEs)"].strip()]

        out.write(f"{iri} a owl:Class ;\n")
        out.write(f'  rdfs:label "{label}"@en ;\n')

        for parent in parents:
            out.write(f"  rdfs:subClassOf {parent} ;\n")

        if definition:
            out.write(f'  dct:description "{definition}"@en ;\n')

        if category:
            out.write(f"  skos:broader mbo:{category} ;\n")

        if evidence:
            out.write(f'  dct:source "{evidence}" ;\n')

        for x in xrefs:
            # Expand CURIEs like NBO:0000009 → http://purl.obolibrary.org/obo/NBO_0000009
            if ":" in x:
                prefix, local = x.split(":", 1)
                url = f"http://purl.obolibrary.org/obo/{prefix}_{local}"
                out.write(f"  skos:closeMatch <{url}> ;\n")

        out.write("  .\n\n")

print(f"✅ Wrote {out_path}")
