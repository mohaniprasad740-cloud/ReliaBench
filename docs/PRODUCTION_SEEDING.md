# Reliabench Production Seeding & Data Isolation Guide

## 1. Automated Cold Start Bootstrap

When Reliabench boots in production (such as on Vercel Serverless Functions or containerized cloud instances), it runs `auto_seed_if_empty(engine)` inside `backend/app/main.py`:

```python
# app/main.py
try:
    Base.metadata.create_all(bind=engine)
    run_additive_migrations(engine)
    import sys
    if "pytest" not in sys.modules and not os.getenv("TESTING"):
        from app.services.demo_seed import auto_seed_if_empty
        auto_seed_if_empty(engine)
except Exception as e:
    pass
```

### Bootstrap Logic:
1. Verifies database connectivity.
2. Runs additive migrations to ensure all nullable columns (`source_mode`, `is_demo`, etc.) exist.
3. Checks if any demo agents exist (`db.query(Agent).filter(Agent.is_demo == True).count() == 0`).
4. If empty, populates the canonical dataset idempotently.
5. In test environments (`pytest`), auto-seeding is suppressed to keep test suites clean.

---

## 2. Deterministic Idempotency Architecture

Every canonical demo record uses deterministic UUIDs generated via `uuid.uuid5(uuid.NAMESPACE_DNS, key)`:

```python
def demo_id(key: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"reliabench.demo.{key}"))
```

### Benefits:
- Running `seed_demo_data()` repeatedly will never produce duplicate records.
- Cross-references between Agents, BenchmarkTasks, Experiments, Runs, Trials, Trajectories, and Telemetry Events remain mathematically and relationally exact.

---

## 3. Data Isolation & Safety Guarantees

Reliabench strictly partitions demo data from real production data:

| Entity Type | User Records | Canonical Demo Records |
| :--- | :--- | :--- |
| `is_demo` Flag | `False` | `True` |
| `source_mode` | `"REAL_EXECUTION"` | `"SIMULATOR"` |
| Reset Impact | **Preserved 100%** | Cleared & Re-seeded |

```python
def clean_existing_demo_records(db: Session) -> int:
    """Purges ONLY records with is_demo=True, strictly preserving real user experiments."""
    demo_exps = db.query(Experiment).filter(Experiment.is_demo == True).all()
    for exp in demo_exps:
        db.delete(exp)
    db.query(BenchmarkTask).filter(BenchmarkTask.is_demo == True).delete(synchronize_session=False)
    db.query(Agent).filter(Agent.is_demo == True).delete(synchronize_session=False)
    db.commit()
```

---

## 4. Operational Endpoints & CLI Commands

### REST Endpoints
- `GET /api/v1/demo/status`: Returns current demo status, entity counts, and canonical agent roster.
- `POST /api/v1/demo/seed`: Triggers idempotent seeding.
- `POST /api/v1/demo/reset`: Safely clears demo entities and re-populates baseline dataset.

### CLI Management
```bash
# Seed demo environment idempotently
python -m app.cli seed-demo

# Force clean and re-seed from scratch
python -m app.cli reset-demo

# Purge demo synthetic data dry-run
python -m app.cli clean-demo-data --dry-run

# Purge demo synthetic data completely
python -m app.cli clean-demo-data
```

