import json
import unittest
from datetime import date
from pathlib import Path

D = json.loads((Path(__file__).resolve().parents[1] / 'public/data/opportunities.json').read_text(encoding='utf-8'))

class ClimateScoutTests(unittest.TestCase):
    def test_unique_ids_and_sources(self):
        self.assertEqual(len({x['id'] for x in D['leads']}), len(D['leads']))
        for lead in D['leads']:
            self.assertTrue(lead['source_url'].startswith('https://'))
            date.fromisoformat(lead['source_publication_date'])
            self.assertTrue(lead['next_step'])
            self.assertTrue(lead['missing'])

    def test_impact_is_only_recorded_with_verification(self):
        impact = D['independent_verified_abatement_tco2e']
        self.assertGreaterEqual(impact, 0)
        verified = [x for x in D['leads'] if x['verified_abatement_tco2e'] is not None]
        if impact:
            self.assertTrue(verified)
        for lead in D['leads']:
            if lead['verified_abatement_tco2e'] is not None:
                self.assertGreater(lead['verified_abatement_tco2e'], 0)
                self.assertEqual(lead['stage'], 'independently_verified')
                self.assertIn('verification_source_url', lead)
                self.assertTrue(lead['verification_source_url'].startswith('https://'))

    def test_open_deadlines_and_snapshot(self):
        date.fromisoformat(D['last_researched'])
        date.fromisoformat(D['review_due'])
        for lead in D['leads']:
            if lead['action_deadline']:
                date.fromisoformat(lead['action_deadline'])
