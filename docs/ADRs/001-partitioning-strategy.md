# ADR-001: Partitioning Strategy

## Status
Accepted

## Context
Jobs and event tables will grow unbounded. Queries must remain fast without DBA intervention.

## Decision
Use PostgreSQL RANGE partitioning by collected_at (monthly). Partitions are created proactively by `cronos-partition-create`.

## Consequences
- Queries with time-range filters scan only relevant partitions
- Old partitions can be dropped for retention without DELETE overhead
- Partition creation is automated (no manual DBA)
