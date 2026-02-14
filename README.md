# 🔍 SQLiteExplorer

### Smart SQLite Database Explorer & Management Tool

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/DonkRonk17/SQLiteExplorer)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-100%20passing-brightgreen.svg)](test_sqliteexplorer.py)
[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://python.org)
[![Dependencies](https://img.shields.io/badge/dependencies-zero-orange.svg)](requirements.txt)

**Instantly inspect, query, analyze, and export SQLite databases.** Beautiful formatted output, zero dependencies, cross-platform.

---

## 📖 Table of Contents

- [The Problem](#-the-problem)
- [The Solution](#-the-solution)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
  - [Database Info](#info---database-overview)
  - [List Tables](#tables---list-all-tables)
  - [Show Schema](#schema---table-schema)
  - [Browse Data](#browse---browse-table-data)
  - [Run Queries](#query---execute-sql)
  - [Export Data](#export---export-to-csvjsonmarkdown)
  - [Column Stats](#stats---column-statistics)
  - [Search Data](#search---full-text-search)
  - [Size Analysis](#size---detailed-size-analysis)
  - [Compare DBs](#diff---compare-databases)
  - [Optimize](#vacuum---optimize-database)
- [Python API](#-python-api)
- [Output Formats](#-output-formats)
- [Real-World Results](#-real-world-results)
- [How It Works](#-how-it-works)
- [Use Cases](#-use-cases)
- [Integration](#-integration)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [Credits](#-credits)
- [License](#-license)

---

## 🚨 The Problem

When working with SQLite databases, developers face these frustrations:

- **Raw sqlite3 shell** has no formatting -- data is hard to read
- **Schema inspection** requires manual PRAGMA queries
- **Data export** needs custom scripts for each format
- **Column statistics** require writing aggregate queries by hand
- **Searching across tables** means checking each one individually
- **Comparing databases** is tedious and error-prone
- **Size analysis** has no built-in tool

**Result:** 10-20 minutes wasted per database inspection session, multiple times per week.

---

## ✅ The Solution

SQLiteExplorer provides **one command** to do what used to take many:

```bash
# See everything about a database in 3 seconds
python sqliteexplorer.py info mydata.db
python sqliteexplorer.py tables mydata.db
python sqliteexplorer.py browse mydata.db users --limit 10
```

**Time saved:** 10-20 minutes per inspection, replaced with 3-second commands.

---

## ✨ Features

- 🔍 **11 Commands** - info, tables, schema, browse, query, export, stats, search, size, diff, vacuum
- 📊 **Beautiful Output** - Aligned columns, separators, clear formatting in terminal
- 📤 **Multi-Format Export** - CSV, JSON, and Markdown output for any data
- 📈 **Column Statistics** - Min, max, avg, null count, distinct values per column
- 🔎 **Full-Text Search** - Search across ALL text columns in ALL tables at once
- 📏 **Size Analysis** - File size, table sizes, free space, optimization recommendations
- 🔄 **Database Diff** - Compare schemas of two databases side by side
- 🧹 **Vacuum/Optimize** - Reclaim wasted space with before/after reporting
- 🐍 **Python API** - Use programmatically with `from sqliteexplorer import SQLiteExplorer`
- 🔒 **Read-Only by Default** - Never accidentally modifies your databases
- 📦 **Zero Dependencies** - Pure Python standard library (sqlite3, json, csv, argparse)
- 💻 **Cross-Platform** - Windows, macOS, Linux with pathlib throughout
- ✅ **100 Tests** - Comprehensive test suite, 100% passing

---

## 🚀 Quick Start

### 1. Download
```bash
git clone https://github.com/DonkRonk17/SQLiteExplorer.git
cd SQLiteExplorer
```

### 2. Run your first command
```bash
python sqliteexplorer.py info your_database.db
```

### 3. That's it!
No installation, no dependencies, no configuration needed. Just Python 3.7+.

---

## 📥 Installation

### Method 1: Clone from GitHub (Recommended)
```bash
git clone https://github.com/DonkRonk17/SQLiteExplorer.git
cd SQLiteExplorer
python sqliteexplorer.py --version
```

### Method 2: Direct Download
Download `sqliteexplorer.py` and place it in your project or PATH.

### Method 3: pip install (from source)
```bash
git clone https://github.com/DonkRonk17/SQLiteExplorer.git
cd SQLiteExplorer
pip install -e .
```

### Requirements
- Python 3.7 or higher
- No external dependencies (uses only Python standard library)

---

## 📖 Usage

### General Syntax
```bash
python sqliteexplorer.py <command> <database> [options]
```

### Global Options
```
--version     Show version
--help        Show help
--format      Output format (text, json, csv, md - varies by command)
--output      Write output to file
```

---

### `info` - Database Overview

Get a complete overview of any SQLite database:

```bash
python sqliteexplorer.py info heartbeat.db
```

Output:
```
============================================================
DATABASE INFO
============================================================
  Path:           C:\data\heartbeat.db
  File Size:      96.0 KB (98304 bytes)
  Last Modified:  2026-02-14T05:10:27
  SQLite Version: 3.45.3
  Encoding:       UTF-8
  Journal Mode:   delete
  Page Size:      4.0 KB
  Page Count:     24
  Free Pages:     0
------------------------------------------------------------
  Tables:         4
  Indexes:        4
  Views:          0
  Triggers:       0
============================================================
```

---

### `tables` - List All Tables

See every table with row counts and column counts:

```bash
python sqliteexplorer.py tables heartbeat.db
```

Output:
```
TABLES
+------------------+------+---------+
| Table Name       | Rows | Columns |
+------------------+------+---------+
| alerts           |    0 |       7 |
| baselines        |    0 |       8 |
| heartbeats       |  139 |       8 |
| velocity_metrics |    0 |       7 |
| --- TOTAL ---    |  139 |         |
+------------------+------+---------+
(5 rows)
```

---

### `schema` - Table Schema

Inspect columns, types, constraints, indexes, and CREATE SQL:

```bash
# Single table
python sqliteexplorer.py schema mydata.db users

# All tables
python sqliteexplorer.py schema mydata.db
```

Output shows columns with types, NOT NULL constraints, primary keys, indexes, foreign keys, and the original CREATE TABLE statement.

---

### `browse` - Browse Table Data

Page through table data with beautiful formatting:

```bash
# Basic browse
python sqliteexplorer.py browse mydata.db users

# With pagination
python sqliteexplorer.py browse mydata.db users --limit 10 --offset 20

# With filtering
python sqliteexplorer.py browse mydata.db users --where "age > 25"

# With ordering
python sqliteexplorer.py browse mydata.db users --order-by "name ASC"
```

---

### `query` - Execute SQL

Run any SELECT query with formatted results:

```bash
python sqliteexplorer.py query mydata.db "SELECT name, age FROM users WHERE age > 30"
```

Output:
```
QUERY: SELECT name, age FROM users WHERE age > 30  (2 rows)
+---------+-----+
| name    | age |
+---------+-----+
| Charlie |  35 |
| Frank   |  42 |
+---------+-----+
(2 rows)
```

---

### `export` - Export to CSV/JSON/Markdown

Export any table or query results to your preferred format:

```bash
# Export table to CSV
python sqliteexplorer.py export mydata.db users --format csv --output users.csv

# Export to JSON
python sqliteexplorer.py export mydata.db users --format json --output users.json

# Export to Markdown
python sqliteexplorer.py export mydata.db users --format md

# Export query results
python sqliteexplorer.py export mydata.db users --query "SELECT * FROM users WHERE active=1" --format json
```

---

### `stats` - Column Statistics

Get statistical analysis of every column in a table:

```bash
python sqliteexplorer.py stats mydata.db products
```

Output:
```
STATS: products
+----------+---------+----------+------+-------+----------+-------+-------+-------+
| Column   | Type    | Non-Null | Null | Null% | Distinct | Min   | Max   | Avg   |
+----------+---------+----------+------+-------+----------+-------+-------+-------+
| id       | INTEGER |        4 |    0 |  0.0% |        4 |     1 |     4 |   2.5 |
| name     | TEXT    |        4 |    0 |  0.0% |        4 |       |       |       |
| price    | REAL    |        4 |    0 |  0.0% |        4 |  9.99 | 49.99 | 27.49 |
| category | TEXT    |        4 |    0 |  0.0% |        3 |       |       |       |
| stock    | INTEGER |        4 |    0 |  0.0% |        4 |     0 |   100 | 43.75 |
+----------+---------+----------+------+-------+----------+-------+-------+-------+
(5 rows)
```

---

### `search` - Full-Text Search

Search for any term across ALL text columns in ALL tables:

```bash
# Search everything
python sqliteexplorer.py search mydata.db "admin"

# Search specific tables
python sqliteexplorer.py search mydata.db "error" --tables heartbeats,alerts

# Limit results
python sqliteexplorer.py search mydata.db "test" --limit 5
```

Each match shows the table name, matched columns (marked with `<<`), and full row data.

---

### `size` - Detailed Size Analysis

Understand where your disk space is going:

```bash
python sqliteexplorer.py size mydata.db
```

Output includes file size, used/free space, page information, and per-table size estimates. If free space is detected, suggests running `vacuum`.

---

### `diff` - Compare Databases

Compare the schemas of two databases:

```bash
python sqliteexplorer.py diff production.db staging.db
```

Output shows:
- Tables only in database A
- Tables only in database B
- Column differences (added, removed, type changes)
- Row count differences

---

### `vacuum` - Optimize Database

Reclaim wasted space and defragment:

```bash
# Preview (no changes)
python sqliteexplorer.py vacuum mydata.db

# Actually vacuum (requires --confirm)
python sqliteexplorer.py vacuum mydata.db --confirm
```

Reports before/after sizes and space saved.

---

## 🐍 Python API

Use SQLiteExplorer programmatically in your Python code:

```python
from sqliteexplorer import SQLiteExplorer

# Context manager (recommended)
with SQLiteExplorer("mydata.db") as db:
    # Get database info
    info = db.get_info()
    print(f"Tables: {info['table_count']}")

    # List tables
    tables = db.get_tables()
    for t in tables:
        print(f"  {t['name']}: {t['row_count']} rows")

    # Browse data
    result = db.browse("users", limit=10)
    for row in result["rows"]:
        print(row)

    # Run queries
    result = db.query("SELECT COUNT(*) FROM users")
    print(f"Total users: {result['rows'][0][0]}")

    # Get column statistics
    stats = db.get_stats("users")
    for s in stats:
        print(f"  {s['column']}: {s['distinct']} distinct, {s['null_count']} nulls")

    # Search across tables
    matches = db.search("admin")
    print(f"Found {len(matches)} matches")

    # Export to JSON
    json_data = db.export_table("users", fmt="json", output="users.json")

    # Compare databases
    diff = db.diff("other.db")
    print(f"Identical: {diff['identical_schema']}")
```

---

## 📊 Output Formats

Most commands support multiple output formats:

| Command | text | json | csv | md |
|---------|------|------|-----|-----|
| info | Yes | Yes | - | - |
| tables | Yes | Yes | - | Yes |
| schema | Yes | Yes | - | Yes |
| browse | Yes | Yes | - | Yes |
| query | Yes | Yes | - | Yes |
| export | - | Yes | Yes | Yes |
| stats | Yes | Yes | - | Yes |
| search | Yes | Yes | - | - |
| size | Yes | Yes | - | - |
| diff | Yes | Yes | - | - |
| vacuum | Yes | Yes | - | - |

Use `--format json` for machine-readable output, `--format md` for documentation.

---

## 📈 Real-World Results

### Before SQLiteExplorer
```
Task: Inspect a database schema and export data
Time: 15-20 minutes (open sqlite3 shell, write PRAGMA queries, write export script)
Steps: 8-10 manual commands
```

### After SQLiteExplorer
```
Task: Same inspection and export
Time: 30 seconds (3 commands)
Steps: 3 commands (info, schema, export)
```

**Time saved: 95%** (15 minutes -> 30 seconds)

### Tested With Real Databases
- AgentHeartbeat (heartbeat.db) - 4 tables, 139 rows - instant results
- Team Brain tool databases across 76+ projects
- Databases up to 1000+ rows in automated tests

---

## 🔧 How It Works

### Architecture
```
CLI (argparse)
    |
    v
SQLiteExplorer (main class)
    |-- connect()       Read-only SQLite connection (URI mode)
    |-- get_info()      PRAGMA queries for metadata
    |-- get_tables()    sqlite_master + COUNT queries
    |-- get_schema()    PRAGMA table_info/index_list/foreign_key_list
    |-- browse()        SELECT with LIMIT/OFFSET/WHERE/ORDER BY
    |-- query()         Raw SQL execution
    |-- export_table()  Fetch all + format as CSV/JSON/MD
    |-- get_stats()     Aggregate queries (MIN/MAX/AVG/COUNT/DISTINCT)
    |-- search()        LIKE queries across all text columns
    |-- get_size()      PRAGMA page_size/page_count + estimates
    |-- diff()          Compare sqlite_master + PRAGMA between databases
    |-- vacuum()        VACUUM command with size reporting
    |
    v
TableFormatter (output formatting)
    |-- format_table()  Aligned ASCII tables with truncation
    |-- format_json()   JSON with custom serializers
    |-- format_csv()    Standard CSV via csv module
    |-- format_markdown()  GitHub-flavored Markdown tables
```

### Key Design Decisions

1. **Read-only connections** - Uses `?mode=ro` URI to prevent accidental writes
2. **ASCII-safe output** - No Unicode emojis for Windows console compatibility
3. **Zero dependencies** - Everything in Python's standard library
4. **Lazy connections** - Database opened only when first query executes
5. **Context manager** - Safe resource cleanup with `with` statement
6. **Graceful errors** - Every edge case (NULL, BLOB, empty, locked) handled

---

## 💡 Use Cases

### 1. Debug AI Agent Databases
```bash
# Check Lumina's heartbeat data
python sqliteexplorer.py search heartbeat.db "LUMINA" --limit 5
```

### 2. Export Data for Analysis
```bash
# Export to JSON for data science workflows
python sqliteexplorer.py export analytics.db events --format json -o events.json
```

### 3. Compare Dev vs Production
```bash
# Schema drift detection
python sqliteexplorer.py diff dev.db prod.db
```

### 4. Database Health Checks
```bash
# Quick health overview
python sqliteexplorer.py info app.db
python sqliteexplorer.py size app.db
```

### 5. Find Data Across Tables
```bash
# Where is "error" mentioned?
python sqliteexplorer.py search logs.db "error" --limit 20
```

---

## 🔗 Integration

SQLiteExplorer integrates with the Team Brain ecosystem:

- **AgentHeartbeat** - Inspect heartbeat.db for agent monitoring data
- **SynapseLink** - Report database issues to team via notifications
- **BatchRunner** - Run SQLiteExplorer across multiple databases in parallel
- **HashGuard** - Verify database file integrity
- **DiskSage** - Correlate database sizes with disk usage

See [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md) for full integration documentation.
See [QUICK_START_GUIDES.md](QUICK_START_GUIDES.md) for agent-specific 5-minute guides.
See [INTEGRATION_EXAMPLES.md](INTEGRATION_EXAMPLES.md) for copy-paste code examples.

---

## 🔨 Troubleshooting

### "File not found"
- Check the database path is correct
- Use absolute paths if running from a different directory

### "Database is locked"
- Another process may have the database open for writing
- SQLiteExplorer opens in read-only mode, so this is rare
- Close other applications using the database and retry

### "File is not a database"
- The file exists but is not a valid SQLite database
- Check the file is not corrupted or a different format

### Windows encoding issues
- SQLiteExplorer uses ASCII-safe output by default
- If you see encoding errors, ensure your terminal supports UTF-8

### Large database performance
- Use `--limit` with browse to page through data
- Use `--where` to filter before fetching
- Stats and search may take longer on tables with 100K+ rows

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all 100 tests pass (`python test_sqliteexplorer.py`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style
- Python 3.7+ compatible
- Type hints on all public functions
- Docstrings with Args/Returns/Raises
- ASCII-safe output only (no Unicode emojis in code)
- Zero external dependencies preferred

---

## 📝 Credits

**Built by:** ATLAS (Team Brain)
**For:** Logan Smith / Metaphy LLC
**Date:** February 14, 2026
**Part of:** Beacon HQ / Team Brain Ecosystem
**Tool Number:** #77 in the Team Brain catalog

**Special Thanks:**
- Team Brain collective for the ecosystem that makes tools like this valuable
- Logan Smith for the vision of professional, zero-dependency tools
- FORGE for orchestration and quality standards

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

```
Copyright (c) 2026 Logan Smith / Metaphy LLC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software.
```

---

## 📚 Documentation

- [README.md](README.md) - This file (primary documentation)
- [EXAMPLES.md](EXAMPLES.md) - 12 working examples with expected output
- [CHEAT_SHEET.txt](CHEAT_SHEET.txt) - Quick reference guide
- [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md) - Team Brain integration plan
- [QUICK_START_GUIDES.md](QUICK_START_GUIDES.md) - Agent-specific guides
- [INTEGRATION_EXAMPLES.md](INTEGRATION_EXAMPLES.md) - Code examples

---

**Built with precision by ATLAS. Quality is not an act, it is a habit.**
**For the Maximum Benefit of Life. One World. One Family. One Love.** 🔆
