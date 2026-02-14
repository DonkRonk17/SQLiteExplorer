#!/usr/bin/env python3
"""
Comprehensive test suite for SQLiteExplorer.

Tests cover:
- Core functionality (info, tables, schema, browse, query, export, stats, search, size, diff, vacuum)
- Edge cases (empty databases, NULL values, BLOB data, long strings)
- Error handling (bad paths, missing tables, SQL errors)
- Integration scenarios (multi-table, large data, various types)
- Formatters (text, JSON, CSV, Markdown)

Run: python test_sqliteexplorer.py

Author: ATLAS (Team Brain)
Date: February 14, 2026
"""

import json
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqliteexplorer import SQLiteExplorer, TableFormatter, _format_size


class TestHelpers(unittest.TestCase):
    """Test utility helper functions."""

    def test_format_size_zero(self):
        """Test formatting zero bytes."""
        self.assertEqual(_format_size(0), "0 B")

    def test_format_size_bytes(self):
        """Test formatting small byte values."""
        self.assertEqual(_format_size(512), "512 B")

    def test_format_size_kilobytes(self):
        """Test formatting kilobyte values."""
        result = _format_size(1024)
        self.assertEqual(result, "1.0 KB")

    def test_format_size_megabytes(self):
        """Test formatting megabyte values."""
        result = _format_size(1024 * 1024)
        self.assertEqual(result, "1.0 MB")

    def test_format_size_gigabytes(self):
        """Test formatting gigabyte values."""
        result = _format_size(1024 * 1024 * 1024)
        self.assertEqual(result, "1.0 GB")

    def test_format_size_negative(self):
        """Test formatting negative values."""
        self.assertEqual(_format_size(-1), "N/A")


class TestTableFormatter(unittest.TestCase):
    """Test the TableFormatter class."""

    def test_format_table_basic(self):
        """Test basic table formatting."""
        headers = ["Name", "Age"]
        rows = [["Alice", 30], ["Bob", 25]]
        result = TableFormatter.format_table(headers, rows)
        self.assertIn("Alice", result)
        self.assertIn("Bob", result)
        self.assertIn("Name", result)
        self.assertIn("(2 rows)", result)

    def test_format_table_empty(self):
        """Test formatting empty table."""
        headers = ["Name", "Age"]
        rows = []
        result = TableFormatter.format_table(headers, rows)
        self.assertIn("(0 rows)", result)

    def test_format_table_no_headers(self):
        """Test formatting with no headers."""
        result = TableFormatter.format_table([], [])
        self.assertEqual(result, "(no columns)")

    def test_format_table_truncation(self):
        """Test long value truncation."""
        headers = ["Value"]
        rows = [["A" * 100]]
        result = TableFormatter.format_table(headers, rows, max_width=20)
        self.assertIn("...", result)

    def test_format_table_null_values(self):
        """Test NULL value display."""
        headers = ["Value"]
        rows = [[None]]
        result = TableFormatter.format_table(headers, rows)
        self.assertIn("NULL", result)

    def test_format_table_blob_values(self):
        """Test BLOB value display."""
        headers = ["Data"]
        rows = [[b"\x00\x01\x02"]]
        result = TableFormatter.format_table(headers, rows)
        self.assertIn("<BLOB 3 bytes>", result)

    def test_format_table_with_title(self):
        """Test table with title."""
        headers = ["Col"]
        rows = [["val"]]
        result = TableFormatter.format_table(headers, rows, title="MY TABLE")
        self.assertIn("MY TABLE", result)

    def test_format_json(self):
        """Test JSON formatting."""
        data = {"key": "value", "num": 42}
        result = TableFormatter.format_json(data)
        parsed = json.loads(result)
        self.assertEqual(parsed["key"], "value")
        self.assertEqual(parsed["num"], 42)

    def test_format_json_blob(self):
        """Test JSON formatting of BLOB data."""
        data = {"data": b"\x00\x01"}
        result = TableFormatter.format_json(data)
        self.assertIn("BLOB", result)

    def test_format_csv(self):
        """Test CSV formatting."""
        headers = ["Name", "Age"]
        rows = [["Alice", 30], ["Bob", 25]]
        result = TableFormatter.format_csv_str(headers, rows)
        self.assertIn("Name,Age", result)
        self.assertIn("Alice,30", result)

    def test_format_csv_null(self):
        """Test CSV formatting with NULL."""
        headers = ["Value"]
        rows = [[None]]
        result = TableFormatter.format_csv_str(headers, rows)
        lines = result.strip().split("\n")
        self.assertEqual(len(lines), 2)

    def test_format_markdown(self):
        """Test Markdown table formatting."""
        headers = ["Name", "Age"]
        rows = [["Alice", 30]]
        result = TableFormatter.format_markdown(headers, rows)
        self.assertIn("| Name | Age |", result)
        self.assertIn("| --- | --- |", result)
        self.assertIn("| Alice | 30 |", result)

    def test_format_markdown_no_headers(self):
        """Test Markdown with no headers."""
        result = TableFormatter.format_markdown([], [])
        self.assertEqual(result, "(no columns)")

    def test_format_markdown_pipe_escape(self):
        """Test Markdown pipe character escaping."""
        headers = ["Value"]
        rows = [["a|b"]]
        result = TableFormatter.format_markdown(headers, rows)
        self.assertIn("a\\|b", result)

    def test_format_table_float_values(self):
        """Test float value formatting."""
        headers = ["Value"]
        rows = [[3.14159265]]
        result = TableFormatter.format_table(headers, rows)
        self.assertIn("3.14159", result)

    def test_format_table_newline_in_value(self):
        """Test newline replacement in values."""
        headers = ["Text"]
        rows = [["line1\nline2"]]
        result = TableFormatter.format_table(headers, rows)
        self.assertIn("line1\\nline2", result)

    def test_format_table_single_row(self):
        """Test single row count display."""
        headers = ["X"]
        rows = [["a"]]
        result = TableFormatter.format_table(headers, rows)
        self.assertIn("(1 row)", result)


class BaseDBTest(unittest.TestCase):
    """Base class with test database setup."""

    def setUp(self):
        """Create test database with sample data."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self._create_test_db()

    def tearDown(self):
        """Clean up test files."""
        try:
            if hasattr(self, "explorer") and self.explorer:
                self.explorer.close()
        except Exception:
            pass
        try:
            for f in Path(self.temp_dir).glob("*"):
                f.unlink()
            Path(self.temp_dir).rmdir()
        except Exception:
            pass

    def _create_test_db(self):
        """Create a populated test database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                age INTEGER,
                balance REAL DEFAULT 0.0,
                bio TEXT,
                avatar BLOB,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert sample users
        users = [
            ("Alice Smith", "alice@example.com", 30, 1500.50, "Developer", None),
            ("Bob Jones", "bob@example.com", 25, 2300.75, "Designer", b"\x89PNG"),
            ("Charlie Brown", "charlie@example.com", 35, 500.00, None, None),
            ("Diana Prince", "diana@example.com", 28, 10000.00, "Hero", None),
            ("Eve Adams", None, None, 0.0, "Mystery person", None),
        ]
        cursor.executemany(
            "INSERT INTO users (name, email, age, balance, bio, avatar) VALUES (?, ?, ?, ?, ?, ?)",
            users,
        )

        # Products table
        cursor.execute("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                category TEXT,
                stock INTEGER DEFAULT 0
            )
        """)

        products = [
            (1, "Widget A", 9.99, "Electronics", 100),
            (2, "Widget B", 19.99, "Electronics", 50),
            (3, "Gadget X", 49.99, "Gadgets", 25),
            (4, "Tool Y", 29.99, "Tools", 0),
        ]
        cursor.executemany(
            "INSERT INTO products VALUES (?, ?, ?, ?, ?)", products
        )

        # Orders table (with foreign key)
        cursor.execute("""
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                product_id INTEGER REFERENCES products(id),
                quantity INTEGER NOT NULL,
                total REAL NOT NULL,
                order_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        orders = [
            (1, 1, 1, 2, 19.98),
            (2, 1, 3, 1, 49.99),
            (3, 2, 2, 3, 59.97),
            (4, 3, 1, 1, 9.99),
        ]
        cursor.executemany(
            "INSERT INTO orders VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)", orders
        )

        # Create an index
        cursor.execute("CREATE INDEX idx_users_email ON users(email)")
        cursor.execute("CREATE INDEX idx_orders_user ON orders(user_id)")

        conn.commit()
        conn.close()


class TestSQLiteExplorerInit(BaseDBTest):
    """Test SQLiteExplorer initialization."""

    def test_init_valid_db(self):
        """Test initialization with valid database."""
        db = SQLiteExplorer(self.db_path)
        self.assertIsNotNone(db)
        db.close()

    def test_init_nonexistent_file(self):
        """Test initialization with non-existent file."""
        with self.assertRaises(FileNotFoundError):
            SQLiteExplorer("/nonexistent/path/db.sqlite")

    def test_init_empty_path(self):
        """Test initialization with empty path."""
        with self.assertRaises(ValueError):
            SQLiteExplorer("")

    def test_init_none_path(self):
        """Test initialization with None path."""
        with self.assertRaises(ValueError):
            SQLiteExplorer(None)

    def test_init_directory_path(self):
        """Test initialization with directory instead of file."""
        with self.assertRaises(ValueError):
            SQLiteExplorer(self.temp_dir)

    def test_context_manager(self):
        """Test context manager support."""
        with SQLiteExplorer(self.db_path) as db:
            tables = db.get_tables()
            self.assertIsNotNone(tables)


class TestGetInfo(BaseDBTest):
    """Test get_info() functionality."""

    def test_info_returns_dict(self):
        """Test info returns a dictionary."""
        with SQLiteExplorer(self.db_path) as db:
            info = db.get_info()
            self.assertIsInstance(info, dict)

    def test_info_has_required_fields(self):
        """Test info has all required fields."""
        with SQLiteExplorer(self.db_path) as db:
            info = db.get_info()
            required = [
                "path", "file_size", "file_size_display", "modified",
                "sqlite_version", "page_size", "page_count",
                "table_count", "index_count",
            ]
            for field in required:
                self.assertIn(field, info, "Missing field: %s" % field)

    def test_info_correct_table_count(self):
        """Test info reports correct table count."""
        with SQLiteExplorer(self.db_path) as db:
            info = db.get_info()
            self.assertEqual(info["table_count"], 3)

    def test_info_correct_index_count(self):
        """Test info reports correct index count."""
        with SQLiteExplorer(self.db_path) as db:
            info = db.get_info()
            # 2 explicit indexes + sqlite autoindex for UNIQUE
            self.assertGreaterEqual(info["index_count"], 2)

    def test_info_file_size_positive(self):
        """Test info reports positive file size."""
        with SQLiteExplorer(self.db_path) as db:
            info = db.get_info()
            self.assertGreater(info["file_size"], 0)


class TestGetTables(BaseDBTest):
    """Test get_tables() functionality."""

    def test_tables_returns_list(self):
        """Test tables returns a list."""
        with SQLiteExplorer(self.db_path) as db:
            tables = db.get_tables()
            self.assertIsInstance(tables, list)

    def test_tables_correct_count(self):
        """Test correct number of tables returned."""
        with SQLiteExplorer(self.db_path) as db:
            tables = db.get_tables()
            self.assertEqual(len(tables), 3)

    def test_tables_have_names(self):
        """Test tables have expected names."""
        with SQLiteExplorer(self.db_path) as db:
            tables = db.get_tables()
            names = [t["name"] for t in tables]
            self.assertIn("users", names)
            self.assertIn("products", names)
            self.assertIn("orders", names)

    def test_tables_row_counts(self):
        """Test tables have correct row counts."""
        with SQLiteExplorer(self.db_path) as db:
            tables = db.get_tables()
            for t in tables:
                if t["name"] == "users":
                    self.assertEqual(t["row_count"], 5)
                elif t["name"] == "products":
                    self.assertEqual(t["row_count"], 4)
                elif t["name"] == "orders":
                    self.assertEqual(t["row_count"], 4)

    def test_tables_column_counts(self):
        """Test tables report column counts."""
        with SQLiteExplorer(self.db_path) as db:
            tables = db.get_tables()
            for t in tables:
                self.assertGreater(t["column_count"], 0)


class TestGetSchema(BaseDBTest):
    """Test get_schema() functionality."""

    def test_schema_single_table(self):
        """Test getting schema for a single table."""
        with SQLiteExplorer(self.db_path) as db:
            schema = db.get_schema("users")
            self.assertEqual(len(schema), 1)
            self.assertEqual(schema[0]["table"], "users")

    def test_schema_all_tables(self):
        """Test getting schema for all tables."""
        with SQLiteExplorer(self.db_path) as db:
            schema = db.get_schema()
            self.assertEqual(len(schema), 3)

    def test_schema_columns(self):
        """Test schema has correct columns for users table."""
        with SQLiteExplorer(self.db_path) as db:
            schema = db.get_schema("users")
            col_names = [c["name"] for c in schema[0]["columns"]]
            self.assertIn("id", col_names)
            self.assertIn("name", col_names)
            self.assertIn("email", col_names)
            self.assertIn("age", col_names)

    def test_schema_column_types(self):
        """Test schema reports column types."""
        with SQLiteExplorer(self.db_path) as db:
            schema = db.get_schema("users")
            cols = {c["name"]: c for c in schema[0]["columns"]}
            self.assertEqual(cols["id"]["type"], "INTEGER")
            self.assertEqual(cols["name"]["type"], "TEXT")
            self.assertEqual(cols["age"]["type"], "INTEGER")

    def test_schema_primary_key(self):
        """Test schema identifies primary key."""
        with SQLiteExplorer(self.db_path) as db:
            schema = db.get_schema("users")
            cols = {c["name"]: c for c in schema[0]["columns"]}
            self.assertTrue(cols["id"]["pk"])

    def test_schema_indexes(self):
        """Test schema includes indexes."""
        with SQLiteExplorer(self.db_path) as db:
            schema = db.get_schema("users")
            idx_names = [i["name"] for i in schema[0]["indexes"]]
            self.assertIn("idx_users_email", idx_names)

    def test_schema_create_sql(self):
        """Test schema includes CREATE SQL."""
        with SQLiteExplorer(self.db_path) as db:
            schema = db.get_schema("users")
            self.assertIn("CREATE TABLE", schema[0]["create_sql"])

    def test_schema_nonexistent_table(self):
        """Test schema raises error for nonexistent table."""
        with SQLiteExplorer(self.db_path) as db:
            with self.assertRaises(ValueError) as ctx:
                db.get_schema("nonexistent")
            self.assertIn("not found", str(ctx.exception))


class TestBrowse(BaseDBTest):
    """Test browse() functionality."""

    def test_browse_basic(self):
        """Test basic table browsing."""
        with SQLiteExplorer(self.db_path) as db:
            result = db.browse("users")
            self.assertEqual(len(result["rows"]), 5)
            self.assertEqual(result["total_rows"], 5)

    def test_browse_with_limit(self):
        """Test browsing with row limit."""
        with SQLiteExplorer(self.db_path) as db:
            result = db.browse("users", limit=2)
            self.assertEqual(len(result["rows"]), 2)
            self.assertEqual(result["total_rows"], 5)

    def test_browse_with_offset(self):
        """Test browsing with offset."""
        with SQLiteExplorer(self.db_path) as db:
            result = db.browse("users", limit=2, offset=3)
            self.assertEqual(len(result["rows"]), 2)

    def test_browse_with_where(self):
        """Test browsing with WHERE filter."""
        with SQLiteExplorer(self.db_path) as db:
            result = db.browse("users", where="age > 28")
            self.assertEqual(len(result["rows"]), 2)  # Alice (30), Charlie (35)

    def test_browse_with_order(self):
        """Test browsing with ORDER BY."""
        with SQLiteExplorer(self.db_path) as db:
            result = db.browse("users", order_by="age DESC")
            # First row should be Charlie (35)
            self.assertEqual(result["rows"][0][1], "Charlie Brown")

    def test_browse_nonexistent_table(self):
        """Test browsing nonexistent table."""
        with SQLiteExplorer(self.db_path) as db:
            with self.assertRaises(ValueError):
                db.browse("nonexistent")

    def test_browse_showing_string(self):
        """Test browse returns correct 'showing' string."""
        with SQLiteExplorer(self.db_path) as db:
            result = db.browse("users", limit=2, offset=0)
            self.assertEqual(result["showing"], "1-2 of 5")


class TestQuery(BaseDBTest):
    """Test query() functionality."""

    def test_query_select(self):
        """Test basic SELECT query."""
        with SQLiteExplorer(self.db_path) as db:
            result = db.query("SELECT * FROM users LIMIT 3")
            self.assertEqual(result["row_count"], 3)
            self.assertIn("name", result["headers"])

    def test_query_aggregate(self):
        """Test aggregate query."""
        with SQLiteExplorer(self.db_path) as db:
            result = db.query("SELECT COUNT(*) as cnt FROM users")
            self.assertEqual(result["rows"][0][0], 5)

    def test_query_join(self):
        """Test JOIN query."""
        with SQLiteExplorer(self.db_path) as db:
            result = db.query(
                "SELECT u.name, o.total FROM users u "
                "JOIN orders o ON u.id = o.user_id"
            )
            self.assertGreater(result["row_count"], 0)

    def test_query_syntax_error(self):
        """Test query with SQL syntax error."""
        with SQLiteExplorer(self.db_path) as db:
            with self.assertRaises(sqlite3.OperationalError):
                db.query("SELCT * FORM users")

    def test_query_empty_result(self):
        """Test query returning no rows."""
        with SQLiteExplorer(self.db_path) as db:
            result = db.query("SELECT * FROM users WHERE age > 1000")
            self.assertEqual(result["row_count"], 0)


class TestExport(BaseDBTest):
    """Test export_table() functionality."""

    def test_export_csv(self):
        """Test CSV export."""
        with SQLiteExplorer(self.db_path) as db:
            content = db.export_table("products", fmt="csv")
            self.assertIn("name", content)
            self.assertIn("Widget A", content)
            lines = content.strip().split("\n")
            self.assertEqual(len(lines), 5)  # header + 4 rows

    def test_export_json(self):
        """Test JSON export."""
        with SQLiteExplorer(self.db_path) as db:
            content = db.export_table("products", fmt="json")
            data = json.loads(content)
            self.assertEqual(len(data), 4)
            self.assertEqual(data[0]["name"], "Widget A")

    def test_export_markdown(self):
        """Test Markdown export."""
        with SQLiteExplorer(self.db_path) as db:
            content = db.export_table("products", fmt="md")
            self.assertIn("| name |", content)
            self.assertIn("| Widget A |", content)

    def test_export_to_file(self):
        """Test export to file."""
        output_path = os.path.join(self.temp_dir, "export.csv")
        with SQLiteExplorer(self.db_path) as db:
            db.export_table("products", fmt="csv", output=output_path)
            self.assertTrue(os.path.exists(output_path))
            content = Path(output_path).read_text()
            self.assertIn("Widget A", content)

    def test_export_with_query(self):
        """Test export with custom query."""
        with SQLiteExplorer(self.db_path) as db:
            content = db.export_table(
                "products", fmt="json",
                query_sql="SELECT name, price FROM products WHERE price > 20"
            )
            data = json.loads(content)
            self.assertEqual(len(data), 2)  # Gadget X, Tool Y

    def test_export_nonexistent_table(self):
        """Test export of nonexistent table."""
        with SQLiteExplorer(self.db_path) as db:
            with self.assertRaises(ValueError):
                db.export_table("nonexistent", fmt="csv")


class TestGetStats(BaseDBTest):
    """Test get_stats() functionality."""

    def test_stats_returns_list(self):
        """Test stats returns a list of column stats."""
        with SQLiteExplorer(self.db_path) as db:
            stats = db.get_stats("users")
            self.assertIsInstance(stats, list)
            self.assertGreater(len(stats), 0)

    def test_stats_column_names(self):
        """Test stats has correct column names."""
        with SQLiteExplorer(self.db_path) as db:
            stats = db.get_stats("users")
            col_names = [s["column"] for s in stats]
            self.assertIn("name", col_names)
            self.assertIn("age", col_names)

    def test_stats_null_counts(self):
        """Test stats correctly counts NULLs."""
        with SQLiteExplorer(self.db_path) as db:
            stats = db.get_stats("users")
            age_stat = next(s for s in stats if s["column"] == "age")
            self.assertEqual(age_stat["null_count"], 1)  # Eve has NULL age

    def test_stats_distinct_counts(self):
        """Test stats correctly counts distinct values."""
        with SQLiteExplorer(self.db_path) as db:
            stats = db.get_stats("products")
            cat_stat = next(s for s in stats if s["column"] == "category")
            self.assertEqual(cat_stat["distinct"], 3)

    def test_stats_numeric_aggregates(self):
        """Test stats computes min/max/avg for numeric columns."""
        with SQLiteExplorer(self.db_path) as db:
            stats = db.get_stats("products")
            price_stat = next(s for s in stats if s["column"] == "price")
            self.assertIsNotNone(price_stat["min"])
            self.assertIsNotNone(price_stat["max"])
            self.assertIsNotNone(price_stat["avg"])

    def test_stats_nonexistent_table(self):
        """Test stats for nonexistent table."""
        with SQLiteExplorer(self.db_path) as db:
            with self.assertRaises(ValueError):
                db.get_stats("nonexistent")


class TestSearch(BaseDBTest):
    """Test search() functionality."""

    def test_search_finds_match(self):
        """Test search finds matching text."""
        with SQLiteExplorer(self.db_path) as db:
            matches = db.search("Alice")
            self.assertGreater(len(matches), 0)
            self.assertEqual(matches[0]["table"], "users")

    def test_search_case_insensitive(self):
        """Test search is case-insensitive."""
        with SQLiteExplorer(self.db_path) as db:
            matches = db.search("alice")
            self.assertGreater(len(matches), 0)

    def test_search_across_tables(self):
        """Test search across multiple tables."""
        with SQLiteExplorer(self.db_path) as db:
            matches = db.search("Widget")
            self.assertGreater(len(matches), 0)
            tables = set(m["table"] for m in matches)
            self.assertIn("products", tables)

    def test_search_with_table_filter(self):
        """Test search limited to specific tables."""
        with SQLiteExplorer(self.db_path) as db:
            matches = db.search("Alice", tables=["products"])
            self.assertEqual(len(matches), 0)

    def test_search_no_match(self):
        """Test search with no matches."""
        with SQLiteExplorer(self.db_path) as db:
            matches = db.search("XYZNONEXISTENT123")
            self.assertEqual(len(matches), 0)

    def test_search_with_limit(self):
        """Test search respects limit."""
        with SQLiteExplorer(self.db_path) as db:
            matches = db.search("e", limit=2)  # 'e' appears in many names
            self.assertLessEqual(len(matches), 2)

    def test_search_matched_columns(self):
        """Test search reports matched columns."""
        with SQLiteExplorer(self.db_path) as db:
            matches = db.search("alice@example.com")
            if matches:
                self.assertIn("email", matches[0]["matched_columns"])


class TestGetSize(BaseDBTest):
    """Test get_size() functionality."""

    def test_size_returns_dict(self):
        """Test size returns a dictionary."""
        with SQLiteExplorer(self.db_path) as db:
            size = db.get_size()
            self.assertIsInstance(size, dict)

    def test_size_has_file_size(self):
        """Test size includes file size."""
        with SQLiteExplorer(self.db_path) as db:
            size = db.get_size()
            self.assertGreater(size["file_size"], 0)

    def test_size_has_tables(self):
        """Test size includes table breakdown."""
        with SQLiteExplorer(self.db_path) as db:
            size = db.get_size()
            self.assertEqual(len(size["tables"]), 3)

    def test_size_page_info(self):
        """Test size includes page information."""
        with SQLiteExplorer(self.db_path) as db:
            size = db.get_size()
            self.assertGreater(size["page_count"], 0)
            self.assertGreater(size["page_size"], 0)


class TestDiff(BaseDBTest):
    """Test diff() functionality."""

    def test_diff_identical(self):
        """Test diffing identical databases."""
        with SQLiteExplorer(self.db_path) as db:
            result = db.diff(self.db_path)
            self.assertTrue(result["identical_schema"])

    def test_diff_different_tables(self):
        """Test diffing databases with different tables."""
        # Create a different database
        other_path = os.path.join(self.temp_dir, "other.db")
        conn = sqlite3.connect(other_path)
        conn.execute("CREATE TABLE different_table (id INTEGER PRIMARY KEY)")
        conn.commit()
        conn.close()

        with SQLiteExplorer(self.db_path) as db:
            result = db.diff(other_path)
            self.assertFalse(result["identical_schema"])
            self.assertGreater(len(result["tables_only_in_a"]), 0)
            self.assertIn("different_table", result["tables_only_in_b"])

    def test_diff_nonexistent_other(self):
        """Test diffing with nonexistent other database."""
        with SQLiteExplorer(self.db_path) as db:
            with self.assertRaises(FileNotFoundError):
                db.diff("/nonexistent/db.sqlite")


class TestVacuum(BaseDBTest):
    """Test vacuum() functionality."""

    def test_vacuum_runs(self):
        """Test vacuum executes successfully."""
        with SQLiteExplorer(self.db_path) as db:
            result = db.vacuum()
            self.assertIn("before_size", result)
            self.assertIn("after_size", result)
            self.assertIn("saved", result)

    def test_vacuum_before_after(self):
        """Test vacuum reports before/after sizes."""
        with SQLiteExplorer(self.db_path) as db:
            result = db.vacuum()
            self.assertGreater(result["before_size"], 0)
            self.assertGreater(result["after_size"], 0)


class TestEdgeCases(BaseDBTest):
    """Test edge cases and special scenarios."""

    def test_empty_database(self):
        """Test with empty database (no tables)."""
        empty_path = os.path.join(self.temp_dir, "empty.db")
        conn = sqlite3.connect(empty_path)
        conn.close()

        with SQLiteExplorer(empty_path) as db:
            tables = db.get_tables()
            self.assertEqual(len(tables), 0)
            info = db.get_info()
            self.assertEqual(info["table_count"], 0)

    def test_empty_table(self):
        """Test with table that has no rows."""
        empty_path = os.path.join(self.temp_dir, "empty_table.db")
        conn = sqlite3.connect(empty_path)
        conn.execute("CREATE TABLE empty (id INTEGER PRIMARY KEY, name TEXT)")
        conn.commit()
        conn.close()

        with SQLiteExplorer(empty_path) as db:
            result = db.browse("empty")
            self.assertEqual(len(result["rows"]), 0)
            stats = db.get_stats("empty")
            self.assertEqual(stats[0]["non_null"], 0)

    def test_blob_data(self):
        """Test handling of BLOB data."""
        with SQLiteExplorer(self.db_path) as db:
            # Bob has a BLOB avatar
            result = db.browse("users", where="name = 'Bob Jones'")
            self.assertEqual(len(result["rows"]), 1)
            # BLOB should be in the row (avatar column index 6)
            avatar = result["rows"][0][6]
            self.assertIsInstance(avatar, bytes)

    def test_null_values_in_browse(self):
        """Test NULL values are handled in browse."""
        with SQLiteExplorer(self.db_path) as db:
            result = db.browse("users", where="email IS NULL")
            self.assertEqual(len(result["rows"]), 1)
            self.assertEqual(result["rows"][0][1], "Eve Adams")

    def test_very_long_string(self):
        """Test handling of very long string values."""
        long_path = os.path.join(self.temp_dir, "long.db")
        conn = sqlite3.connect(long_path)
        conn.execute("CREATE TABLE data (id INTEGER PRIMARY KEY, text TEXT)")
        conn.execute("INSERT INTO data VALUES (1, ?)", ("A" * 10000,))
        conn.commit()
        conn.close()

        with SQLiteExplorer(long_path) as db:
            result = db.browse("data")
            self.assertEqual(len(result["rows"]), 1)
            # Export should contain full data
            content = db.export_table("data", fmt="json")
            data = json.loads(content)
            self.assertEqual(len(data[0]["text"]), 10000)

    def test_special_characters_in_data(self):
        """Test handling of special characters."""
        special_path = os.path.join(self.temp_dir, "special.db")
        conn = sqlite3.connect(special_path)
        conn.execute("CREATE TABLE data (id INTEGER PRIMARY KEY, text TEXT)")
        conn.execute("INSERT INTO data VALUES (1, ?)", ('He said "hello" & <goodbye>',))
        conn.commit()
        conn.close()

        with SQLiteExplorer(special_path) as db:
            result = db.browse("data")
            self.assertEqual(len(result["rows"]), 1)

    def test_many_columns(self):
        """Test table with many columns."""
        many_path = os.path.join(self.temp_dir, "many_cols.db")
        conn = sqlite3.connect(many_path)
        cols = ", ".join("col%d TEXT" % i for i in range(50))
        conn.execute("CREATE TABLE wide (id INTEGER PRIMARY KEY, %s)" % cols)
        vals = ", ".join("'val%d'" % i for i in range(50))
        conn.execute("INSERT INTO wide VALUES (1, %s)" % vals)
        conn.commit()
        conn.close()

        with SQLiteExplorer(many_path) as db:
            schema = db.get_schema("wide")
            self.assertEqual(len(schema[0]["columns"]), 51)  # id + 50 cols


class TestIntegration(BaseDBTest):
    """Integration tests for full workflows."""

    def test_full_inspection_workflow(self):
        """Test complete inspection: info -> tables -> schema -> browse."""
        with SQLiteExplorer(self.db_path) as db:
            # Step 1: Info
            info = db.get_info()
            self.assertEqual(info["table_count"], 3)

            # Step 2: Tables
            tables = db.get_tables()
            self.assertEqual(len(tables), 3)

            # Step 3: Schema
            schema = db.get_schema("users")
            self.assertGreater(len(schema[0]["columns"]), 0)

            # Step 4: Browse
            result = db.browse("users", limit=3)
            self.assertEqual(len(result["rows"]), 3)

    def test_export_all_formats(self):
        """Test exporting in all formats."""
        with SQLiteExplorer(self.db_path) as db:
            csv_out = db.export_table("products", fmt="csv")
            json_out = db.export_table("products", fmt="json")
            md_out = db.export_table("products", fmt="md")

            self.assertIn("Widget A", csv_out)
            self.assertIn("Widget A", json_out)
            self.assertIn("Widget A", md_out)

            # Verify JSON is valid
            data = json.loads(json_out)
            self.assertEqual(len(data), 4)

    def test_search_and_browse(self):
        """Test search then browse workflow."""
        with SQLiteExplorer(self.db_path) as db:
            # Search
            matches = db.search("Electronics")
            self.assertGreater(len(matches), 0)

            # Browse matching table
            result = db.browse("products", where="category = 'Electronics'")
            self.assertEqual(len(result["rows"]), 2)

    def test_stats_all_tables(self):
        """Test getting stats for all tables."""
        with SQLiteExplorer(self.db_path) as db:
            tables = db.get_tables()
            for t in tables:
                stats = db.get_stats(t["name"])
                self.assertGreater(len(stats), 0)

    def test_large_data(self):
        """Test with a larger dataset."""
        large_path = os.path.join(self.temp_dir, "large.db")
        conn = sqlite3.connect(large_path)
        conn.execute("CREATE TABLE data (id INTEGER PRIMARY KEY, value TEXT, num REAL)")
        rows = [(i, "item_%d" % i, float(i) * 1.5) for i in range(1000)]
        conn.executemany("INSERT INTO data VALUES (?, ?, ?)", rows)
        conn.commit()
        conn.close()

        with SQLiteExplorer(large_path) as db:
            tables = db.get_tables()
            self.assertEqual(tables[0]["row_count"], 1000)

            result = db.browse("data", limit=10)
            self.assertEqual(len(result["rows"]), 10)

            stats = db.get_stats("data")
            num_stat = next(s for s in stats if s["column"] == "num")
            self.assertIsNotNone(num_stat["avg"])

    def test_multiple_databases(self):
        """Test working with multiple databases in sequence."""
        db2_path = os.path.join(self.temp_dir, "db2.db")
        conn = sqlite3.connect(db2_path)
        conn.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, data TEXT)")
        conn.execute("INSERT INTO items VALUES (1, 'test')")
        conn.commit()
        conn.close()

        with SQLiteExplorer(self.db_path) as db1:
            tables1 = db1.get_tables()
            self.assertEqual(len(tables1), 3)

        with SQLiteExplorer(db2_path) as db2:
            tables2 = db2.get_tables()
            self.assertEqual(len(tables2), 1)


# =============================================================================
# TEST RUNNER
# =============================================================================

def run_tests():
    """Run all tests with clear output."""
    print("=" * 70)
    print("TESTING: SQLiteExplorer v%s" % __version__ if '__version__' in dir() else "1.0.0")
    print("=" * 70)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestHelpers,
        TestTableFormatter,
        TestSQLiteExplorerInit,
        TestGetInfo,
        TestGetTables,
        TestGetSchema,
        TestBrowse,
        TestQuery,
        TestExport,
        TestGetStats,
        TestSearch,
        TestGetSize,
        TestDiff,
        TestVacuum,
        TestEdgeCases,
        TestIntegration,
    ]

    for cls in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 70)
    passed = result.testsRun - len(result.failures) - len(result.errors)
    print("RESULTS: %d tests run" % result.testsRun)
    print("[OK] Passed: %d" % passed)
    if result.failures:
        print("[X] Failed: %d" % len(result.failures))
    if result.errors:
        print("[X] Errors: %d" % len(result.errors))
    print("=" * 70)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
