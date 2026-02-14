# SQLiteExplorer - Usage Examples

**12 working examples** covering basic to advanced usage.

Quick navigation:
- [Example 1: First Look at a Database](#example-1-first-look-at-a-database)
- [Example 2: Browsing Table Data](#example-2-browsing-table-data)
- [Example 3: Running SQL Queries](#example-3-running-sql-queries)
- [Example 4: Exporting Data to CSV](#example-4-exporting-data-to-csv)
- [Example 5: Exporting to JSON](#example-5-exporting-to-json)
- [Example 6: Column Statistics](#example-6-column-statistics)
- [Example 7: Searching Across Tables](#example-7-searching-across-tables)
- [Example 8: Size Analysis](#example-8-size-analysis)
- [Example 9: Comparing Two Databases](#example-9-comparing-two-databases)
- [Example 10: Optimizing with Vacuum](#example-10-optimizing-with-vacuum)
- [Example 11: Python API Usage](#example-11-python-api-usage)
- [Example 12: Real-World Team Brain Workflow](#example-12-real-world-team-brain-workflow)

---

## Example 1: First Look at a Database

**Scenario:** You have a database and want to understand its structure quickly.

**Steps:**
```bash
# Step 1: Get database overview
python sqliteexplorer.py info mydata.db

# Step 2: See all tables
python sqliteexplorer.py tables mydata.db

# Step 3: Inspect a specific table's schema
python sqliteexplorer.py schema mydata.db users
```

**Expected Output (info):**
```
============================================================
DATABASE INFO
============================================================
  Path:           /path/to/mydata.db
  File Size:      44.0 KB (45056 bytes)
  Last Modified:  2026-02-14T10:30:00
  SQLite Version: 3.45.3
  Encoding:       UTF-8
  Journal Mode:   delete
  Page Size:      4.0 KB
  Page Count:     11
  Free Pages:     0
------------------------------------------------------------
  Tables:         3
  Indexes:        2
  Views:          0
  Triggers:       0
============================================================
```

**What You Learned:**
- Database size and location
- Number of tables, indexes, views, triggers
- SQLite version and configuration

---

## Example 2: Browsing Table Data

**Scenario:** You need to see what's in a table, with pagination.

**Steps:**
```bash
# Browse first 10 rows
python sqliteexplorer.py browse mydata.db users --limit 10

# Browse with offset (page 2)
python sqliteexplorer.py browse mydata.db users --limit 10 --offset 10

# Browse with filter
python sqliteexplorer.py browse mydata.db users --where "age > 25" --order-by "name ASC"
```

**Expected Output:**
```
TABLE: users  [1-5 of 5]
+----+---------------+---------------------+-----+---------+
| id | name          | email               | age | balance |
+----+---------------+---------------------+-----+---------+
|  1 | Alice Smith   | alice@example.com   |  30 | 1500.50 |
|  2 | Bob Jones     | bob@example.com     |  25 | 2300.75 |
|  3 | Charlie Brown | charlie@example.com |  35 |  500.00 |
|  4 | Diana Prince  | diana@example.com   |  28 | 10000.0 |
|  5 | Eve Adams     | NULL                |     |       0 |
+----+---------------+---------------------+-----+---------+
(5 rows)
```

**What You Learned:**
- How pagination works (limit/offset)
- NULL values display as "NULL"
- Numeric columns are right-aligned
- The "showing" indicator tells you position in the dataset

---

## Example 3: Running SQL Queries

**Scenario:** You need to run a specific SQL query.

**Steps:**
```bash
# Simple query
python sqliteexplorer.py query mydata.db "SELECT name, age FROM users WHERE age > 28"

# Aggregate query
python sqliteexplorer.py query mydata.db "SELECT COUNT(*) as total, AVG(age) as avg_age FROM users"

# JOIN query
python sqliteexplorer.py query mydata.db "SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id"

# Get results as JSON
python sqliteexplorer.py query mydata.db "SELECT * FROM users" --format json
```

**Expected Output (first query):**
```
QUERY: SELECT name, age FROM users WHERE age > 28  (2 rows)
+---------------+-----+
| name          | age |
+---------------+-----+
| Alice Smith   |  30 |
| Charlie Brown |  35 |
+---------------+-----+
(2 rows)
```

**What You Learned:**
- Any valid SELECT query can be executed
- Results are formatted automatically
- Use --format json for machine-readable output

---

## Example 4: Exporting Data to CSV

**Scenario:** You need to export table data for analysis in Excel or pandas.

**Steps:**
```bash
# Export to file
python sqliteexplorer.py export mydata.db products --format csv --output products.csv

# Export to stdout (pipe to other tools)
python sqliteexplorer.py export mydata.db products --format csv

# Export query results
python sqliteexplorer.py export mydata.db products --query "SELECT name, price FROM products WHERE price > 20" --format csv --output expensive.csv
```

**Expected Output (stdout):**
```
id,name,price,category,stock
1,Widget A,9.99,Electronics,100
2,Widget B,19.99,Electronics,50
3,Gadget X,49.99,Gadgets,25
4,Tool Y,29.99,Tools,0
```

**What You Learned:**
- Export full tables or custom queries
- Output to file with --output or to stdout
- CSV format is Excel-compatible

---

## Example 5: Exporting to JSON

**Scenario:** You need structured data for a web API or data pipeline.

**Steps:**
```bash
# Export full table
python sqliteexplorer.py export mydata.db users --format json --output users.json

# Export to stdout
python sqliteexplorer.py export mydata.db users --format json
```

**Expected Output:**
```json
[
  {
    "id": 1,
    "name": "Alice Smith",
    "email": "alice@example.com",
    "age": 30,
    "balance": 1500.5
  },
  {
    "id": 2,
    "name": "Bob Jones",
    "email": "bob@example.com",
    "age": 25,
    "balance": 2300.75
  }
]
```

**What You Learned:**
- JSON export preserves data types (numbers, strings, null)
- Each row becomes a JSON object with column names as keys
- BLOB values are represented as `"<BLOB N bytes>"`
- NULL values become JSON `null`

---

## Example 6: Column Statistics

**Scenario:** You need to understand data quality -- nulls, distributions, ranges.

**Steps:**
```bash
python sqliteexplorer.py stats mydata.db users
```

**Expected Output:**
```
STATS: users
+------------+---------+----------+------+-------+----------+--------+--------+--------+
| Column     | Type    | Non-Null | Null | Null% | Distinct | Min    | Max    | Avg    |
+------------+---------+----------+------+-------+----------+--------+--------+--------+
| id         | INTEGER |        5 |    0 |  0.0% |        5 |      1 |      5 |      3 |
| name       | TEXT    |        5 |    0 |  0.0% |        5 |        |        |        |
| email      | TEXT    |        4 |    1 | 20.0% |        4 |        |        |        |
| age        | INTEGER |        4 |    1 | 20.0% |        4 |     25 |     35 | 29.5   |
| balance    | REAL    |        5 |    0 |  0.0% |        5 |      0 |  10000 | 2860.3 |
+------------+---------+----------+------+-------+----------+--------+--------+--------+
(5 rows)
```

**What You Learned:**
- See NULL counts and percentages instantly
- Numeric columns get min/max/avg
- Distinct value counts help identify data quality
- Identify columns that need cleaning (high null %)

---

## Example 7: Searching Across Tables

**Scenario:** You know a value exists somewhere but don't know which table.

**Steps:**
```bash
# Search all tables
python sqliteexplorer.py search mydata.db "alice"

# Search specific tables only
python sqliteexplorer.py search mydata.db "Electronics" --tables products

# Limit results
python sqliteexplorer.py search mydata.db "error" --limit 5

# JSON output for automation
python sqliteexplorer.py search mydata.db "admin" --format json
```

**Expected Output:**
```
============================================================
SEARCH: "alice"  (1 match)
============================================================

--- Match 1 [users] (columns: name, email) ---
  id: 1
  name: Alice Smith <<
  email: alice@example.com <<
  age: 30
  balance: 1500.5

(1 match)
```

**What You Learned:**
- Search is case-insensitive
- Matched columns are marked with `<<`
- Full row data is shown for context
- Works across all text columns in all tables

---

## Example 8: Size Analysis

**Scenario:** Your database is growing and you want to understand where space is used.

**Steps:**
```bash
python sqliteexplorer.py size mydata.db
```

**Expected Output:**
```
============================================================
SIZE ANALYSIS
============================================================
  File Size:   96.0 KB
  Used Space:  96.0 KB (24 pages)
  Free Space:  0 B (0 pages, 0.0%)
  Page Size:   4.0 KB
------------------------------------------------------------

TABLE SIZES
+------------------+------+---------+----------------+
| Table            | Rows | Columns | Est. Data Size |
+------------------+------+---------+----------------+
| alerts           |    0 |       7 | 0 B            |
| baselines        |    0 |       8 | 0 B            |
| heartbeats       |  139 |       8 | 11.8 KB        |
| velocity_metrics |    0 |       7 | 0 B            |
+------------------+------+---------+----------------+
(4 rows)
```

**What You Learned:**
- File size vs used space vs free space
- Per-table size estimates
- If free space > 0%, vacuum can help
- Page size and count for SQLite internals

---

## Example 9: Comparing Two Databases

**Scenario:** You need to check if dev and production schemas match.

**Steps:**
```bash
python sqliteexplorer.py diff dev.db production.db
```

**Expected Output (when different):**
```
============================================================
SCHEMA DIFF
============================================================
  A: dev.db
  B: production.db
  Common tables: 3
------------------------------------------------------------

  Tables only in A:
    + test_data

  Table Differences:
    Table: users
      Columns only in A: avatar
      Row count: 100 (A) vs 5000 (B) [diff: -4900]
============================================================
```

**What You Learned:**
- Tables unique to each database
- Column differences in shared tables
- Type mismatches between databases
- Row count comparison

---

## Example 10: Optimizing with Vacuum

**Scenario:** Database has grown over time and you want to reclaim space.

**Steps:**
```bash
# Preview (does nothing)
python sqliteexplorer.py vacuum mydata.db

# Actually optimize
python sqliteexplorer.py vacuum mydata.db --confirm
```

**Expected Output (vacuum):**
```
============================================================
VACUUM COMPLETE
============================================================
  Before: 256.0 KB
  After:  192.0 KB
  Saved:  64.0 KB (25.0%)
============================================================
```

**What You Learned:**
- Vacuum requires --confirm for safety
- Before/after comparison shows actual savings
- Always backup before vacuuming production databases

---

## Example 11: Python API Usage

**Scenario:** Using SQLiteExplorer programmatically in a Python script.

**Code:**
```python
from sqliteexplorer import SQLiteExplorer

# Open database with context manager
with SQLiteExplorer("heartbeat.db") as db:
    # Get overview
    info = db.get_info()
    print(f"Database has {info['table_count']} tables")

    # List tables
    for table in db.get_tables():
        print(f"  {table['name']}: {table['row_count']} rows")

    # Get statistics
    stats = db.get_stats("heartbeats")
    for s in stats:
        if s["null_count"] > 0:
            print(f"  Warning: {s['column']} has {s['null_count']} NULLs")

    # Search for an agent
    matches = db.search("LUMINA")
    print(f"Found {len(matches)} LUMINA heartbeats")

    # Export to JSON
    db.export_table("heartbeats", fmt="json", output="heartbeats_export.json")
    print("Exported to heartbeats_export.json")
```

**Expected Output:**
```
Database has 4 tables
  alerts: 0 rows
  baselines: 0 rows
  heartbeats: 139 rows
  velocity_metrics: 0 rows
  Warning: capabilities has 139 NULLs
Found 5 LUMINA heartbeats
Exported to heartbeats_export.json
```

---

## Example 12: Real-World Team Brain Workflow

**Scenario:** Debugging why an agent's heartbeats stopped.

**Steps:**
```bash
# Step 1: Check database health
python sqliteexplorer.py info heartbeat.db

# Step 2: See latest heartbeats
python sqliteexplorer.py browse heartbeat.db heartbeats --limit 5 --order-by "id DESC"

# Step 3: Search for the specific agent
python sqliteexplorer.py search heartbeat.db "LUMINA" --limit 10

# Step 4: Get stats to understand patterns
python sqliteexplorer.py stats heartbeat.db heartbeats

# Step 5: Check for alerts
python sqliteexplorer.py browse heartbeat.db alerts

# Step 6: Export recent data for analysis
python sqliteexplorer.py export heartbeat.db heartbeats --query "SELECT * FROM heartbeats ORDER BY id DESC LIMIT 50" --format json --output recent_heartbeats.json
```

**What You Learned:**
- Complete debugging workflow in 6 commands
- Combine info, browse, search, stats, and export for full picture
- Export specific subsets with custom queries
- Total time: under 1 minute vs 15+ minutes manually

---

## 📝 Tips & Tricks

1. **Use JSON format for scripting:** `--format json` for machine-readable output
2. **Pipe CSV to other tools:** `python sqliteexplorer.py export db users --format csv | head -20`
3. **Quick table check:** `python sqliteexplorer.py tables db` is the fastest overview
4. **Debug with search:** When you don't know which table has data, `search` checks them all
5. **Check before vacuum:** Always run `size` first to see if vacuum will help

---

**Built by ATLAS (Team Brain) for Logan Smith / Metaphy LLC**
**February 14, 2026**
