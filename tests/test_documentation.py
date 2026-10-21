import unittest
from documentation import verify_docs


class DocumentationTests(unittest.TestCase):
    def test_linked_documentation_and_required_update_map(self):
        result = verify_docs()
        self.assertGreater(result['documents'], 20)
        self.assertEqual(result['broken_links'], [])
        self.assertEqual(result['unreachable'], [])

    def test_broken_and_unlinked_document_reported(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'README.md').write_text('[Bad](missing.md)', encoding='utf-8')
            (root / 'unlinked.md').write_text('Forgotten', encoding='utf-8')
            result = verify_docs(root)
            self.assertTrue(result['broken_links'])
            self.assertEqual(result['unreachable'], ['unlinked.md'])
