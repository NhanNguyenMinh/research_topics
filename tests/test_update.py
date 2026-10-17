import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from update import publication_date, from_crossref

class MetadataTests(unittest.TestCase):
    def test_online_date_precedes_future_print_issue(self):
        self.assertEqual(publication_date({'published-online':{'date-parts':[[2026,10,1]]},'published-print':{'date-parts':[[2027,1]]}}), '2026-10-01')
    def test_partial_date_is_preserved(self):
        self.assertEqual(publication_date({'published':{'date-parts':[[2025]]}}),'2025')
    def test_future_or_unrelated_or_missing_date_rejected(self):
        item={'DOI':'10.1234/example','title':['Neural operator for mechanics'],'type':'journal-article','published':{'date-parts':[[2027,1,1]]}}
        topics=[{'id':'sciml','keywords':['neural operator']}]
        self.assertIsNone(from_crossref(item,topics,'2026-10-18'))
        item['published']['date-parts']=[[2026,1,1]]
        self.assertIsNotNone(from_crossref(item,topics,'2026-10-18'))
        item['title']=['Unrelated clinical research']
        self.assertIsNone(from_crossref(item,topics,'2026-10-18'))
        item.pop('published')
        self.assertIsNone(from_crossref(item,topics,'2026-10-18'))

if __name__=='__main__':unittest.main()
