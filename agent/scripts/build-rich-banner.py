"""Rebuild only the contextual topic banner and an explicitly fictional example."""

import json
from pathlib import Path
import yaml

from authoring_yaml import dump_authoring_yaml
from banner_cards import NODE_ID, banner_node, card


ROOT = Path(__file__).resolve().parents[1]


def main():
    path = ROOT / "topics" / "SearchSharePoint.mcs.yml"
    topic = yaml.safe_load(path.read_text(encoding="utf-8"))
    actions = topic["beginDialog"]["actions"]
    prior = [node for node in actions if node.get("id") != NODE_ID]
    index = next(i for i, node in enumerate(prior) if node.get("id") == "reportCount")
    if prior[index - 1].get("id") != "checkSearchResult":
        raise ValueError("The contextual banner must immediately precede the guarded native result message.")
    topic["beginDialog"]["actions"] = prior[:index] + [banner_node()] + prior[index:]
    path.write_text(dump_authoring_yaml(topic), encoding="utf-8")
    examples = ROOT / "cards" / "examples"
    examples.mkdir(exist_ok=True)
    (examples / "HR.card.json").write_text(json.dumps(card("HR"), indent=2) + "\n", encoding="utf-8")
    print("Rebuilt contextual HR example and topic banner only. No flow, workbook or cloud changes.")


if __name__ == "__main__":
    main()
