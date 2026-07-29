# ADR-002: Plugin-Based Collector Architecture

## Status
Accepted

## Context
Cronos must support multiple data sources (NetBackup, Veeam, SNMP, etc.) without hardcoding each.

## Decision
Collectors implement a common `Collector` ABC with async `collect()` generator. Discovery scans `collectors/` directory and pip entrypoints (`cronos_collector_*`).

## Consequences
- New data sources can be added without modifying core
- Config is YAML-based, validated against JSON Schema
- Each collector declares its capabilities and config schema
