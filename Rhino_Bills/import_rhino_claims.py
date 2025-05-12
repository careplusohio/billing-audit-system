import pandas as pd
import psycopg2
from psycopg2 import sql

# Database connection settings
DB_NAME = "careplus"
DB_USER = "postgres"
DB_PASSWORD = "careplus123"
DB_HOST = "localhost"
DB_PORT = "5432"

# Load the Excel file
excel_file = "rhino.xlsx"
df = pd.read_excel(excel_file)

# Clean column names to match the table fields
df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

# Insert data row by row
for idx, row in df.iterrows():
    columns = list(row.index)
    values = [row[col] for col in columns]
    insert_query = sql.SQL("""
        INSERT INTO rhino_claims ({})
        VALUES ({})
    """).format(
        sql.SQL(', ').join(map(sql.Identifier, columns)),
        sql.SQL(', ').join(sql.Placeholder() * len(values))
    )
    cur.execute(insert_query, values)

conn.commit()
cur.close()
conn.close()

print("✅ Successfully imported data into rhino_claims table.")
