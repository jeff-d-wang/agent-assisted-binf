"""Offline workflow tests. Claude responses here are fixtures, not scientific evidence."""
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import run_analysis as workflow


def reply(text="A fixture response", reason="end_turn", blocks=None):
    return {"model": "fixture-only", "content": blocks or [{"type": "text", "text": text}],
            "stop_reason": reason, "usage": {"input_tokens": 10, "output_tokens": 10}}


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.config = workflow.load_config(workflow.HERE / "cases/4hjo.json")
        self.config["output_dir"] = str(self.root)
        self.checks = {"pdb_id": "4hjo", "input_sha256": {
            path: workflow.digest(path) for key, path in self.config["structure"].items() if key != "chain"}}
        self.run = workflow.create_run(self.config, self.checks)
        self.state = {"stage": "plan", "messages": [], "draft": ""}

    def tearDown(self):
        self.temp.cleanup()

    def test_invalid_mutations_and_output_are_rejected(self):
        base = json.loads((workflow.HERE / "cases/4hjo.json").read_text())
        for changes in ({"mutations": ["L0R"]}, {"mutations": ["L858L"]},
                        {"mutations": ["L858R", "L858R"]}, {"output_dir": "datasets"},
                        {"api_key": "placeholder-not-a-key"}):
            with self.subTest(changes=changes):
                path = self.root / "case.json"
                path.write_text(json.dumps({**base, **changes}))
                with self.assertRaises(ValueError):
                    workflow.load_config(path)

    def test_mismatched_coordinate_files_stop_before_api(self):
        pdb = Path(self.config["structure"]["pdb"]).read_text()
        changed = self.root / "changed.pdb"
        # Change one real coordinate while preserving the entry ID.
        lines = pdb.splitlines(keepends=True)
        index = next(i for i, line in enumerate(lines) if line.startswith("ATOM  "))
        line = lines[index]
        lines[index] = line[:30] + f"{float(line[30:38]) + 1:8.3f}" + line[38:]
        changed.write_text("".join(lines))
        self.config["structure"]["pdb"] = str(changed)
        with self.assertRaisesRegex(ValueError, "coordinates differ"):
            workflow.preflight(self.config)

    @patch("run_analysis.call_claude", return_value=reply("Plan fixture"))
    @patch("run_analysis.compute")
    def test_quitting_plan_never_computes_and_resume_keeps_plan(self, compute, api):
        with patch("builtins.input", return_value="quit"), patch("sys.stdout", new=io.StringIO()):
            workflow.interact(self.run, self.config)
            workflow.interact(self.run, self.config)
        compute.assert_not_called()
        self.assertEqual(api.call_count, 1)
        self.assertEqual(json.loads((self.run / "state.json").read_text())["stage"], "plan")
        self.assertFalse((self.run / "RESULTS.md").exists())

    @patch("run_analysis.call_claude", return_value=reply(reason="max_tokens"))
    def test_truncated_response_is_not_a_completed_draft(self, api):
        with self.assertRaisesRegex(ValueError, "max_tokens"), patch("sys.stdout", new=io.StringIO()):
            workflow.ask_claude(self.run, self.config, self.state, "Plan")
        self.assertEqual(self.state["messages"], [])
        self.assertTrue((self.run / "api/001.response.json").exists())
        self.assertEqual(api.call_args.args[0]['max_tokens'], 32000)

    @patch("run_analysis.call_claude", side_effect=ValueError("HTTP 429"))
    def test_api_failure_preserves_conversation_and_records_failure(self, api):
        with self.assertRaisesRegex(ValueError, "429"), patch("sys.stdout", new=io.StringIO()):
            workflow.ask_claude(self.run, self.config, self.state, "Plan")
        self.assertEqual(self.state["messages"], [])
        self.assertIn("api_error", (self.run / "events.jsonl").read_text())

    @patch("run_analysis.seal_evidence")
    def test_tool_results_round_trip_and_unknown_tool_is_not_executed(self, seal):
        tool = {"type": "tool_use", "id": "tool1", "name": "arbitrary_shell", "input": {"command": "no"}}
        with patch("run_analysis.call_claude", side_effect=[reply(reason="tool_use", blocks=[tool]), reply("Revised")]) as api:
            with patch("sys.stdout", new=io.StringIO()):
                result = workflow.ask_claude(self.run, self.config, self.state, "Interpret", allow_tools=True)
        self.assertEqual(result, "Revised")
        returned = api.call_args.args[0]["messages"][2]["content"][0]
        self.assertTrue(returned["is_error"])
        self.assertEqual(returned["tool_use_id"], "tool1")

    def test_changed_input_stops_resume(self):
        data = self.root / "input.pdb"
        data.write_text("original")
        workflow.save_json(self.run / "input_checks.json", {"input_sha256": {str(data): workflow.digest(data)}})
        data.write_text("changed")
        with self.assertRaisesRegex(ValueError, "input changed"):
            workflow.check_inputs_unchanged(self.run)

    def test_manifest_detects_changed_evidence(self):
        evidence = self.run / "example.csv"
        evidence.write_text("original")
        workflow.save_json(self.run / "manifest.json", {"example.csv": workflow.digest(evidence)})
        evidence.write_text("changed")
        with self.assertRaisesRegex(ValueError, "evidence changed"):
            workflow.verify_manifest(self.run)

    def test_pubmed_records_include_real_text_and_urls(self):
        xml = b'<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>123</PMID><Article><ArticleTitle>A <i>title</i></ArticleTitle><Abstract><AbstractText>Evidence.</AbstractText></Abstract><Journal><Title>Journal</Title></Journal></Article></MedlineCitation></PubmedArticle></PubmedArticleSet>'
        with patch("run_analysis.retrieve", side_effect=[b'{"esearchresult":{"idlist":["123"]}}', xml]), patch("run_analysis.time.sleep"):
            result = workflow.search_pubmed(self.run, "EGFR")
        self.assertEqual(result["papers"][0]["title"], "A title")
        self.assertEqual(result["papers"][0]["abstract"], "Evidence.")
        self.assertEqual(result["papers"][0]["url"], "https://pubmed.ncbi.nlm.nih.gov/123/")
        self.assertTrue(list((self.run / "data").glob("pubmed_*.xml")))

    def test_http_request_uses_claude_endpoint_and_header_only_credentials(self):
        response = io.BytesIO(json.dumps(reply()).encode())
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-placeholder"}), \
             patch("run_analysis.urllib.request.urlopen", return_value=response) as opener:
            workflow.call_claude({"model": "fixture", "messages": [], "max_tokens": 8})
        request = opener.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.anthropic.com/v1/messages")
        self.assertEqual(request.get_header("X-api-key"), "test-placeholder")
        self.assertNotIn(b"test-placeholder", request.data)
        self.assertEqual(opener.call_args.kwargs['timeout'], 360)

    def test_failed_pymol_check_is_rejected(self):
        table = self.run / "tables"
        table.mkdir()
        c = {**self.config, "mutations": ["G719S"]}
        (table / "mapping.csv").write_text("mutation,sifts_alignment_agree\nG719S,True\n")
        (table / "measurements.csv").write_text("mutation,min_dist_ligand\nG719S,AQ4:5.06\n")
        (table / "pymol_check.csv").write_text("mutation,ligand,agrees\nG719S,AQ4,False\n")
        with self.assertRaisesRegex(ValueError, "PyMOL check failed"):
            workflow.verify_outputs(self.run, c)

    def test_contact_control_exposes_cutoff_sensitivity(self):
        (self.run / "tables").mkdir()
        for name in ("mapping.csv", "measurements.csv"):
            (self.run / "tables" / name).write_bytes((workflow.HERE / "tables" / name).read_bytes())
        rows = workflow.contact_sensitivity(self.run, self.config)["rows"]
        flags = {(r["mutation"], r["cutoff_A"]): r["ligand_in_cutoff"] for r in rows}
        for mutation in ("G719S", "L858R"):
            self.assertFalse(flags[mutation, 5.0])
            self.assertTrue(flags[mutation, 6.0])
        self.assertFalse(flags["L861Q", 6.0])

    def test_complete_interactive_flow_with_fixture_claude(self):
        draft = "# Fixture report\n" + ", ".join(self.config["mutations"])
        (self.run / "figures").mkdir()
        (self.run / "figures/structure_annotated.png").write_bytes(b"fixture")
        with patch("run_analysis.call_claude", side_effect=[reply("Plan"), reply(draft), reply(draft + "\nRevised")]) as api, \
             patch("run_analysis.compute") as compute, \
             patch("run_analysis.evidence_packet", return_value={"fixture": True}), \
             patch("run_analysis.verify_outputs") as verify, \
             patch("run_analysis.verify_manifest"), patch("run_analysis.seal_evidence"), \
             patch("builtins.input", side_effect=["approve", "Explain the limitations", "accept", "Checked fixture; limited to one structure."]), \
             patch("sys.stdout", new=io.StringIO()):
            workflow.interact(self.run, self.config)
        self.assertEqual(api.call_count, 3)
        compute.assert_called_once()
        verify.assert_called_once()
        self.assertEqual(json.loads((self.run / "state.json").read_text())["stage"], "accepted")
        self.assertIn("Revised", (self.run / "RESULTS.md").read_text())
        events = (self.run / "events.jsonl").read_text()
        self.assertLess(events.index("plan_approved"), events.index("follow_up"))
        self.assertIn("report_accepted", events)
        self.assertIn("fixture-only", events)


if __name__ == "__main__":
    unittest.main()
