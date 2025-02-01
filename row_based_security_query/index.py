import sqlglot
from sqlglot import parse_one
from sqlglot.expressions import Table, Subquery, Alias

def wrap_table_with_filter(expression):
    """
    Recursively traverse the SQL AST and replace table references
    with a subquery that filters by company_id = 1.
    Preserve schema qualification.
    """
    if isinstance(expression, Table):
        table_name = expression.name
        schema_name = expression.db or ""  # Ensure schema is correctly preserved
        full_table_name = f"{schema_name}.{table_name}" if schema_name else table_name
        
        subquery = Subquery(this=parse_one(f"SELECT * FROM {full_table_name} WHERE company_id = 1"))
        
        return Alias(this=subquery, alias=expression.alias or table_name)
    
    for key, value in expression.args.items():
        if isinstance(value, list):
            expression.args[key] = [wrap_table_with_filter(sub) for sub in value]
        elif isinstance(value, sqlglot.Expression):
            expression.args[key] = wrap_table_with_filter(value)
    
    return expression

def transform_sql(sql):
    """
    Parse and transform SQL by wrapping each table in a subquery while keeping schema qualifications.
    """
    parsed = parse_one(sql)
    transformed = wrap_table_with_filter(parsed)
    return transformed.sql(pretty=True)

# Normalize SQL for comparison
def normalize_sql(sql):
    return "".join(sql.lower().split())

# ===============================
# Test Cases
# ===============================
test_cases = [
    # Simple FROM clause
    ("SELECT * FROM dataset.customers", 
     "SELECT * FROM (SELECT * FROM dataset.customers WHERE company_id = 1) as customers"),
   
    ("SELECT count(*)/count(select count(x) from dataset.x WHERE company_id = 1) FROM dataset.customers", 
     "SELECT count(*)/count(select count(x) from (select * from dataset.x WHERE company_id = 1) as x where  company_id = 1) FROM  (select * from dataset.customers WHERE company_id = 1) as customers"),
    
    # JOINs with alias
    ("""
    SELECT a.id, b.name 
    FROM x.customers 
    JOIN x.orders b ON a.id = b.customer_id
    """,
    """
    SELECT a.id, b.name
    FROM (SELECT * FROM x.customers WHERE company_id = 1) as customers
    JOIN (SELECT * FROM x.orders WHERE company_id = 1) as b ON a.id = b.customer_id
    """),

    # Subquery in SELECT clause
    ("""
    SELECT 
        COUNT(*) AS count3, 
        (SELECT COUNT(*) FROM table2) AS count4
    FROM table1
    """,
    """
    SELECT 
        COUNT(*) AS count3, 
        (SELECT COUNT(*) FROM (SELECT * FROM table2 WHERE company_id = 1)) AS count4
    FROM (SELECT * FROM table1 WHERE company_id = 1)
    """),

    # # Multiple tables in FROM clause
    # ("""
    # SELECT * FROM table1, table2, table3
    # """,
    # """
    # SELECT * 
    # FROM (SELECT * FROM table1 WHERE company_id = 1), 
    #      (SELECT * FROM table2 WHERE company_id = 1), 
    #      (SELECT * FROM table3 WHERE company_id = 1)
    # """),

    # # CTE with filtering
    # ("""
    # WITH cte AS (
    #     SELECT id, name FROM customers WHERE active = 1
    # )
    # SELECT * FROM cte
    # """,
    # """
    # WITH cte AS (
    #     SELECT id, name FROM (SELECT * FROM customers WHERE company_id = 1) WHERE active = 1
    # )
    # SELECT * FROM (SELECT * FROM cte WHERE company_id = 1)
    # """),

    # # Nested subqueries
    # ("""
    # SELECT * FROM (SELECT id, name FROM employees) AS sub
    # """,
    # """
    # SELECT * FROM (SELECT id, name FROM (SELECT * FROM employees WHERE company_id = 1)) AS sub
    # """),

    # # EXISTS clause handling
    # ("""
    # SELECT id FROM users WHERE EXISTS (SELECT 1 FROM orders WHERE users.id = orders.user_id)
    # """,
    # """
    # SELECT id FROM (SELECT * FROM users WHERE company_id = 1)
    # WHERE EXISTS (SELECT 1 FROM (SELECT * FROM orders WHERE company_id = 1) WHERE users.id = orders.user_id)
    # """)
]

# Run test cases
for i, (input_sql, expected_sql) in enumerate(test_cases, 1):
    transformed_sql = transform_sql(input_sql)
    print(f"Test Case {i}: {'PASS' if normalize_sql(transformed_sql) == normalize_sql(expected_sql) else 'FAIL'}")
    print("Input SQL:\n", normalize_sql(input_sql))
    print("Transformed SQL:\n", (transformed_sql))

    print("Transformed SQL:\n", normalize_sql(transformed_sql))
    print("Expected SQL:\n", normalize_sql(expected_sql))
    print("=" * 80)
    if i == 3:
        break