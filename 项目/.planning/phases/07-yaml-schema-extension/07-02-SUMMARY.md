---
phase: 07-yaml-schema-extension
plan: 02
subsystem: learning-behavior-system
tags: [yaml-schema, sub-points, review-sessions, skill-doc]
dependency_graph:
  requires: [07-01]
  provides: [sub_points-fields-in-batch1-cards, SKILL.md-v1.1-docs]
  affects: [learning-behavior-system/states/active/, learning-behavior-system/SKILL.md]
tech_stack:
  added: []
  patterns: [append-only-yaml-fields, status-derived-from-weak_points]
key_files:
  created: []
  modified:
    - 00. learning/learning-behavior-system/states/active/009-MediaCodec编解码原理.yaml
    - 00. learning/learning-behavior-system/states/active/010-音视频基础概念.yaml
    - 00. learning/learning-behavior-system/states/active/011-音视频同步原理.yaml
    - 00. learning/learning-behavior-system/states/active/014-音视频重封装MP4.yaml
    - 00. learning/learning-behavior-system/states/active/017-OpenGL-ES零拷贝图形管线.yaml
    - 00. learning/learning-behavior-system/states/active/018-OpenGL-ES渲染管线基础.yaml
    - 00. learning/learning-behavior-system/states/active/019-GLSL与Android渲染架构.yaml
    - 00. learning/learning-behavior-system/SKILL.md
decisions:
  - "sub_point statuses derived from last_assessment.weak_points: mentioned weak → weak/ok, not mentioned → good"
  - "Card 017 review_sessions only covers sp1/sp2/sp4/sp5 (sp3 not covered per research example)"
  - "Both status enum instances in SKILL.md updated to include archived (knowledge-point and project types)"
metrics:
  duration: 4m51s
  completed_date: 2026-03-31
  tasks_completed: 2
  files_modified: 8
---

# Phase 07 Plan 02: Add sub_points and review_sessions to First Batch of Cards — Summary

**One-liner:** Added sub_points (3-6 items per card, status from weak_points) and review_sessions (initial historical entry) to 7 active YAML cards, then updated SKILL.md with all v1.1 field definitions, archived status, dynamic interval rules subsection, and sub-points section with links to both rule documents.

## Tasks Completed

| Task | Name | Commit | Key Files |
|------|------|--------|-----------|
| 1 | Add sub_points and review_sessions to cards 009, 010, 011, 014, 017, 018, 019 | c28fb14 | 7 YAML card files |
| 2 | Update SKILL.md with new field definitions and rule document references | 4f842a9 | SKILL.md |

## What Was Built

### Task 1: 7 YAML Cards Updated

Each card received two new appended sections:

**sub_points** — 3-8 items per card, each with id, desc, status, last_reviewed:
- Card 009 (MediaCodec): 4 sub_points — sp4=weak (MediaExtractor/Muxer confusion per weak_points)
- Card 010 (音视频基础概念): 5 sub_points — all good (no weak_points recorded)
- Card 011 (音视频同步原理): 5 sub_points — sp2=ok (PTS diff expression weakness)
- Card 014 (音视频重封装MP4): 5 sub_points — sp3/sp4/sp5=ok (MP4 box details and advance() weakness)
- Card 017 (OpenGL ES零拷贝): 5 sub_points exactly matching research example — sp2=ok, sp3=weak
- Card 018 (OpenGL ES渲染管线): 5 sub_points — sp2=ok (coordinate origin confusion)
- Card 019 (GLSL与Android渲染架构): 6 sub_points — sp1/sp2=ok (uniform variable confusion)

**review_sessions** — one initial historical entry per card based on last_assessment:
- date from last_assessment.date
- covered_sub_points lists all sub_points (initial migration entry)
- result and score from last_assessment

Card 017 exception: review_sessions covers only sp1/sp2/sp4/sp5 (sp3 was not covered in the last session per research example — sp3=weak because it wasn't reviewed well).

No existing YAML fields were modified (all ids, titles, statuses, consecutive_success values confirmed unchanged).

### Task 2: SKILL.md Updated

Five specific edits applied:
1. **YAML field definition**: Added sub_points and review_sessions example blocks after suggested_interval_days in the knowledge-point type section
2. **Status enum**: Added `archived` to both knowledge-point and project type status fields; added note explaining archived behavior with reference to interval-rules.md
3. **复习周期规则 section**: Added "动态间隔规则（v1.1 新增）" subsection at the top with link to interval-rules.md and 5 core change bullet points
4. **TOC and new section**: Added `子知识点追踪规则` to table of contents; added full `## 子知识点追踪规则` section before 注意事项 with link to sub-points-rules.md and 4 core requirement bullet points
5. **目录结构**: Added `interval-rules.md` and `sub-points-rules.md` lines to the directory listing

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None. All 7 cards have real sub_points derived from their actual notes and weak_points content. SKILL.md documents complete field definitions referencing the rule documents created in Plan 01.

## Self-Check: PASSED

Files confirmed present:
- `00. learning/learning-behavior-system/states/active/009-MediaCodec编解码原理.yaml` — FOUND
- `00. learning/learning-behavior-system/states/active/017-OpenGL-ES零拷贝图形管线.yaml` — FOUND
- `00. learning/learning-behavior-system/SKILL.md` — FOUND

Commits confirmed:
- `c28fb14` — FOUND (feat(07-02): add sub_points and review_sessions to 7 active YAML cards)
- `4f842a9` — FOUND (feat(07-02): update SKILL.md with v1.1 schema additions)

Acceptance criteria verified:
- All 7 cards contain sub_points: field — PASS
- All 7 cards contain review_sessions: field with at least one entry — PASS
- Card 017 has exactly 5 sub_points — PASS
- Card 009 has sp4 with status: weak — PASS
- SKILL.md contains sub_points, review_sessions, interval-rules.md, sub-points-rules.md, archived — PASS
- SKILL.md contains 动态間隔規則（v1.1 新增）subsection — PASS
- SKILL.md contains 子知識點追踪規則 section — PASS
- No existing card fields modified (card 009 consecutive_success still 6) — PASS
