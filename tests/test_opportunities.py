import json,unittest
from pathlib import Path
D=json.loads((Path(__file__).resolve().parents[1]/'public/data/opportunities.json').read_text(encoding='utf-8'))
class ClimateScoutTests(unittest.TestCase):
 def test_ids_unique(self):
  self.assertEqual(len({x['id'] for x in D['leads']}),len(D['leads']))
 def test_evidence_no_unsupported_abatement(self):
  self.assertEqual(D['independent_verified_abatement_tco2e'],0)
  for x in D['leads']:
   self.assertTrue(x['source_url'].startswith('https://'))
   self.assertIsNone(x['verified_abatement_tco2e'])
   self.assertEqual(x['additionality'],'unknown')
   self.assertFalse(x['owner_confirmed'])
 def test_sources_have_dates(self):
  for x in D['leads']:
   self.assertRegex(x['source_publication_date'],r'^20\\d{2}-\\d{2}-\\d{2}$'.replace('\\\\','\\'))
