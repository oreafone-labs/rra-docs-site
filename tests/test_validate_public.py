from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from tools.validate_public import validate


class PublicValidationTests(unittest.TestCase):
    def make_site(self, root: Path, body: str) -> None:
        site = root / "site"
        site.mkdir()
        (site / "index.html").write_text(body, encoding="utf-8")
        (site / "build-metadata.json").write_text(
            json.dumps(
                {
                    "source_revision": "a" * 40,
                    "authority": "public_projection_only",
                }
            ),
            encoding="utf-8",
        )

    def test_valid_projection(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_site(root, "<p>RRA</p>")
            self.assertEqual(validate(root), [])

    def test_private_link_is_rejected(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_site(root, "https://github.com/oreafone-labs/rra-ops")
            self.assertTrue(validate(root))

    def test_missing_local_link_is_rejected(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_site(root, '<a href="missing.html">Missing</a>')
            self.assertTrue(validate(root))


if __name__ == "__main__":
    unittest.main()
