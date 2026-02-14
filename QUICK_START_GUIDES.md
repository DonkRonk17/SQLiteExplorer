# SQLiteExplorer - Quick Start Guides

## About These Guides

Each Team Brain agent has a **5-minute quick-start guide** tailored to their role and workflows.

**Choose your guide:**
- [Forge (Orchestrator)](#forge-quick-start)
- [Atlas (Executor)](#atlas-quick-start)
- [Clio (Linux Agent)](#clio-quick-start)
- [Nexus (Multi-Platform)](#nexus-quick-start)
- [Bolt (Free Executor)](#bolt-quick-start)
- [Logan (Human)](#logan-quick-start)

---

## FORGE QUICK START

**Role:** Orchestrator / Reviewer
**Time:** 5 minutes
**Goal:** Learn to use SQLiteExplorer for database review and verification

### Step 1: Installation Check
```bash
python sqliteexplorer.py --version
# Expected: SQLiteExplorer 1.0.0
```

### Step 2: First Use - Database Review
```bash
# Review VitalHeart database structure
python sqliteexplorer.py info "C:\Users\logan\.teambrain\heartbeat.db"

# Check all tables
python sqliteexplorer.py tables "C:\Users\logan\.teambrain\heartbeat.db"

# Verify schema matches spec
python sqliteexplorer.py schema "C:\Users\logan\.teambrain\heartbeat.db" heartbeats
```

### Step 3: Code Review Integration
```python
# Verify database after agent build
from sqliteexplorer import SQLiteExplorer

with SQLiteExplorer("heartbeat.db") as db:
    # Check schema integrity
    schema = db.get_schema("heartbeats")
    cols = [c["name"] for c in schema[0]["columns"]]
    print(f"Columns: {cols}")

    # Check data quality
    stats = db.get_stats("heartbeats")
    for s in stats:
        if s["null_count"] > 0:
            print(f"[!] {s['column']}: {s['null_count']} NULLs ({s['null_pct']})")
```

### Step 4: Common Forge Commands
```bash
# Compare dev vs production schema
python sqliteexplorer.py diff dev.db prod.db

# Export data for review
python sqliteexplorer.py export db table --format json -o review.json

# Search for specific data
python sqliteexplorer.py search db "LUMINA"
```

### Next Steps for Forge
1. Read [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md) - Forge section
2. Try [EXAMPLES.md](EXAMPLES.md) - Examples 9, 12
3. Add to code review checklist: verify DB schema after builds

---

## ATLAS QUICK START

**Role:** Executor / Builder
**Time:** 5 minutes
**Goal:** Learn to use SQLiteExplorer for debugging and development

### Step 1: Installation Check
```bash
python -c "from sqliteexplorer import SQLiteExplorer; print('OK')"
# Expected: OK
```

### Step 2: First Use - Debug a Database
```bash
# Quick overview of any database
python sqliteexplorer.py info mydata.db

# Browse data during development
python sqliteexplorer.py browse mydata.db users --limit 5

# Check column stats for data quality
python sqliteexplorer.py stats mydata.db users
```

### Step 3: Build Workflow Integration
```python
# During tool development
from sqliteexplorer import SQLiteExplorer

# Inspect test database
with SQLiteExplorer("test_output.db") as db:
    tables = db.get_tables()
    for t in tables:
        print(f"  {t['name']}: {t['row_count']} rows, {t['column_count']} cols")

    # Export test fixtures
    db.export_table("test_data", fmt="json", output="fixtures.json")
```

### Step 4: Common Atlas Commands
```bash
# Debug: what's in this database?
python sqliteexplorer.py tables db && python sqliteexplorer.py browse db tablename --limit 5

# Export for test fixtures
python sqliteexplorer.py export db tablename --format json -o fixtures.json

# Size check after builds
python sqliteexplorer.py size db
```

### Next Steps for Atlas
1. Use during every tool build that creates SQLite databases
2. Add to debugging toolkit alongside LogHunter
3. Export test data for regression tests

---

## CLIO QUICK START

**Role:** Linux / Ubuntu Agent
**Time:** 5 minutes
**Goal:** Learn to use SQLiteExplorer in Linux environment

### Step 1: Linux Installation
```bash
git clone https://github.com/DonkRonk17/SQLiteExplorer.git
cd SQLiteExplorer
python3 sqliteexplorer.py --version
```

### Step 2: First Use - Linux Database Inspection
```bash
# Inspect any SQLite database
python3 sqliteexplorer.py info /var/lib/myapp/data.db

# List tables
python3 sqliteexplorer.py tables /var/lib/myapp/data.db

# Browse data
python3 sqliteexplorer.py browse /var/lib/myapp/data.db users --limit 10
```

### Step 3: Batch Analysis
```bash
# Inspect multiple databases
for db in /var/lib/myapp/*.db; do
    echo "=== $db ==="
    python3 sqliteexplorer.py tables "$db"
done

# Export all databases to JSON
for db in /var/lib/myapp/*.db; do
    name=$(basename "$db" .db)
    python3 sqliteexplorer.py export "$db" main_table --format json -o "${name}.json"
done
```

### Step 4: Common Clio Commands
```bash
# Quick health check
python3 sqliteexplorer.py info db && python3 sqliteexplorer.py size db

# Search across databases
python3 sqliteexplorer.py search db "error" --limit 20

# Optimize storage
python3 sqliteexplorer.py vacuum db --confirm
```

### Next Steps for Clio
1. Add to system monitoring scripts
2. Use with BatchRunner for parallel database analysis
3. Create cron jobs for daily database health checks

---

## NEXUS QUICK START

**Role:** Multi-Platform Agent
**Time:** 5 minutes
**Goal:** Learn cross-platform usage of SQLiteExplorer

### Step 1: Platform Detection
```python
import platform
from sqliteexplorer import SQLiteExplorer

print(f"Platform: {platform.system()}")
# SQLiteExplorer works identically on all platforms
```

### Step 2: Cross-Platform Usage
```python
from pathlib import Path
from sqliteexplorer import SQLiteExplorer

# Works on Windows, Linux, macOS
db_path = Path.home() / ".teambrain" / "heartbeat.db"
if db_path.exists():
    with SQLiteExplorer(str(db_path)) as db:
        info = db.get_info()
        print(f"Tables: {info['table_count']}, Size: {info['file_size_display']}")
```

### Step 3: Platform-Specific Considerations

**Windows:**
- Paths use backslashes but pathlib handles this
- Console encoding handled automatically (ASCII-safe output)

**Linux:**
- Use python3 explicitly
- File permissions may affect database access

**macOS:**
- Works identically to Linux
- Use python3

### Next Steps for Nexus
1. Test on all 3 platforms
2. Verify path handling with different database locations
3. Report any platform-specific issues

---

## BOLT QUICK START

**Role:** Free Executor (Cline + Grok)
**Time:** 5 minutes
**Goal:** Learn to use SQLiteExplorer without API costs

### Step 1: Verify Free Access
```bash
# No API key required! No pip install needed!
python sqliteexplorer.py --version
# Expected: SQLiteExplorer 1.0.0
```

### Step 2: First Use
```bash
# Quick database check - zero cost
python sqliteexplorer.py tables mydata.db
python sqliteexplorer.py browse mydata.db main_table --limit 5
```

### Step 3: Batch Operations
```bash
# Process multiple databases efficiently
python sqliteexplorer.py info db1.db
python sqliteexplorer.py info db2.db
python sqliteexplorer.py diff db1.db db2.db
```

### Step 4: Cost-Free Analysis
```bash
# Full analysis pipeline - zero API calls
python sqliteexplorer.py info db
python sqliteexplorer.py tables db
python sqliteexplorer.py stats db main_table
python sqliteexplorer.py search db "keyword"
python sqliteexplorer.py export db main_table --format json -o export.json
```

### Next Steps for Bolt
1. Add to Cline workflows for database debugging
2. Use for repetitive database inspections
3. Report issues via Synapse

---

## LOGAN QUICK START

**Role:** Human / Team Lead
**Time:** 3 minutes
**Goal:** Quick database inspection from command line

### Most Common Commands
```bash
# What's in this database?
python sqliteexplorer.py info heartbeat.db

# Show me the tables
python sqliteexplorer.py tables heartbeat.db

# Show me the data
python sqliteexplorer.py browse heartbeat.db heartbeats --limit 10

# Find something
python sqliteexplorer.py search heartbeat.db "LUMINA"

# Export for analysis
python sqliteexplorer.py export heartbeat.db heartbeats --format json -o heartbeats.json
```

### Pro Tips
1. Use `tables` first for a quick overview
2. Use `search` when you don't know which table has the data
3. Use `--format json` for machine-readable output
4. Use `stats` to check data quality

---

## Additional Resources

**For All Agents:**
- Full Documentation: [README.md](README.md)
- Examples: [EXAMPLES.md](EXAMPLES.md)
- Integration Plan: [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md)
- Cheat Sheet: [CHEAT_SHEET.txt](CHEAT_SHEET.txt)

**Support:**
- GitHub Issues: https://github.com/DonkRonk17/SQLiteExplorer/issues
- Synapse: Post in THE_SYNAPSE/active/

---

**Last Updated:** February 14, 2026
**Maintained By:** ATLAS (Team Brain)
