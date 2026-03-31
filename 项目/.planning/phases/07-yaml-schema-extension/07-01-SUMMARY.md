---
phase: 07-yaml-schema-extension
plan: 01
subsystem: learning-system
tags: [spaced-repetition, yaml-schema, interval-rules, sub-points, graduation, regression]

# Dependency graph
requires: []
provides:
  - "interval-rules.md: consecutive_success lookup table (0→1d through 9+→90d), ok-cap formula, graduation/regression conditions"
  - "sub-points-rules.md: sub_points YAML schema, review_sessions append-only log schema, covered/uncovered status update rules"
affects: [07-02, 07-03, SKILL.md updates, all YAML card reviews]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "consecutive_success → interval lookup table (manual SM-2-inspired, 1.4-1.7x growth)"
    - "ok-result cap: min(lookup_value, last_interval × 1.3)"
    - "sub_points flat list with per-item weak/ok/good status inside card YAML"
    - "review_sessions append-only log with covered_sub_points list"

key-files:
  created:
    - "00. learning/learning-behavior-system/interval-rules.md"
    - "00. learning/learning-behavior-system/sub-points-rules.md"
  modified: []

key-decisions:
  - "Graduation threshold: consecutive_success >= 8 AND last_interval >= 30d (not just count-based)"
  - "Regression threshold: consecutive_failures >= 3 consecutive (not 8 cumulative like Anki leech)"
  - "ok result increments consecutive_success but caps interval growth at min(lookup, last × 1.3)"
  - "sub_points are static lists, not independently scheduled — card remains minimum scheduling unit"
  - "uncovered sub_points retain status (not forgotten just because not asked this session)"

patterns-established:
  - "interval-rules.md is the single authoritative source for next_review calculation — no ad-hoc estimation"
  - "sub-points-rules.md governs how sub_point status evolves — covered/uncovered logic explicit"

requirements-completed: [GRADUATE-01, GRADUATE-02, GRADUATE-03, SUBPOINT-01, SUBPOINT-02, SUBPOINT-03]

# Metrics
duration: 8min
completed: 2026-03-31
---

# Phase 07 Plan 01: YAML Schema Extension Rule Documents Summary

**SM-2-inspired consecutive_success lookup table (1d–90d) with graduation/regression conditions and sub_points YAML schema with append-only review_sessions tracking**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-03-31T07:20:02Z
- **Completed:** 2026-03-31T07:28:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Created `interval-rules.md` as the authoritative interval calculation reference: 10-row lookup table, per-result rules (good/ok/fail), graduation condition (consecutive_success >= 8 AND interval >= 30d), regression condition (consecutive_failures >= 3), two worked examples with real cards 009 and 027
- Created `sub-points-rules.md` as the authoritative sub-knowledge-point tracking reference: sub_points field schema, review_sessions append-only log schema, covered/uncovered status update logic, backward compatibility rules, complete Card 017 OpenGL ES example with 5 sub_points

## Task Commits

Each task was committed atomically:

1. **Task 1: Create interval-rules.md** - `89854c2` (feat)
2. **Task 2: Create sub-points-rules.md** - `9b7ffee` (feat)

## Files Created/Modified

- `00. learning/learning-behavior-system/interval-rules.md` - Dynamic interval lookup table (consecutive_success 0–9+ → 1–90 days), result-specific calculation rules, graduation/regression conditions with thresholds, two worked examples
- `00. learning/learning-behavior-system/sub-points-rules.md` - sub_points YAML schema with id/desc/status/last_reviewed fields, review_sessions append-only log schema, covered/uncovered status update rules, backward compatibility notes, full Card 017 worked example

## Decisions Made

- Graduation requires both consecutive_success >= 8 AND last actual interval >= 30 days — count alone is insufficient (a card could get lucky with short intervals)
- Regression threshold is 3 consecutive failures (not 8 like Anki leech) because this system tracks consecutive failures, which is a stronger signal than cumulative
- ok result caps interval at min(lookup, last_interval × 1.3) to prevent ok-streaks from inflating intervals too fast
- sub_points uncovered status is preserved (not reset) — absence of assessment is not evidence of forgetting

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Plan 02 (SKILL.md schema extension) can now reference interval-rules.md and sub-points-rules.md as authoritative sources
- Plan 03 (YAML card migration) has a clear spec for adding sub_points to existing cards
- Both rule documents are self-contained: any reader can compute next_review or update sub_point status without consulting RESEARCH.md

## Self-Check: PASSED

- FOUND: `00. learning/learning-behavior-system/interval-rules.md`
- FOUND: `00. learning/learning-behavior-system/sub-points-rules.md`
- FOUND: `.planning/phases/07-yaml-schema-extension/07-01-SUMMARY.md`
- FOUND: commit 89854c2 (Task 1 — interval-rules.md)
- FOUND: commit 9b7ffee (Task 2 — sub-points-rules.md)

---
*Phase: 07-yaml-schema-extension*
*Completed: 2026-03-31*
