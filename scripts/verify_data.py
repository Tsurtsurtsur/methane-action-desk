from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'public/data/sites.json').read_text(encoding='utf-8'))
actions=json.loads((ROOT/'public/data/actions.json').read_text(encoding='utf-8'))
sites=data['sites']
assert len(sites)==10
assert len(set(s['id'] for s in sites))==10
assert all(s['ch4_tonnes_per_hour_observed']>0 and s['operator_confidence'] in {'unverified','reported','independently_verified'} for s in sites)
assert all('annual_emissions' not in s for s in sites)
for a in actions['actions']:
 assert a['status'] in {'research_complete','outreach_requested','response_received','repair_claimed','independently_verified'}
 if a['outcome_ch4_tonnes_avoided_verified'] is not None:
  assert a['status']=='independently_verified'
  assert isinstance(a['outcome_ch4_tonnes_avoided_verified'],(int,float))
  assert a['outcome_ch4_tonnes_avoided_verified']>=0
print('Evidence validation passed; no unsupported impact claims.')
