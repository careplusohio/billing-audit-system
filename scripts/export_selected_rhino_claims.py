import psycopg2
import csv

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="careplus",
    user="postgres",
    password="careplus123",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# 🔥 Only select specific columns you care about
cur.execute("""
    SELECT 
        patient_first_name,
        patient_last_name,
        patient_dob,
        total_billed,
        total_paid,
        payer,
        claim_status
    FROM rhino_claims;
""")
rows = cur.fetchall()

# Column headers
colnames = [desc[0] for desc in cur.description]

# Write to CSV
with open("rhino_claims_selected_export.csv", mode="w", newline='', encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(colnames)  # Write headers
    writer.writerows(rows)     # Write data

print("✅ Selective export completed: rhino_claims_selected_export.csv")

# Close connection
cur.close()
conn.close()
