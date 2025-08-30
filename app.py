from flask import Flask, request, jsonify, render_template
import sqlite3
import openai
import os
import re
from collections import deque, defaultdict

app = Flask(__name__, template_folder="frontend")

# --- OpenAI API key ---
openai.api_key = "Open_AI_KEY_HERE"
# --- Database ---
DB_FILE = os.path.abspath("bank.db")
print("📂 Using DB file:", DB_FILE)

# --- Load schema ---
def load_schema():
    schema = {}
    primary_keys = {}
    foreign_keys = defaultdict(list)
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        tables = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        ).fetchall()
        for (table,) in tables:
            cols = cur.execute(f"PRAGMA table_info({table});").fetchall()
            schema[table] = [col[1] for col in cols]
            for col in cols:
                if col[5]:  # PK
                    primary_keys[table] = col[1]
            fks = cur.execute(f"PRAGMA foreign_key_list({table});").fetchall()
            for fk in fks:
                foreign_keys[table].append((fk[3], fk[2], fk[4]))  # col_from, table_to, col_to
    return schema, primary_keys, foreign_keys

SCHEMA, PRIMARY_KEYS, FOREIGN_KEYS = load_schema()

# --- Build join graph ---
JOIN_GRAPH = defaultdict(list)
for table, fks in FOREIGN_KEYS.items():
    for col_from, table_to, col_to in fks:
        JOIN_GRAPH[table].append((table_to, col_from, col_to))
        JOIN_GRAPH[table_to].append((table, col_from, col_to))

# --- BFS join path ---
def find_join_path(start_tables, target_table):
    queue = deque([(t, []) for t in start_tables])
    visited = set(start_tables)
    while queue:
        current, path = queue.popleft()
        if current == target_table:
            return path
        for neighbor, col_from, col_to in JOIN_GRAPH.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [(current, neighbor, col_from, col_to)]))
    return []

# --- Generate joins with aliases ---
def generate_joins(path, alias_map, used_aliases, inner_tables=set()):
    joins_sql = []
    for left, right, left_col, right_col in path:
        left_alias = next(a for a, t in alias_map.items() if t == left)
        right_alias = next((a for a, t in alias_map.items() if t == right), None)
        if not right_alias:
            base_alias = right[:2].lower()
            right_alias = base_alias
            count = 1
            while right_alias in used_aliases:
                right_alias = f"{base_alias}{count}"
                count += 1
            alias_map[right_alias] = right
            used_aliases.add(right_alias)
        join_type = "INNER JOIN" if right in inner_tables else "LEFT JOIN"
        joins_sql.append(f"{join_type} {right} {right_alias} ON {left_alias}.{left_col} = {right_alias}.{right_col}")
    return joins_sql

# --- Run SQL ---
def run_sql(query):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cur = conn.cursor()
            cur.execute(query)
            rows = cur.fetchall()
            cols = [desc[0] for desc in cur.description] if cur.description else []
            return {"success": True, "columns": cols, "rows": rows}
    except Exception as e:
        return {"success": False, "error": str(e)}

# --- Build SQL dynamically ---
def build_sql(nlq):
    nlq_lower = nlq.lower()
    is_count_query = bool(re.search(r'\b(count|number of|total|how many)\b', nlq_lower))
    limit_match = re.search(r'\b(?:show|top)\s+(\d+)\b', nlq_lower)
    limit_number = int(limit_match.group(1)) if limit_match else None

    # --- Detect tables dynamically with fuzzy matching ---
    needed_tables = set()
    for table in SCHEMA:
        table_lower = table.lower()
        if table_lower in nlq_lower:
            needed_tables.add(table)
        elif table_lower.endswith('s') and table_lower[:-1] in nlq_lower:
            needed_tables.add(table)
        elif not table_lower.endswith('s') and table_lower + 's' in nlq_lower:
            needed_tables.add(table)
        else:
            # Also check for columns in NLQ
            for col in SCHEMA[table]:
                if col.lower() in nlq_lower:
                    needed_tables.add(table)
    if not needed_tables:
        needed_tables.add(list(SCHEMA.keys())[0])

    # --- Assign aliases dynamically ---
    alias_map = {}
    used_aliases = set()
    for table in sorted(needed_tables):
        base_alias = table[:2].lower()
        alias = base_alias
        count = 1
        while alias in used_aliases:
            alias = f"{base_alias}{count}"
            count += 1
        alias_map[alias] = table
        used_aliases.add(alias)

    # --- Determine main table ---
    main_table = sorted(list(needed_tables))[0]
    main_alias = next(a for a, t in alias_map.items() if t == main_table)

    # --- Generate joins dynamically ---
    joins_sql = []
    added_tables = {main_table}
    for table in needed_tables:
        if table in added_tables:
            continue
        path = find_join_path(list(added_tables), table)
        if path:
            joins_sql += generate_joins(path, alias_map, used_aliases, inner_tables=needed_tables)
            added_tables.update([right for _, right, _, _ in path])

    from_clause = f"FROM {main_table} {main_alias}\n" + "\n".join(joins_sql)

    # --- Deduplicate columns dynamically ---
    select_cols = []
    added_cols = set()
    for alias, table in alias_map.items():
        for col in SCHEMA[table]:
            if col not in added_cols:
                select_cols.append(f"{alias}.{col}")
                added_cols.add(col)

    # --- COUNT query ---
    if is_count_query:
        pk = PRIMARY_KEYS.get(main_table, list(SCHEMA[main_table])[0])
        select_clause = f"COUNT(DISTINCT {main_alias}.{pk}) AS customer_count"
    else:
        select_clause = ",\n    ".join(select_cols)

    # --- Dynamic WHERE clause for any column=value ---
    where_clauses = []
    pattern = r'(\w+)\s+is\s+([^\s,]+)'
    matches = re.findall(pattern, nlq_lower)
    for col_name, value in matches:
        for alias, table in alias_map.items():
            if col_name in [c.lower() for c in SCHEMA[table]]:
                if '@' in value or not value.isdigit():  # treat as string
                    value_formatted = f"'{value}'"
                else:
                    value_formatted = value
                where_clauses.append(f"{alias}.{col_name} = {value_formatted}")
                break

    where_clause = ""
    if where_clauses:
        where_clause = "WHERE " + " AND ".join(where_clauses)

    # --- Assemble final SQL ---
    sql = f"SELECT\n    {select_clause}\n{from_clause}"
    if where_clause:
        sql += f"\n{where_clause}"
    if limit_number and not is_count_query:
        sql += f"\nLIMIT {limit_number}"

    return sql

# --- Flask routes ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/query", methods=["POST"])
def query():
    try:
        data = request.json
        nlq = data.get("nlq", "")
        sql = build_sql(nlq)
        print("🔎 Generated SQL:", sql)
        result = run_sql(sql)
        return jsonify({"nlq": nlq, "sql": sql, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
