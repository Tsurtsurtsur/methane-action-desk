import json
from pathlib import Path
import unittest
root=Path(__file__).resolve().parents[1]
class AutomationPolicyTests(unittest.TestCase):
 def test_no_unconsented_partners(self):
  partners=json.loads((root/'automation/consenting_partners.json').read_text(encoding='utf-8'))
  self.assertEqual(partners['partners'],[])
 def test_feed_does_not_claim_verified_impact(self):
  feed=json.loads((root/'public/data/israel-monitor.json').read_text(encoding='utf-8'))
  self.assertNotIn('annual_emissions',feed)
  for c in feed.get('review_candidates',[]):
   self.assertEqual(c['outreach_approved'],False)
if __name__=="__main__":unittest.main()
