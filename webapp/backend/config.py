from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
ONTOLOGY_DIR = BASE_DIR / "ontology"
SRC_DIR = BASE_DIR / "src"
VOCAB_DIR = BASE_DIR / "vocab"
SHAPES_DIR = BASE_DIR / "shapes"
EXAMPLES_DIR = BASE_DIR / "examples"
STATE_DIR = BASE_DIR / "webapp" / "state"

CORE_TTL = SRC_DIR / "mbo-core.ttl"
MEASURES_TTL = VOCAB_DIR / "mbo-measures.ttl"
GENERATED_TTL = BASE_DIR / "build" / "mbo-generated.ttl"
SHACL_PATH = SHAPES_DIR / "mbo-profile.shacl.ttl"

DEFAULT_PREFIXES = {
    "mbo": "http://purl.org/mapp/mbo#",
    "ex": "http://example.org/",
}

STATE_DIR.mkdir(parents=True, exist_ok=True)
WORKSPACE_PATH = STATE_DIR / "workspace.json"
EXPORT_DIR = BASE_DIR / "build"
EXPORT_DIR.mkdir(exist_ok=True)
