# SQLiteExplorer - Integration Plan

## Integration Goals

This document outlines how SQLiteExplorer integrates with:
1. Team Brain agents (Forge, Atlas, Clio, Nexus, Bolt)
2. Existing Team Brain tools
3. BCH (Beacon Command Hub)
4. Logan's workflows

---

## BCH Integration

### Overview
SQLiteExplorer can be invoked from BCH as a diagnostic tool for any SQLite database in the Team Brain ecosystem.

### BCH Commands
```
@sqliteexplorer info <db_path>
@sqliteexplorer tables <db_path>
@sqliteexplorer search <db_path> <term>
```

### Implementation Steps
1. Add SQLiteExplorer to BCH tool registry
2. Create command handlers for info, tables, search
3. Route results through BCH messaging
4. Test with heartbeat.db and other Team Brain databases

---

## AI Agent Integration

### Integration Matrix

| Agent | Use Case | Integration Method | Priority |
|-------|----------|-------------------|----------|
| **Forge** | Review database schemas, verify test data | CLI + Python API | HIGH |
| **Atlas** | Debug tool databases, export test data | CLI + Python API | HIGH |
| **Clio** | Linux database inspection, batch analysis | CLI | MEDIUM |
| **Nexus** | Cross-platform DB checks | CLI + Python API | MEDIUM |
| **Bolt** | Quick database health checks | CLI | LOW |

### Agent-Specific Workflows

#### Forge (Orchestrator / Reviewer)
**Primary Use Case:** Review database schemas during code review, verify VitalHeart data integrity

**Integration Steps:**
1. Import SQLiteExplorer in review scripts
2. Use get_schema() to verify table structures match specifications
3. Use get_stats() to verify data quality after builds
4. Use diff() to compare database versions

**Example Workflow:**
```python
from sqliteexplorer import SQLiteExplorer

# During VitalHeart code review
with SQLiteExplorer("heartbeat.db") as db:
    # Verify schema matches spec
    schema = db.get_schema("heartbeats")
    expected_cols = ["id", "agent_name", "timestamp", "status", "mood"]
    actual_cols = [c["name"] for c in schema[0]["columns"]]
    assert all(c in actual_cols for c in expected_cols), "Schema mismatch!"

    # Verify data integrity
    stats = db.get_stats("heartbeats")
    for s in stats:
        if s["column"] == "agent_name" and s["null_count"] > 0:
            print("[!] Warning: agent_name has NULLs")
```

#### Atlas (Executor / Builder)
**Primary Use Case:** Debug tool databases during development, export test fixtures

**Integration Steps:**
1. Use during tool building to inspect databases created by tests
2. Export test data for regression testing
3. Verify database structure after migrations

**Example Workflow:**
```python
from sqliteexplorer import SQLiteExplorer

# After building a new tool with SQLite storage
with SQLiteExplorer("new_tool.db") as db:
    info = db.get_info()
    print(f"Database created: {info['table_count']} tables, {info['file_size_display']}")

    # Export test fixtures
    db.export_table("test_data", fmt="json", output="fixtures/test_data.json")
```

#### Clio (Linux / Ubuntu Agent)
**Primary Use Case:** Database inspection on Linux systems, batch analysis

**Platform Considerations:**
- Works identically on Linux (cross-platform by design)
- Use with BatchRunner for multi-database analysis

**Example:**
```bash
# Quick database health check
python3 sqliteexplorer.py info /var/lib/myapp/data.db
python3 sqliteexplorer.py stats /var/lib/myapp/data.db users
```

#### Nexus (Multi-Platform Agent)
**Primary Use Case:** Cross-platform database verification

**Cross-Platform Notes:**
- Uses pathlib for all paths (works on Windows/Linux/macOS)
- ASCII-safe output for all terminals
- No platform-specific dependencies

#### Bolt (Cline / Free Executor)
**Primary Use Case:** Quick database health checks without API costs

**Cost Considerations:**
- Zero API calls needed (local tool)
- Zero dependencies (no pip install required)
- Instant results (no network latency)

---

## Integration with Other Team Brain Tools

### With AgentHeartbeat
**Use Case:** Inspect and analyze the heartbeat database directly

```python
from sqliteexplorer import SQLiteExplorer

# Direct inspection of AgentHeartbeat's database
with SQLiteExplorer("C:/Users/logan/.teambrain/heartbeat.db") as db:
    # Check agent status
    result = db.query(
        "SELECT agent_name, status, mood, current_task "
        "FROM heartbeats ORDER BY id DESC LIMIT 5"
    )
    for row in result["rows"]:
        print(f"  {row[0]}: {row[1]} ({row[2]})")
```

### With SynapseLink
**Use Case:** Report database health to Team Brain

```python
from synapselink import quick_send
from sqliteexplorer import SQLiteExplorer

with SQLiteExplorer("heartbeat.db") as db:
    info = db.get_info()
    tables = db.get_tables()

    report = f"Tables: {info['table_count']}, Size: {info['file_size_display']}"
    for t in tables:
        report += f"\n  {t['name']}: {t['row_count']} rows"

    quick_send("TEAM", "DB Health Report", report, priority="NORMAL")
```

### With BatchRunner
**Use Case:** Run SQLiteExplorer across all Team Brain databases

```python
from batchrunner import BatchRunner

runner = BatchRunner()
runner.add("heartbeat", "python sqliteexplorer.py info heartbeat.db")
runner.add("sessions", "python sqliteexplorer.py info sessions.db")
runner.add("notes", "python sqliteexplorer.py info notes.db")
results = runner.run_parallel()
```

### With HashGuard
**Use Case:** Verify database file integrity before inspection

```python
from hashguard import HashGuard
from sqliteexplorer import SQLiteExplorer

guard = HashGuard()
if guard.verify("heartbeat.db"):
    with SQLiteExplorer("heartbeat.db") as db:
        info = db.get_info()
else:
    print("[!] Database integrity check failed!")
```

### With TaskQueuePro
**Use Case:** Schedule database inspection tasks

```python
from taskqueuepro import TaskQueuePro
from sqliteexplorer import SQLiteExplorer

queue = TaskQueuePro()
task_id = queue.create_task(
    title="Daily database health check",
    agent="ATLAS",
    priority=2,
    metadata={"tool": "SQLiteExplorer"}
)

with SQLiteExplorer("heartbeat.db") as db:
    info = db.get_info()
    queue.complete_task(task_id, result=str(info))
```

### With MemoryBridge
**Use Case:** Persist database analysis results

```python
from memorybridge import MemoryBridge
from sqliteexplorer import SQLiteExplorer

memory = MemoryBridge()

with SQLiteExplorer("heartbeat.db") as db:
    info = db.get_info()
    stats = db.get_stats("heartbeats")

memory.set("db_health_heartbeat", {
    "timestamp": info["modified"],
    "tables": info["table_count"],
    "size": info["file_size"],
    "stats": stats,
})
memory.sync()
```

### With SessionReplay
**Use Case:** Record database operations for debugging

```python
from sessionreplay import SessionReplay
from sqliteexplorer import SQLiteExplorer

replay = SessionReplay()
session_id = replay.start_session("ATLAS", task="DB inspection")

with SQLiteExplorer("heartbeat.db") as db:
    replay.log_input(session_id, "Inspecting heartbeat.db")
    info = db.get_info()
    replay.log_output(session_id, f"Tables: {info['table_count']}")

replay.end_session(session_id, status="COMPLETED")
```

### With ConfigManager
**Use Case:** Share SQLiteExplorer settings

```python
from configmanager import ConfigManager
from sqliteexplorer import SQLiteExplorer

config = ConfigManager()
db_path = config.get("databases.heartbeat", "~/.teambrain/heartbeat.db")

with SQLiteExplorer(db_path) as db:
    info = db.get_info()
```

### With ContextCompressor
**Use Case:** Compress large query outputs before sharing

```python
from contextcompressor import ContextCompressor
from sqliteexplorer import SQLiteExplorer

compressor = ContextCompressor()

with SQLiteExplorer("large_db.db") as db:
    full_report = db.export_table("events", fmt="json")
    compressed = compressor.compress_text(full_report, query="recent errors")
    print(f"Compressed from {len(full_report)} to {len(compressed.compressed_text)} chars")
```

### With DiskSage
**Use Case:** Correlate database sizes with disk usage

```python
from disksage import DiskSage
from sqliteexplorer import SQLiteExplorer

sage = DiskSage()
scan = sage.scan("~/.teambrain/")

# Find all SQLite databases and analyze each
for file_info in scan.files:
    if file_info.name.endswith(".db"):
        with SQLiteExplorer(file_info.path) as db:
            info = db.get_info()
            print(f"{file_info.name}: {info['table_count']} tables, {info['file_size_display']}")
```

---

## Adoption Roadmap

### Phase 1: Core Adoption (Week 1)
**Goal:** All agents aware and can use basic commands

**Steps:**
1. Tool deployed to GitHub
2. Quick-start guides sent via Synapse
3. Each agent tests info/tables/browse
4. Feedback collected

### Phase 2: Integration (Week 2-3)
**Goal:** Integrated into database debugging workflows

**Steps:**
1. Add to agent diagnostic routines
2. Create integration examples with AgentHeartbeat
3. Use for VitalHeart database inspection
4. Monitor usage patterns

### Phase 3: Optimization (Week 4+)
**Goal:** Fully adopted and optimized

**Steps:**
1. Collect efficiency metrics
2. Implement v1.1 improvements
3. Deepen integrations
4. Add advanced features (FTS5 support, graph output)

---

## Success Metrics

**Adoption:** Number of agents using tool daily
**Efficiency:** Time saved per inspection (target: 90%+ reduction)
**Quality:** Bug reports (target: < 3 per month)
**Integration:** Number of tools connected (target: 5+)

---

## Technical Integration Details

### Import Path
```python
from sqliteexplorer import SQLiteExplorer, TableFormatter
```

### Error Handling
- Exit code 0: Success
- Exit code 1: Error (file not found, SQL error, permission)
- Exit code 130: Interrupted (Ctrl+C)

### Logging
SQLiteExplorer does not produce log files by default. Use `--format json` for structured output suitable for log aggregation.

---

**Last Updated:** February 14, 2026
**Maintained By:** ATLAS (Team Brain)
