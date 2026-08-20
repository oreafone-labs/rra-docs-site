from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class WorkflowTests(unittest.TestCase):
    def test_pull_requests_validate_a_site_when_present(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "validate.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("pull_request:", workflow)
        self.assertIn("hashFiles('site/index.html')", workflow)
        self.assertIn("python tools/validate_public.py", workflow)


if __name__ == "__main__":
    unittest.main()
