import importlib.util
import random
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location("stable_paging_flow", ROOT / "scripts" / "build-search-export-flow.py")
FLOW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FLOW)
EXPECTED = [{"Property": "[docid]", "Direction": 0}]


def request_actions(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key in ("Initial_request", "Next_request") and isinstance(child, dict) and child.get("type") == "Compose":
                yield key, child["inputs"]["request"]
            yield from request_actions(child)
    elif isinstance(value, list):
        for child in value:
            yield from request_actions(child)


class StablePagingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        template = (FLOW.TARGET / "RuntimeSearchResults.template.xlsx").read_bytes()
        cls.definition = FLOW.build_definition(FLOW.load_policy(), template)

    def test_initial_and_next_pages_have_identical_docid_only_sort(self):
        requests = dict(request_actions(self.definition))
        self.assertEqual(set(requests), {"Initial_request", "Next_request"})
        for request in requests.values():
            self.assertEqual(request["SortList"], EXPECTED)
        self.assertEqual(requests["Initial_request"]["StartRow"], 0)
        self.assertEqual(requests["Next_request"]["StartRow"], "@variables('PageStart')")

    def test_existing_query_locator_and_page_contract_is_preserved(self):
        for offset in (0, 100, 500, "@variables('PageStart')"):
            request = FLOW.search_request("item()?['Kql']", offset)["request"]
            self.assertEqual(request["RowLimit"], 100)
            self.assertEqual(request["StartRow"], offset)
            self.assertEqual(request["SelectProperties"], ["SPWebUrl", "SiteID", "ListID", "ListItemID"])
            self.assertFalse(request["TrimDuplicates"])
            self.assertFalse(request["EnableQueryRules"])
            self.assertIn("item()?['Kql']", request["Querytext"])
            self.assertIn("outputs('Literal_query')", request["Querytext"])
            self.assertIn("IsDocument:1 OR FileExtension:aspx", request["Querytext"])

    def test_512_tie_heavy_synthetic_rows_cover_every_docid_once(self):
        rng = random.Random(512)
        rows = [{"[docid]": i, "rank": 100, "collection": i % 10} for i in range(1, 513)]
        collected, sizes = [], []
        for start in range(0, len(rows), 100):
            shuffled = rows.copy()
            rng.shuffle(shuffled)
            request = FLOW.search_request("item()?['Kql']", start)["request"]
            for clause in reversed(request["SortList"]):
                shuffled.sort(key=lambda row: row[clause["Property"]], reverse=bool(clause["Direction"]))
            page = shuffled[request["StartRow"]:request["StartRow"] + request["RowLimit"]]
            collected.extend(row["[docid]"] for row in page)
            sizes.append(len(page))
        self.assertEqual(sizes, [100, 100, 100, 100, 100, 12])
        self.assertEqual(collected, list(range(1, 513)))
        self.assertEqual(len(set(collected)), 512)

    def test_rank_changes_do_not_change_document_id_paging_order(self):
        rng = random.Random(400)
        rows = [{"[docid]": i, "rank": rng.random()} for i in range(1, 401)]
        collected = []
        for start in range(0, len(rows), 100):
            for row in rows:
                row["rank"] = rng.random()
            rng.shuffle(rows)
            request = FLOW.search_request("item()?['Kql']", start)["request"]
            ordered = rows.copy()
            for clause in reversed(request["SortList"]):
                ordered.sort(key=lambda row: row[clause["Property"]], reverse=bool(clause["Direction"]))
            collected.extend(row["[docid]"] for row in ordered[start:start + 100])
        self.assertEqual(collected, list(range(1, 401)))

    def test_request_sort_arrays_are_not_shared_mutable_state(self):
        first = FLOW.search_request("item()?['Kql']", 0)["request"]
        first["SortList"][0]["Direction"] = 1
        self.assertEqual(FLOW.search_request("item()?['Kql']", 100)["request"]["SortList"], EXPECTED)


if __name__ == "__main__":
    unittest.main()
