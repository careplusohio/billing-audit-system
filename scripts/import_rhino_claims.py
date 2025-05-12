import psycopg2
import pandas as pd

try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        dbname="careplus",
        user="postgres",
        password="careplus123",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()

    # Load Excel
    df = pd.read_excel("rhino.xlsx")

    # Insert into database
    for index, row in df.iterrows():
        insert_query = """
            INSERT INTO rhino_claims (
                trading_partner_id,
                rb_ref_num,
                patient_id,
                patient_first_name,
                patient_last_name,
                patient_dob,
                date_of_service,
                total_charges,
                claim_status,
                paid_amount,
                denial_reason,
                rb_claim_id,
                edi_file_id,
                edi_file_name,
                provider_name,
                payer_provider_id,
                provider_npi,
                patient_payer_id,
                original_claim_id,
                adjustment_claim_id,
                icn,
                payer,
                payer_type,
                procedure_code,
                created_date,
                service_begin_date,
                service_end_date,
                total_hours,
                total_units,
                patient_responsibility,
                total_billed,
                total_paid,
                paycheck_date,
                patient_sex,
                patient_address_1,
                patient_address_2,
                patient_city,
                patient_state,
                patient_zip,
                prior_authorization,
                discharge_date,
                diagnosis_1,
                diagnosis_2,
                diagnosis_3,
                diagnosis_4,
                orp_first_name,
                orp_last_name,
                orp_npi,
                accident_type
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            );
        """
        values = tuple(row)

        cur.execute(insert_query, values)

    conn.commit()
    print("✅ rhino.xlsx imported successfully into rhino_claims table!")

except Exception as e:
    print("❌ Import failed:", e)

finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()
