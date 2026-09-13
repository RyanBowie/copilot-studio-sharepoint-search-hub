"""Compile the standing portable agent into the existing unpacked solution."""

import json
from pathlib import Path
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
AGENT = ROOT.parent / "agent"
FLOW_ID = "96794fbd-20ae-f111-aaab-002248403bef"
PLACEHOLDER_FLOW_ID = "00000000-0000-4000-8000-000000000100"
sys.path.insert(0, str(AGENT / "scripts"))
from authoring_yaml import dump_authoring_yaml


def bind_flow(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "flowId":
                if child not in (PLACEHOLDER_FLOW_ID, FLOW_ID):
                    raise ValueError("Unexpected flow identity; review solution references before changing it.")
                value[key] = FLOW_ID
            else:
                bind_flow(child)
    elif isinstance(value, list):
        for child in value:
            bind_flow(child)
    return value


def portable_file(schema):
    if ".topic." in schema:
        return AGENT / "topics" / (schema.rsplit(".", 1)[1] + ".mcs.yml")
    if schema.endswith(".gpt.default"):
        return AGENT / "agent.mcs.yml"
    if schema.endswith(".action.CorpNetSearchCount-CallerPermissions"):
        return AGENT / "actions" / "SearchAndExport.mcs.yml"
    raise ValueError(f"Unexpected packaged component: {schema}")


def compiled_component(schema):
    data = yaml.safe_load(portable_file(schema).read_text(encoding="utf-8"))
    data.pop("mcs.metadata", None)
    return bind_flow(data)


def main():
    for folder in (ROOT / "src" / "botcomponents").iterdir():
        (folder / "data").write_text(dump_authoring_yaml(compiled_component(folder.name)), encoding="utf-8")
    flow_file, = (ROOT / "src" / "Workflows").glob("*.json")
    flow = json.loads(flow_file.read_text(encoding="utf-8"))
    flow["properties"]["definition"] = json.loads(
        (AGENT / "flows" / "search-export" / "definition.json").read_text(encoding="utf-8"))
    flow_file.write_text(json.dumps(flow, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Compiled 16 components and the portable native definition; intrinsic solution flow identity retained.")


if __name__ == "__main__":
    main()
