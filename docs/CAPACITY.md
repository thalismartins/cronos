# Capacity Planning

## Scale Targets
- Up to 200k jobs/day
- 22 master servers
- 90-day retention (~18M jobs rows)
- 3 concurrent dashboard users

## Storage
- Jobs table: ~200 bytes/row → ~3.6 GB for 18M rows
- Indexes: ~1.5x data size → ~5.4 GB
- Total estimate: ~10 GB for 90-day retention

## Performance
- All KPI endpoints: p95 < 300ms with rollups
- Job list with keyset pagination: p95 < 200ms
- Partitioning: monthly ranges keep index size manageable

## When to Scale
- >500k jobs/day → increase API replicas
- >50M jobs → reduce retention or add Redis cache
