# Milestone v1.1 State — 学习系统基建改造

## Current Position

Phase: Not started
Plan: —
Status: Defining requirements
Last activity: 2026-03-31 — Milestone v1.1 started

## Notes

- 现有 YAML cards 017~027 均在 active，028 在 pool（未学习）
- 三个核心问题已明确：毕业机制缺失、子知识点无追踪、单点复习无法验证全局
- GSD 工作流对接是第四个改造目标
- 存量复习（每日队列）继续正常运行，改造与复习并行

## Accumulated Context

- consecutive_success / consecutive_failures 为独立累计规则（已有 memory 记录）
- ok = success，不重置 success 计数
- 现有 level 1/2 的升级机制较粗糙，需要替换为动态间隔
