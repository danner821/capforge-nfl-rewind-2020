#!/usr/bin/env python3
"""V13: spoiler-free 2020 contracts/staff baseline audit.

This is a diagnostic only. V12 and previous import files are never rewritten
here, and modeled Madden salaries are NOT represented as historical NFL facts.
"""
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
PLAYERS = ROOT / "preview/players-2020-nine-class-scoutfix-v12.json"
TEAMS = ROOT / "preview/teams-2020-roofs-v2.json"
REPORT = ROOT / "preview/v13-2020-contract-staff-audit.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    data, teams_data = read(PLAYERS), read(TEAMS)
    assert data["schemaVersion"] == 3 and data["meta"]["baseSeason"] == 2020
    assert teams_data["schemaVersion"] == 3
    roster = [p for p in data["players"] if p["pool"] == "roster"]
    assert len(roster) == 2293, "V12 historical roster count changed"
    teams = teams_data["teams"]
    assert len(teams) == 32 and len({t["abbr"] for t in teams}) == 32
    by_team = defaultdict(list)
    for p in roster:
        assert p["teamAbbr"] in {t["abbr"] for t in teams}
        by_team[p["teamAbbr"]].append(p)
    assert len(by_team) == 32

    salary_totals = {}
    flat_schedule = 0
    zero_bonus = 0
    approx_quarter_guarantee = 0
    initial_zero_guarantee = 0
    signed_2020 = 0
    years_hist = Counter()
    for abbr, players in sorted(by_team.items()):
        team_total = 0
        for p in players:
            c = p["contract"]
            years = c["years"]
            assert type(years) is int and 1 <= years <= 5
            years_hist[years] += 1
            assert c.get("signedSeason") == 2020
            signed_2020 += 1
            salary = c["salary"]
            guarantee = c["guarantee"]
            assert type(salary) is int and salary > 0
            assert type(guarantee) is int and guarantee >= 0
            assert 0 <= c["currentYearIndex"] < years
            assert type(c["currentGuarantee"]) is int and c["currentGuarantee"] >= 0
            for field in ("salaryByYear", "bonusByYear", "guaranteeByYear"):
                values = c[field]
                assert isinstance(values, list) and len(values) == years, field
                assert all(type(v) is int and v >= 0 for v in values), field
            assert c["salaryByYear"][0] == salary
            assert c["guaranteeByYear"][0] == c["currentGuarantee"]
            assert all(c["salaryByYear"]), "Rostered player has zero modeled annual salary"
            assert isinstance(c["extension"], dict)
            flat_schedule += (len(set(c["salaryByYear"])) == 1)
            zero_bonus += (not any(c["bonusByYear"]))
            approx_quarter_guarantee += abs(guarantee - round(salary * .25)) <= 2
            initial_zero_guarantee += c["currentGuarantee"] == 0
            team_total += salary
        salary_totals[abbr] = team_total
    assert signed_2020 == 2293
    assert sorted(salary_totals) == sorted(t["abbr"] for t in teams)

    # Teams V2 carries stadium, division, colors and logos; it does not contain
    # a supported historical coaching-staff payload. Do not invent that schema.
    staff_keys = ("staff", "coaches", "headCoach", "offensiveCoordinator",
                  "defensiveCoordinator", "coachingStaff")
    staff_embedded = [t["abbr"] for t in teams if any(k in t for k in staff_keys)]

    report = {
        "status": "AUDIT_ONLY_V12_IMPORT_UNCHANGED_HISTORICAL_ACCURACY_UNVERIFIED",
        "baseSeason": 2020,
        "auditedPlayerFile": PLAYERS.name,
        "historicalRosterCount": len(roster),
        "teamCount": len(teams),
        "draftClassesUntouched": True,
        "modeledContractWarnings": [
            "2020 contract values come from a salary heuristic, not authenticated 2020 contract/cap-hit ledgers",
            "Signed season is hard-coded to 2020; do not treat it as the player's real signature date",
            "Flat annual salaries and zero bonus schedules are source-model placeholders",
            "Any real 2020 salary cap comparisons require a verified per-player cap-hit/bonus source"
        ],
        "contractStructure": {
            "rosteredContractsChecked": signed_2020,
            "contractYearsHistogram": dict(sorted(years_hist.items())),
            "flatAnnualSalarySchedules": flat_schedule,
            "zeroBonusSchedules": zero_bonus,
            "guaranteeApproximately25PercentAnnualSalary": approx_quarter_guarantee,
            "zeroFirstYearGuarantees": initial_zero_guarantee,
            "teamSalarySumsRange": {
                "min": min(salary_totals.values()),
                "median": median(salary_totals.values()),
                "max": max(salary_totals.values()),
            },
            "teamSumsAreModeledSalaryNotNFL2020CapHits": True,
            "teamModeledAnnualSalaryTotals": dict(sorted(salary_totals.items())),
        },
        "coachingStaff": {
            "teamsWithEmbeddedStaffFields": staff_embedded,
            "currentImportRecommendation": "Default staff; no historical staff import validated",
            "historical2020CoachAssignmentsVerified": False,
            "staffSchemaVerified": False,
        },
        "nextEvidenceRequired": [
            "Source-verifiable historical 2020 NFL contracts, cap hits, remaining years and guarantees",
            "A known CapForge-compatible historical coaching staff JSON schema",
            "Disposable-game 2020 import, free agency and later season simulation validation",
        ],
        "privacy": "Only aggregates and team-level modeled salaries; no hidden potentials or progression disclosed",
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "result": report["status"],
        "historical_roster_count": len(roster),
        "teams": len(teams),
        "flat_salary_schedules": flat_schedule,
        "zero_bonus_schedules": zero_bonus,
        "staff_schema": "not_verified",
        "report": str(REPORT.relative_to(ROOT)),
    }, indent=2))


if __name__ == "__main__":
    main()
