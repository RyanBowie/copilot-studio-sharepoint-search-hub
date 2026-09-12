from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]


def load(*parts):
    return yaml.safe_load(ROOT.joinpath(*parts).read_text(encoding="utf-8-sig"))


class SystemTopicSafetyTests(unittest.TestCase):
    def test_generic_fallback_fails_without_retry_or_escalation(self):
        dialog = load("topics", "Fallback.mcs.yml")["beginDialog"]
        self.assertEqual(dialog["kind"], "OnUnknownIntent")
        self.assertEqual(
            [action["kind"] for action in dialog["actions"]],
            ["SendActivity", "CancelAllDialogs"],
        )
        self.assertIn("could not return verified SharePoint results", dialog["actions"][0]["activity"])
        self.assertNotIn("FallbackCount", str(dialog))
        self.assertNotIn("BeginDialog", str(dialog))

    def test_implicit_escalation_remains_handled_without_claiming_transfer(self):
        dialog = load("topics", "Escalate.mcs.yml")["beginDialog"]
        self.assertEqual(dialog["kind"], "OnEscalate")
        self.assertEqual(
            [action["kind"] for action in dialog["actions"]],
            ["SendActivity", "CancelAllDialogs"],
        )
        message = dialog["actions"][0]["activity"]
        self.assertIn("Human handoff is not configured", message)
        self.assertIn("no transfer was performed", message)
        self.assertNotIn("conversationOutcome", str(dialog))
        self.assertNotIn("this is where the agent could provide", message)

    def test_controlled_search_redirect_is_preserved(self):
        dialog = load("topics", "Search.mcs.yml")["beginDialog"]
        self.assertEqual(dialog["kind"], "OnUnknownIntent")
        self.assertEqual(len(dialog["actions"]), 1)
        self.assertEqual(dialog["actions"][0]["kind"], "BeginDialog")
        self.assertEqual(
            dialog["actions"][0]["dialog"],
            "cnh_corpnetSearchHub.topic.SearchSharePoint",
        )

    def test_approved_classic_orchestration_retains_authentication(self):
        instructions = load("agent.mcs.yml")["instructions"]
        self.assertIn("Do not invent spelling corrections", instructions)
        self.assertIn("Do not promise a search, handoff", instructions)
        self.assertIn("Do not require a separate pre-flow Graph identity attestation", instructions)
        self.assertIn("effective search/export identity", instructions)
        self.assertIn("verified profile's nonempty directory mail", instructions)
        settings = load("settings.mcs.yml")
        self.assertFalse(settings["configuration"]["settings"]["GenerativeActionsEnabled"])
        self.assertNotIn("recognizer", settings["configuration"])
        self.assertFalse(settings["configuration"]["isAgentConnectable"])
        self.assertEqual(settings["configuration"]["aISettings"]["contentModeration"], "High")
        self.assertEqual(settings["authenticationMode"], "Integrated")
        self.assertEqual(settings["authenticationTrigger"], "Always")

    def test_screenshot_request_has_an_explicit_classic_trigger(self):
        dialog = load("topics", "SearchSharePoint.mcs.yml")["beginDialog"]
        self.assertIn("Search for SharePoint content", dialog["intent"]["triggerQueries"])
        self.assertEqual(dialog["actions"][0]["kind"], "SendActivity")
        self.assertIn("up to five verified file/page links with stored tags", dialog["actions"][0]["activity"])
        self.assertEqual(dialog["actions"][1]["kind"], "Question")
        self.assertEqual(dialog["actions"][1]["variable"], "Topic.DepartmentInput")


if __name__ == "__main__":
    unittest.main()
