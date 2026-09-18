# Architecture Decisions

## ADR-001 — One JSON document
The V1/V2 requirement is one JSON file. The root object contains entity collection keys. This keeps storage simple while exercising persistence abstraction.

## ADR-002 — Generic repository
CRUD that is structurally identical is implemented once. Specialized repositories exist only for domain-specific queries.

## ADR-003 — Unit of Work
Feature operations that update multiple collections commit once to the JSON file.

## ADR-004 — Derived course progress
Completed hours, remaining hours and status are derived from `total_hours` plus daily reports.

## ADR-005 — Role versus training method
Role defines the broad authorization category. Training method refines trainer behavior. They are not the same concept.

## ADR-006 — No runtime frameworks
The project intentionally uses the standard library at runtime. This keeps the one-day delivery focused on architecture and engineering practices.
