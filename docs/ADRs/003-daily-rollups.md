# ADR-003: Daily Rollups for KPI Performance

## Status
Accepted

## Context
Dashboard KPI queries scanning the raw `jobs` table become slow as it grows (millions of rows).

## Decision
Build a daily rollup table (`job_kpi_daily`) with pre-aggregated counts. KPI queries read rollups first, with a fallback to the raw table.

## Consequences
- KPI queries are O(days) instead of O(jobs)
- Rollups are rebuilt incrementally by `cronos-rollup`
- Raw data is still available for drill-down
