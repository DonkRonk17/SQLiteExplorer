# SQLiteExplorer - Integration Examples

## Integration Philosophy

SQLiteExplorer is designed to work seamlessly with other Team Brain tools. This document provides **copy-paste-ready code examples** for common integration patterns.

---

## Table of Contents

1. [Pattern 1: SQLiteExplorer + AgentHeartbeat](#pattern-1-sqliteexplorer--agentheartbeat)
2. [Pattern 2: SQLiteExplorer + SynapseLink](#pattern-2-sqliteexplorer--synapselink)
3. [Pattern 3: SQLiteExplorer + TaskQueuePro](#pattern-3-sqliteexplorer--taskqueuepro)
4. [Pattern 4: SQLiteExplorer + MemoryBridge](#pattern-4-sqliteexplorer--memorybridge)
5. [Pattern 5: SQLiteExplorer + SessionReplay](#pattern-5-sqliteexplorer--sessionreplay)
6. [Pattern 6: SQLiteExplorer + ContextCompressor](#pattern-6-sqliteexplorer--contextcompressor)
7. [Pattern 7: SQLiteExplorer + ConfigManager](#pattern-7-sqliteexplorer--configmanager)
8. [Pattern 8: SQLiteExplorer + HashGuard](#pattern-8-sqliteexplorer--hashguard)
9. [Pattern 9: SQLiteExplorer + BatchRunner](#pattern-9-sqliteexplorer--batchrunner)
10. [Pattern 10: Full Team Brain Database Health Stack](#pattern-10-full-team-brain-database-health-stack)

---

## Pattern 1: SQLiteExplorer + AgentHeartbeat

**Use Case:** Monitor agent vital signs by inspecting the heartbeat database

**Why:** Understand agent activity patterns without writing raw SQL

**Code:**

```python
from sqliteexplorer import SQLiteExplorer
from pathlib import Path

# Find the heartbeat database
db_path = Path.home() / ".teambrain" / "heartbeat.db"

with SQLiteExplorer(str(db_path)) as db:
    # Get latest heartbeats
    result = db.query(
        "SELECT agent_name, status, mood, current_task "
        "FROM heartbeats ORDER BY id DESC LIMIT 10"
    )

    print("Recent Agent Activity:")
    for row in result["rows"]:
        agent, status, mood, task = row[0], row[1], row[2], row[3]
        task_short = (task[:50] + "...") if task and len(task) > 50 else task
        print(f"  {agent}: {status} ({mood}) - {task_short}")

    # Check for agents that haven't reported recently
    stats = db.get_stats("heartbeats")
    agent_stat = next(s for s in stats if s["column"] == "agent_name")
    print(f"\nTotal heartbeats: {agent_stat['non_null']}")
    print(f"Unique agents: {agent_stat['distinct']}")
```

**Result:** Instant visibility into agent health without raw SQL

---

## Pattern 2: SQLiteExplorer + SynapseLink

**Use Case:** Automated database health reports to Team Brain

**Why:** Keep team informed of database status automatically

**Code:**

```python
from synapselink import quick_send
from sqliteexplorer import SQLiteExplorer

def report_db_health(db_path, db_name):
    """Generate and send database health report."""
    with SQLiteExplorer(db_path) as db:
        info = db.get_info()
        tables = db.get_tables()
        size = db.get_size()

        report_lines = [
            f"Database: {db_name}",
            f"Size: {info['file_size_display']}",
            f"Tables: {info['table_count']}",
            "",
        ]

        for t in tables:
            report_lines.append(f"  {t['name']}: {t['row_count']} rows")

        if size["free_pages"] > 0:
            report_lines.append(f"\n[!] Free space: {size['free_space_display']} - vacuum recommended")

        report = "\n".join(report_lines)

    quick_send("TEAM", f"DB Health: {db_name}", report, priority="NORMAL")
    return report

# Run health check
report_db_health("heartbeat.db", "AgentHeartbeat")
```

**Result:** Team receives formatted database health updates

---

## Pattern 3: SQLiteExplorer + TaskQueuePro

**Use Case:** Schedule and track database inspection tasks

**Why:** Systematic database monitoring with task tracking

**Code:**

```python
from taskqueuepro import TaskQueuePro
from sqliteexplorer import SQLiteExplorer

queue = TaskQueuePro()

# Create inspection task
task_id = queue.create_task(
    title="Daily heartbeat.db inspection",
    agent="ATLAS",
    priority=2,
    metadata={"tool": "SQLiteExplorer", "database": "heartbeat.db"}
)

queue.start_task(task_id)

try:
    with SQLiteExplorer("heartbeat.db") as db:
        info = db.get_info()
        tables = db.get_tables()
        total_rows = sum(t["row_count"] for t in tables)

    queue.complete_task(task_id, result={
        "tables": info["table_count"],
        "total_rows": total_rows,
        "size": info["file_size_display"],
        "status": "healthy"
    })

except Exception as e:
    queue.fail_task(task_id, error=str(e))
```

**Result:** Database inspections tracked in centralized task system

---

## Pattern 4: SQLiteExplorer + MemoryBridge

**Use Case:** Persist database analysis results for historical tracking

**Why:** Track database growth and health over time

**Code:**

```python
from memorybridge import MemoryBridge
from sqliteexplorer import SQLiteExplorer
from datetime import datetime

memory = MemoryBridge()

with SQLiteExplorer("heartbeat.db") as db:
    info = db.get_info()
    tables = db.get_tables()

# Load history
history = memory.get("db_health_history", default=[])

# Add current snapshot
history.append({
    "timestamp": datetime.now().isoformat(),
    "file_size": info["file_size"],
    "table_count": info["table_count"],
    "tables": {t["name"]: t["row_count"] for t in tables},
})

# Keep last 30 snapshots
history = history[-30:]

memory.set("db_health_history", history)
memory.sync()

print(f"Recorded snapshot #{len(history)}")
```

**Result:** Historical database health data persisted in Memory Core

---

## Pattern 5: SQLiteExplorer + SessionReplay

**Use Case:** Record database operations for debugging

**Why:** Replay database inspection steps when issues occur

**Code:**

```python
from sessionreplay import SessionReplay
from sqliteexplorer import SQLiteExplorer

replay = SessionReplay()
session_id = replay.start_session("ATLAS", task="DB investigation")

with SQLiteExplorer("heartbeat.db") as db:
    # Log each step
    replay.log_input(session_id, "Getting database info")
    info = db.get_info()
    replay.log_output(session_id, f"Tables: {info['table_count']}, Size: {info['file_size_display']}")

    replay.log_input(session_id, "Searching for LUMINA")
    matches = db.search("LUMINA")
    replay.log_output(session_id, f"Found {len(matches)} matches")

    if not matches:
        replay.log_error(session_id, "No LUMINA heartbeats found!")
        replay.end_session(session_id, status="INVESTIGATION_NEEDED")
    else:
        replay.end_session(session_id, status="COMPLETED")
```

**Result:** Full replay trail of database investigation steps

---

## Pattern 6: SQLiteExplorer + ContextCompressor

**Use Case:** Compress large query outputs before sharing

**Why:** Save tokens when sharing database results in conversations

**Code:**

```python
from contextcompressor import ContextCompressor
from sqliteexplorer import SQLiteExplorer

compressor = ContextCompressor()

with SQLiteExplorer("large_events.db") as db:
    # Get full export
    full_json = db.export_table("events", fmt="json")
    original_size = len(full_json)

    # Compress for sharing
    compressed = compressor.compress_text(
        full_json,
        query="error events from today",
        method="summary"
    )

    print(f"Original: {original_size} chars")
    print(f"Compressed: {len(compressed.compressed_text)} chars")
    print(f"Savings: {compressed.estimated_token_savings} tokens")
```

**Result:** 70-90% reduction in shared database output size

---

## Pattern 7: SQLiteExplorer + ConfigManager

**Use Case:** Centralized database path configuration

**Why:** Share database locations across tools and agents

**Code:**

```python
from configmanager import ConfigManager
from sqliteexplorer import SQLiteExplorer

config = ConfigManager()

# Store database paths in shared config
databases = config.get("team_databases", {
    "heartbeat": "~/.teambrain/heartbeat.db",
    "sessions": "~/.teambrain/sessions.db",
    "notes": "~/.teambrain/notes.db",
})

# Inspect all configured databases
for name, path in databases.items():
    try:
        with SQLiteExplorer(path) as db:
            info = db.get_info()
            print(f"[OK] {name}: {info['table_count']} tables, {info['file_size_display']}")
    except FileNotFoundError:
        print(f"[X] {name}: not found at {path}")
```

**Result:** Centralized database discovery and health checking

---

## Pattern 8: SQLiteExplorer + HashGuard

**Use Case:** Verify database integrity before inspection

**Why:** Detect corruption or unauthorized changes

**Code:**

```python
from hashguard import HashGuard
from sqliteexplorer import SQLiteExplorer

guard = HashGuard()

# Verify integrity first
db_path = "heartbeat.db"
integrity_ok = guard.verify(db_path)

if integrity_ok:
    with SQLiteExplorer(db_path) as db:
        info = db.get_info()
        print(f"[OK] Integrity verified, inspecting: {info['table_count']} tables")
else:
    print("[X] Database integrity check FAILED!")
    print("    Database may be corrupted or modified.")
    print("    Restore from backup before proceeding.")
```

**Result:** Safe database inspection with pre-flight integrity check

---

## Pattern 9: SQLiteExplorer + BatchRunner

**Use Case:** Inspect multiple databases in parallel

**Why:** Scale database monitoring across the Team Brain ecosystem

**Code:**

```python
from batchrunner import BatchRunner
import json

runner = BatchRunner()

# Define database inspection commands
databases = [
    ("heartbeat", "heartbeat.db"),
    ("sessions", "sessions.db"),
    ("notes", "notes.db"),
]

for name, db_path in databases:
    runner.add(
        name,
        f'python sqliteexplorer.py info "{db_path}" --format json'
    )

# Run all inspections in parallel
results = runner.run_parallel()

# Process results
for name, result in results.items():
    if result.success:
        info = json.loads(result.stdout)
        print(f"[OK] {name}: {info['table_count']} tables, {info['file_size_display']}")
    else:
        print(f"[X] {name}: {result.stderr}")
```

**Result:** All databases inspected simultaneously, saving time

---

## Pattern 10: Full Team Brain Database Health Stack

**Use Case:** Complete database monitoring workflow

**Why:** Production-grade database health monitoring

**Code:**

```python
from sqliteexplorer import SQLiteExplorer
from synapselink import quick_send
from datetime import datetime

def full_health_check(db_path, db_name):
    """Complete database health check with Team Brain integration."""

    report = {
        "database": db_name,
        "timestamp": datetime.now().isoformat(),
        "status": "healthy",
        "warnings": [],
    }

    try:
        with SQLiteExplorer(db_path) as db:
            # 1. Basic info
            info = db.get_info()
            report["tables"] = info["table_count"]
            report["size"] = info["file_size_display"]

            # 2. Table health
            tables = db.get_tables()
            for t in tables:
                if t["row_count"] == 0:
                    report["warnings"].append(f"Empty table: {t['name']}")

            # 3. Data quality
            for t in tables:
                if t["row_count"] > 0:
                    stats = db.get_stats(t["name"])
                    for s in stats:
                        null_pct = (s["null_count"] / s["total_rows"] * 100) if s["total_rows"] > 0 else 0
                        if null_pct > 50:
                            report["warnings"].append(
                                f"{t['name']}.{s['column']}: {null_pct:.0f}% NULL"
                            )

            # 4. Size health
            size = db.get_size()
            if size["free_pages"] > 0:
                report["warnings"].append(
                    f"Free space: {size['free_space_display']} (vacuum recommended)"
                )

    except Exception as e:
        report["status"] = "error"
        report["error"] = str(e)

    # Set status based on warnings
    if report["warnings"]:
        report["status"] = "warnings"

    # Send report
    priority = "HIGH" if report["status"] == "error" else "NORMAL"
    msg = f"Status: {report['status']}\nSize: {report.get('size', 'N/A')}\nTables: {report.get('tables', 'N/A')}"
    if report["warnings"]:
        msg += f"\nWarnings: {len(report['warnings'])}"
        for w in report["warnings"][:5]:
            msg += f"\n  - {w}"

    quick_send("TEAM", f"DB Health: {db_name}", msg, priority=priority)

    return report


# Run for all Team Brain databases
databases = {
    "heartbeat": "~/.teambrain/heartbeat.db",
}

for name, path in databases.items():
    report = full_health_check(path, name)
    print(f"{name}: {report['status']} ({len(report['warnings'])} warnings)")
```

**Result:** Fully instrumented, automated database health monitoring

---

## Recommended Integration Priority

**Week 1 (Essential):**
1. AgentHeartbeat - Inspect vital signs database
2. SynapseLink - Report database health to team
3. SessionReplay - Record inspection operations

**Week 2 (Productivity):**
4. TaskQueuePro - Schedule regular inspections
5. MemoryBridge - Track database health over time
6. ConfigManager - Centralize database paths

**Week 3 (Advanced):**
7. ContextCompressor - Compress large outputs
8. HashGuard - Pre-flight integrity checks
9. BatchRunner - Parallel multi-database analysis
10. Full stack monitoring

---

## Troubleshooting Integrations

**Import Errors:**
```python
import sys
from pathlib import Path
sys.path.append(str(Path.home() / "OneDrive/Documents/AutoProjects"))
from sqliteexplorer import SQLiteExplorer
```

**Database Path Issues:**
```python
from pathlib import Path
# Always resolve paths before passing
db_path = Path("relative/path.db").resolve()
db = SQLiteExplorer(str(db_path))
```

---

**Last Updated:** February 14, 2026
**Maintained By:** ATLAS (Team Brain)
