# Fleet Telemetry System

An early-stage Python telemetry and data engineering project for generating, validating, and eventually processing fleet telemetry data through a production-oriented pipeline.

## Current State

The repository currently includes:

- Synthetic fleet telemetry generation with Faker
- Pydantic models for telemetry validation
- JSON batch output for generated events
- A minimal DuckDB initialization check

The project is intentionally being developed incrementally. Features listed below under **Roadmap** are planned work and should not be considered implemented yet.

## Current Architecture

```text
Synthetic telemetry generator
        |
        v
Pydantic validation
        |
        v
JSON batch output

DuckDB is currently used only for an initial database connectivity/setup check.
```

## Technologies Currently Used

- Python
- Pydantic
- Faker
- DuckDB

## Project Goals

The goal is to evolve this repository into a defensible software/data engineering project that demonstrates practical work with ingestion, relational databases, data quality, testing, failure handling, observability, and maintainable Python structure.

## Roadmap

Planned milestones include:

1. Define a relational telemetry schema and persist validated events to PostgreSQL
2. Build a repeatable ingestion workflow with duplicate handling and safe reruns
3. Add unit and integration tests with pytest
4. Introduce structured logging and clearer error handling
5. Add transformation/modeling for analytics-oriented queries
6. Containerize local services with Docker and Docker Compose
7. Add a small API/query layer
8. Add CI for automated tests and quality checks
9. Add orchestration or cloud deployment only if it solves a real project requirement

## Repository Structure

```text
.
├── data/                  # Local/generated data (ignored by Git where appropriate)
├── src/
│   ├── generators/        # Synthetic telemetry generation
│   ├── models/            # Pydantic telemetry models
│   └── db_check.py        # Initial DuckDB setup check
├── .gitignore
├── requirements.txt
└── README.md
```

## Running the Current Code

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Generate a sample telemetry batch:

```bash
python -m src.generators.fleet_generator
```

Run the DuckDB initialization check:

```bash
python -m src.db_check
```

## Status

**In active development.** The current implementation is a project foundation, not a finished production system.
