import datetime as dt
import sys
from pathlib import Path
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ingest_israel as im


def raw(plume, date="2026-10-03T12:00:00Z", lon=34.9, lat=32.0, rate=700):
    return {
        "plume_id": plume, "scene_timestamp": date, "gas": "CH4", "status": "published",
        "mission_phase": "production", "plume_quality": "good", "instrument": "tan",
        "geometry_json": {"type": "Point", "coordinates": [lon, lat]},
        "emission_auto": rate, "emission_uncertainty_auto": 150
    }


class MonitorTests(unittest.TestCase):
    def test_normalize_israel_region_candidate(self):
        obs = im.normalize(raw("A"))
        self.assertEqual(obs["rate_kg_h_observed"], 700)
        self.assertEqual(obs["attribution"], "unknown")
        self.assertEqual(obs["geographic_scope"], "region_bbox_not_jurisdiction")

    def test_no_unpublished_bad_firstlight_or_wrong_gas(self):
        for changes in [{"plume_quality":"bad"}, {"status":"valid"}, {"gas":"CO2"},
                        {"mission_phase":"first_light"}, {"emission_auto":100}]:
            item = raw("A")
            item.update(changes)
            self.assertIsNone(im.normalize(item))

    def test_excludes_outside_bbox(self):
        self.assertIsNone(im.normalize(raw("A",lon=39.0)))

    def test_dedup_and_distinct_dates(self):
        a=im.normalize(raw("A",date="2026-10-03T12:00:00Z"))
        b=im.normalize(raw("B",date="2026-10-04T12:00:00Z"))
        prior={"observations":[a],"last_success_at":"2026-10-04T13:00:00Z"}
        updated=im.update(prior,[raw("A",date="2026-10-03T12:00:00Z"),raw("B",date="2026-10-04T12:00:00Z")],"2026-10-05T01:00:00Z")
        self.assertEqual(updated["new_ids_since_previous_success"],1)
        self.assertEqual(len(updated["observations"]),2)
        self.assertEqual(len(updated["review_candidates"]),1)
        self.assertFalse(updated["review_candidates"][0]["outreach_approved"])
        self.assertFalse(updated["review_candidates"][0]["operator_identified"])

    def test_quality_missing_is_quarantined_without_outreach(self):
        item=raw("P",date="2026-10-03T12:00:00Z")
        item["plume_quality"]=None
        self.assertIsNone(im.normalize(item))
        preliminary=im.normalize(item,allow_unknown_quality=True)
        self.assertEqual(preliminary["quality_state"],"unknown_not_approved")
        result=im.update({},[item],"2026-10-05T01:00:00Z")
        self.assertEqual(result["observations"],[])
        self.assertEqual(len(result["unconfirmed_quality_observations"]),1)
        self.assertEqual(result["review_candidates"],[])

    def test_single_day_not_candidate(self):
        updated=im.update({},[raw("A"),raw("B")],"2026-10-05T01:00:00Z")
        self.assertEqual(updated["review_candidates"],[])

    def test_api_page_and_filter_params(self):
        seen=[]
        def fake_fetch(url, token):
            seen.append(url)
            return {"items": [raw("A")], "total_count":1}
        items=im.pull(fetch=fake_fetch)
        self.assertEqual(len(items),1)
        from urllib.parse import urlparse,parse_qs
        params=parse_qs(urlparse(seen[0]).query)
        self.assertEqual(params["bbox"],[str(x) for x in im.BBOX])
        self.assertEqual(params["plume_gas"],["CH4"])

    def test_malformed_fetch_fails_closed(self):
        with self.assertRaises(ValueError):
            im.pull(fetch=lambda url,token:{"unexpected":"structure"})

if __name__=="__main__":
    unittest.main()
