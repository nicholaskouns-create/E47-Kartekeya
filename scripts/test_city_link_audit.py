"""Regression coverage for GitHub Pages subpath resolution."""
import unittest
from scripts.audit_city_links import normalized

class PagesResolution(unittest.TestCase):
    def test_nested_home_and_instrument_links(self):
        current='interfaces/civic-assignment/index.html'
        self.assertEqual(normalized(current,'../../'),'index.html')
        self.assertEqual(normalized(current,'../observatory/?view=signal#main'),'interfaces/observatory/index.html')
        self.assertEqual(normalized('index.html','interfaces/observatory/bridge.mjs'),'interfaces/observatory/bridge.mjs')

    def test_external_and_fragment_links_are_excluded(self):
        for link in ['#main','https://example.com/','https://nicholaskouns-create.github.io/','mailto:hello@example.com','javascript:alert(1)']:
            self.assertIsNone(normalized('index.html',link))

    def test_canonical_absolute_and_root_relative_paths(self):
        expected='interfaces/observatory/index.html'
        self.assertEqual(normalized('index.html','https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/observatory/'),expected)
        self.assertEqual(normalized('index.html','/E47-Kartekeya/interfaces/observatory/?view=city'),expected)

if __name__=='__main__':unittest.main()
