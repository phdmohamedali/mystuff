# Simple Way to prvoide Row Level Security for AI-Generated SQL

## Overview

This source code provides a solution for securing AI generated SQL queries used in web applications by ensuring they only access data related to a specific company, identified by `company_id = {company_id comming from session}`. This script rewrites SQL queries by wrapping all table references with subqueries that filter results based on the `company_id` field.

The solution is implemented using the `sqlglot` library to parse, modify, and regenerate SQL queries. It supports both basic SQL queries and more complex ones with joins, subqueries, and aliases. The transformation ensures that the queries are secure and scoped to a single company, preventing unauthorized access to data.

## Features

- **Automatic Filtering**: Every table in the SQL query is wrapped with a subquery that filters by `company_id = (company_id)`, ensuring security.
- **Preserved Schema**: The schema qualifications of the original tables are maintained.
- **Normalization**: The solution normalizes SQL for consistency and comparison, making it easy to ensure that queries are transformed correctly.

## Requirements

Before running the script, you need the following:

- **Python 3.x**: The script is written in Python and requires version 3.x.
- **sqlglot**: This library is used for parsing and transforming SQL queries.

To install `sqlglot`, run:

```bash
pip install sqlglot
```

## How It Works

1. **Input SQL Query**: The script takes a raw SQL query as input.
2. **SQL Parsing**: The query is parsed using `sqlglot`, which generates an Abstract Syntax Tree (AST) for the SQL.
3. **Table Transformation**: The `wrap_table_with_filter` function recursively walks through the AST and replaces every table with a subquery that applies a filter (`WHERE company_id = 1`).
4. **Query Regeneration**: After modifying the AST, the query is regenerated with the necessary changes.
5. **Output**: The transformed SQL query is output with the required security constraints.

## How to Run

1. **Clone the Repository**:

```bash
git clone https://github.com/your-repository/sql-query-secure.git
cd sql-query-secure
```

2. **Install Dependencies**:

```bash
pip install -r requirements.txt
```

3. **Run the Script**:

You can run the script directly by passing a SQL query string. Here is an example:

```python
from sqlglot import parse_one
from sqlglot.expressions import Table, Subquery, Alias

def wrap_table_with_filter(expression):
    # Function code from above...
    pass

def transform_sql(sql):
    # Function code from above...
    pass

# Example SQL Query
sql = "SELECT * FROM x.customers JOIN x.orders b ON a.id = b.customer_id"
transformed_sql = transform_sql(sql)
print(transformed_sql)
```

### Example Output

For an input like:

```sql
SELECT * FROM x.customers JOIN x.orders b ON a.id = b.customer_id
```

The transformed output will be:

```sql
SELECT a.id, b.name
FROM (SELECT * FROM x.customers WHERE company_id = 1) as customers
JOIN (SELECT * FROM x.orders WHERE company_id = 1) as b ON a.id = b.customer_id
```

This ensures that the query is scoped to data from `company_id = 1`, improving security.

## Test Cases

Here are some test cases demonstrating how different SQL queries are transformed:

### Simple `FROM` Clause

Input:

```sql
SELECT * FROM dataset.customers
```

Output:

```sql
SELECT * FROM (SELECT * FROM dataset.customers WHERE company_id = 1) as customers
```

### SQL with Nested Queries

Input:

```sql
SELECT count(*)/count(select count(x) from dataset.x WHERE company_id = 1) 
FROM dataset.customers
```

Output:

```sql
SELECT count(*)/count(select count(x) from (select * from dataset.x WHERE company_id = 1) as x where  company_id = 1) 
FROM  (select * from dataset.customers WHERE company_id = 1) as customers
```

### SQL with Joins and Aliases

Input:

```sql
SELECT a.id, b.name 
FROM x.customers 
JOIN x.orders b ON a.id = b.customer_id
```

Output:

```sql
SELECT a.id, b.name
FROM (SELECT * FROM x.customers WHERE company_id = 1) as customers
JOIN (SELECT * FROM x.orders WHERE company_id = 1) as b ON a.id = b.customer_id
```

### SQL with Subqueries in `SELECT` Clause

Input:

```sql
SELECT 
    COUNT(*) AS count3, 
    (SELECT COUNT(*) FROM table2) AS count4
FROM table1
```

Output:

```sql
SELECT 
    COUNT(*) AS count3, 
    (SELECT COUNT(*) FROM (SELECT * FROM table2 WHERE company_id = 1)) AS count4
FROM (SELECT * FROM table1 WHERE company_id = 1)
```

## Conclusion

This solution provides an easy way to ensure that your web application’s SQL queries are secure by automatically filtering data based on `company_id`. By leveraging `sqlglot`, we provide an AI-powered transformation that handles various complexities like joins, subqueries, and aliases. With this, you can safeguard your application from unauthorized access to sensitive data while maintaining a clean and efficient SQL codebase.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Feel free to enhance, customize, and scale this solution based on your organization's specific needs!