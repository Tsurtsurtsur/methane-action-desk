import unittest,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class EvidenceTests(unittest.TestCase):
 def setUp(self):
  self.sites=json.loads((ROOT/'public/data/sites.json').read_text(encoding='utf-8'))['sites']
  self.actions=json.loads((ROOT/'public/data/actions.json').read_text(encoding='utf-8'))['actions']
 def test_ten_sites_unique(self):
  self.assertEqual(len(self.sites),10)
  self.assertEqual(len({s['id'] for s in self.sites}),10)
 def test_top_site(self):
  self.assertEqual(max(self.sites,key=lambda s:s['ch4_tonnes_per_hour_observed'])['id'],'silivri')
 def test_impact_never_inferred(self):
  self.assertTrue(all(a['outcome_ch4_tonnes_avoided_verified'] is None for a in self.actions if a['status']!='independently_verified'))
 def test_no_annualization(self):
  self.assertTrue(all('annual_emissions' not in s for s in self.sites))
if __name__=='__main__':unittest.main()
