#!/usr/bin/env python3
"""Low-volume, read-only Carbon Mapper observation monitor. No operator attribution or emails."""
import datetime as dt
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "public/data/israel-monitor.json"
API = "https://api.carbonmapper.org/api/v1/catalog/plumes/annotated"
# Geographic region of interest, NOT an administrative border. Includes neighboring territories.
BBOX = (34.1, 29.4, 36.0, 33.5)
LOOKBACK_DAYS = 45
INITIAL_BACKFILL_DAYS = 365
LIMIT = 100
MAX_PAGES = 24
MIN_KG_H = 300
MAX_PUBLIC_RECORDS = 700
TIMEOUT = 25
SCHEMA_VERSION = 1


def now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_time(value):
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def inside(lon, lat):
    return BBOX[0] <= lon <= BBOX[2] and BBOX[1] <= lat <= BBOX[3]


def get_json(url, token=None, opener=None):
    headers = {"Accept": "application/json", "User-Agent": "CH4-Action-Desk/0.1 (independent noncommercial climate monitoring; https://github.com/Tsurtsurtsur/methane-action-desk)"}
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(url, headers=headers)
    response = (opener or urllib.request.urlopen)(request, timeout=TIMEOUT)
    with response as stream:
        raw = stream.read(4_000_001)
    if len(raw) > 4_000_000:
        raise ValueError("API response exceeds safety limit")
    return json.loads(raw)


def pull(token=None, fetch=get_json, days=LOOKBACK_DAYS):
    start = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    query = [("bbox", value) for value in BBOX] + [
        ("plume_gas", "CH4"), ("status", "published"), ("qualities", "good"),
        ("sectors", "6A"), ("emission_min", MIN_KG_H),
        ("created_at", start + "/.."), ("limit", LIMIT)
    ]
    items = []
    for page in range(MAX_PAGES):
        url = API + "?" + urllib.parse.urlencode(query + [("offset", page * LIMIT)])
        response = fetch(url, token)
        if not isinstance(response, dict) or not isinstance(response.get("items"), list):
            raise ValueError("Unexpected Carbon Mapper API response; refusing to overwrite saved data")
        batch = response["items"]
        if len(batch) > LIMIT:
            raise ValueError("Unexpected API page size")
        items.extend(batch)
        total = response.get("total_count")
        if total is not None and not isinstance(total, int):
            raise ValueError("Unexpected total_count type")
        if len(batch) < LIMIT:
            return items
        if total is not None and len(items) >= total:
            return items
    sample = items[0] if items else {}
    loc = sample.get("geometry_json", {}).get("coordinates") if isinstance(sample.get("geometry_json"), dict) else None
    raise ValueError("Pagination limit reached for waste sites; possible ignored bbox/filter. "
                     + "total=" + str(total) + " first_coordinates=" + str(loc)[:50])


def normalize(raw, allow_unknown_quality=False):
    if not isinstance(raw, dict) or raw.get("gas") != "CH4":
        return None
    if raw.get("status") != "published" or raw.get("mission_phase") == "first_light":
        return None
    quality = raw.get("plume_quality") or raw.get("quality")
    if quality != "good" and not (allow_unknown_quality and quality is None):
        return None
    g = raw.get("geometry_json")
    if not isinstance(g, dict) or g.get("type") != "Point":
        return None
    point = g.get("coordinates")
    if not isinstance(point, list) or len(point) < 2:
        return None
    try:
        lon, lat = float(point[0]), float(point[1])
        rate = float(raw["emission_auto"])
    except (TypeError, ValueError, KeyError):
        return None
    if not inside(lon, lat) or not MIN_KG_H <= rate < 10_000_000:
        return None
    plume_id = raw.get("plume_id")
    acquired = raw.get("scene_timestamp")
    if not isinstance(plume_id, str) or not plume_id or not isinstance(acquired, str):
        return None
    try:
        parsed = parse_time(acquired)
        if parsed.tzinfo is None:
            return None
    except ValueError:
        return None
    uncertainty = raw.get("emission_uncertainty_auto")
    try:
        uncertainty = round(float(uncertainty), 1) if uncertainty is not None else None
    except (TypeError, ValueError):
        uncertainty = None
    return {
        "id": plume_id[:100], "acquired_at": acquired, "longitude": round(lon, 5),
        "latitude": round(lat, 5), "rate_kg_h_observed": round(rate, 1),
        "uncertainty_kg_h": uncertainty, "instrument": str(raw.get("instrument") or "")[:20],
        "sector_code_unverified": str(raw.get("sector") or "NA")[:20],
        "geographic_scope": "region_bbox_not_jurisdiction",
        "attribution": "unknown",
        "quality_state": "good" if quality == "good" else "unknown_not_approved"
    }


def group_candidates(records):
    """Conservative heuristic: approximate 0.01-degree cells, distinct observation days."""
    clusters = defaultdict(list)
    for r in records:
        cell = (round(r["longitude"], 2), round(r["latitude"], 2))
        clusters[cell].append(r)
    result = []
    for (lon, lat), entries in clusters.items():
        dates = {r["acquired_at"][:10] for r in entries}
        if len(dates) < 2:
            continue
        result.append({
            "cell": str(lon) + "," + str(lat),
            "observation_count": len(entries),
            "distinct_days": len(dates),
            "latest_observation": max(r["acquired_at"] for r in entries),
            "max_observed_kg_h": max(r["rate_kg_h_observed"] for r in entries),
            "assessment": "manual_review_required",
            "operator_identified": False,
            "outreach_approved": False
        })
    return sorted(result, key=lambda r: (-r["max_observed_kg_h"], r["cell"]))[:100]


def update(prior, raw_items, checked_at, query_days=LOOKBACK_DAYS):
    clean = [normalize(raw) for raw in raw_items]
    recent = [r for r in clean if r]
    review_only = [normalize(raw, allow_unknown_quality=True) for raw in raw_items]
    review_only = [r for r in review_only if r and r["quality_state"] == "unknown_not_approved"]
    unconfirmed = {r["id"]: r for r in prior.get("unconfirmed_quality_observations", [])}
    for r in review_only:
        unconfirmed[r["id"]] = r
    by_id = {r["id"]: r for r in prior.get("observations", [])}
    previously_known = set(by_id)
    for r in recent:
        by_id[r["id"]] = r
    all_records = sorted(by_id.values(), key=lambda r: (r["acquired_at"], r["id"]), reverse=True)
    new_count = sum(r["id"] not in previously_known for r in recent)
    return {
        "schema_version": SCHEMA_VERSION, "source": "Carbon Mapper", "source_url": API,
        "source_terms_url": "https://carbonmapper.org/terms",
        "scope": "Geographic Israel-region bounding box 34.1–36.0 E, 29.4–33.5 N, including neighboring territories. Not an administrative boundary.",
        "status": "ok", "last_attempt_at": checked_at, "last_success_at": checked_at,
        "source_error": None, "observation_window_days": query_days,
        "backfill_complete": True,
        "minimum_display_rate_kg_h": MIN_KG_H,
        "last_scan_observations": len(recent),
        "last_scan_api_records": len(raw_items),
        "last_scan_metadata": {"gas_counts": {k: sum(str(r.get("gas")) == k for r in raw_items) for k in ("CH4", "CO2", "None")},
                               "quality_good": sum(str(r.get("plume_quality") or r.get("quality")) == "good" for r in raw_items),
                               "plume_quality_values": {k: sum(str(r.get("plume_quality")) == k for r in raw_items) for k in ("good", "questionable", "bad", "None")},
                               "quality_values": {k: sum(str(r.get("quality")) == k for r in raw_items) for k in ("good", "questionable", "bad", "None")},
                               "mission_phases": {k: sum(str(r.get("mission_phase")) == k for r in raw_items) for k in ("first_light", "production", "None")},
                               "inside_bbox": sum(isinstance(r.get("geometry_json"), dict) and isinstance(r["geometry_json"].get("coordinates"), list) and len(r["geometry_json"]["coordinates"]) >= 2 and inside(float(r["geometry_json"]["coordinates"][0]),float(r["geometry_json"]["coordinates"][1])) for r in raw_items)},
        "new_ids_since_previous_success": new_count,
        "first_baseline": prior.get("last_success_at") is None,
        "observations": all_records[:MAX_PUBLIC_RECORDS],
        "unconfirmed_quality_observations": sorted(unconfirmed.values(), key=lambda r: r["acquired_at"], reverse=True)[:100],
        "review_candidates": group_candidates(all_records[:MAX_PUBLIC_RECORDS]),
        "methodology": "Published good-quality CH4 point observations only. No evidence of continuous emissions, operator, facility, jurisdiction, legal breach or verified abatement. Spatial grouping is a heuristic, not a source match."
    }


def main():
    prior = json.loads(OUTPUT.read_text(encoding="utf-8"))
    checked = now()
    try:
        days = LOOKBACK_DAYS if prior.get("backfill_complete") else INITIAL_BACKFILL_DAYS
        if os.getenv("GITHUB_EVENT_NAME") == "push":
            days = INITIAL_BACKFILL_DAYS  # one-time diagnostic or code revision run
        items = pull(os.getenv("CARBON_MAPPER_API_TOKEN"), days=days)
        result = update(prior, items, checked, query_days=days)
    except Exception as e:
        # Preserve all previous observations and last successful acquisition.
        result = dict(prior)
        result.update(status="source_error", last_attempt_at=checked,
                      source_error=(type(e).__name__ + ": " + str(e))[:180])
        print("Data source failed; previously verified source records kept. " + result["source_error"], file=sys.stderr)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Monitor status={result['status']}; records={len(result.get('observations', []))}; "
          f"review candidates={len(result.get('review_candidates', []))}")
    if result["status"] != "ok":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
