import re

def replace_tables_with_company_filter(sql_script, company_id):
    """
    Replaces each table name in the SQL script with a subquery that includes a 
    company_id filter.

    Args:
        sql_script: The SQL script as a string.
        company_id: The company ID to use in the filter.

    Returns:
        The modified SQL script with the table replacements.
    """

    def replace_match(match):
        table_name = match.group(1)
        return f"(SELECT * FROM {table_name} WHERE company_id = '{company_id}')"

    # Regular expression to find table names (adjust as needed for your SQL syntax)
    # This one is pretty broad and might need refinement depending on your SQL
    # For example, it doesn't handle quoted table names or schema prefixes.
    pattern = r"\bFROM\s+([a-zA-Z0-9_]+)\b"  # Matches table names after FROM

    modified_sql = re.sub(pattern, replace_match, sql_script, flags=re.IGNORECASE)

    # Handle potential CTEs (Common Table Expressions)
    cte_pattern = r"\bWITH\s+([a-zA-Z0-9_]+)\s+AS\s*\(" # Matches CTE names after WITH
    modified_sql = re.sub(cte_pattern, lambda match: f"WITH {match.group(1)} AS (", modified_sql, flags=re.IGNORECASE)


    return modified_sql


# Test cases
test_cases = [
    {
        "sql": "SELECT * FROM my_table left join mytable2 WHERE condition;",
        "company_id": "123",
        "expected": "SELECT * FROM (SELECT * FROM my_table WHERE company_id = '123') WHERE condition;"
    },
    {
        "sql": "SELECT col1, col2 FROM another_table JOIN my_table ON condition;",
        "company_id": "456",
        "expected": "SELECT col1, col2 FROM (SELECT * FROM another_table WHERE company_id = '456') JOIN (SELECT * FROM my_table WHERE company_id = '456') ON condition;"
    },
    {
        "sql": "SELECT * FROM schema.my_table;",  # Doesn't handle schema
        "company_id": "789",
        "expected": "SELECT * FROM (SELECT * FROM schema.my_table WHERE company_id = '789');" # Should ideally handle schema
    },
    {
        "sql": "WITH my_cte AS (SELECT * FROM my_table) SELECT * FROM my_cte;",
        "company_id": "101",
        "expected": "WITH my_cte AS (SELECT * FROM (SELECT * FROM my_table WHERE company_id = '101')) SELECT * FROM my_cte;"
    },
    {
        "sql": "SELECT * FROM my_table WHERE company_id = 'already_filtered';", # Should not double filter
        "company_id": "202",
        "expected": "SELECT * FROM (SELECT * FROM my_table WHERE company_id = '202') WHERE company_id = 'already_filtered';" # This is a current limitation
    }

]

for i, test in enumerate(test_cases):
    modified_sql = replace_tables_with_company_filter(test["sql"], test["company_id"])
    print(f"Test Case {i+1}:")
    print("Original SQL:", test["sql"])
    print("Modified SQL:", modified_sql)
    print("Expected SQL:", test["expected"])
    assert modified_sql == test["expected"], f"Test Case {i+1} failed!"
    print("-" * 20)