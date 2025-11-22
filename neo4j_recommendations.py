# neo4j_recommendations.py

from neo4j import GraphDatabase
import pandas as pd
from tableauhyperapi import (
    HyperProcess, Connection, TableDefinition, SqlType,
    Telemetry, TableName, Inserter
)
from tqdm import tqdm

# -----------------------------
# ⚙️ Neo4j connection details
# -----------------------------
uri = "bolt://localhost:7687"   # Neo4j URI
user = "neo4j"
password = "test1234"
database = "reviews"            # Database name

driver = GraphDatabase.driver(uri, auth=(user, password))

# -----------------------------
# 🧠 Recommendation query
# -----------------------------
def run_batched_recommendations(batch_size=50):
    all_rows = []

    with driver.session(database=database) as session:
        # Count total users that are not processed
        total_users = session.run("""
            MATCH (u:User) WHERE u.processed IS NULL
            RETURN count(u) AS total
        """).single()["total"]

        print(f"Total unprocessed users: {total_users}")

        progress_bar = tqdm(total=total_users, desc="Processing users", unit="users")

        while True:
            # Run batched query
            result = session.run(f"""
                MATCH (target:User)
                WHERE target.processed IS NULL
                WITH target LIMIT {batch_size}

                MATCH (target)-[:WROTE]->(:Review)-[:REVIEWS]->(p:Product)
                WITH target, COLLECT(p) AS targetProducts

                MATCH (other:User)-[:WROTE]->(:Review)-[:REVIEWS]->(op:Product)
                WHERE other <> target AND op IN targetProducts
                WITH target, targetProducts, other, COUNT(op) AS shared_products
                WHERE shared_products > 0

                MATCH (other)-[:WROTE]->(:Review)-[:REVIEWS]->(rec:Product)
                WHERE NOT rec IN targetProducts

                WITH target.user_id AS UserID, rec.asin AS RecommendedProductID,
                     rec.title AS RecommendedProduct,
                     SUM(shared_products) AS similarity_score,
                     AVG(rec.average_rating) AS avg_rating
                ORDER BY similarity_score DESC, avg_rating DESC
                LIMIT 10

                RETURN UserID, RecommendedProductID, RecommendedProduct, similarity_score, avg_rating
            """)

            rows = [record.data() for record in result]

            if not rows:
                break

            all_rows.extend(rows)

            # Mark users as processed
            session.run(f"""
                MATCH (target:User)
                WHERE target.processed IS NULL
                WITH target LIMIT {batch_size}
                SET target.processed = true
            """)

            progress_bar.update(batch_size)

        progress_bar.close()

    return all_rows


# -----------------------------
# 💾 Export to CSV
# -----------------------------
def export_to_csv(rows, filename="recommendations.csv"):
    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"✅ Exported recommendations to {filename}")
    return df


# -----------------------------
# 📊 Export to Tableau Hyper
# -----------------------------
def export_to_hyper(df, hyper_path="recommendations.hyper"):
    with HyperProcess(telemetry=Telemetry.SEND_USAGE_DATA_TO_TABLEAU) as hyper:
        table = TableDefinition(
            table_name=TableName("Extract", "Recommendations"),
            columns=[
                TableDefinition.Column("UserID", SqlType.text()),
                TableDefinition.Column("RecommendedProductID", SqlType.text()),
                TableDefinition.Column("RecommendedProduct", SqlType.text()),
                TableDefinition.Column("similarity_score", SqlType.double()),
                TableDefinition.Column("avg_rating", SqlType.double())
            ]
        )

        with Connection(endpoint=hyper.endpoint, database=hyper_path, create_mode=True) as conn:
            # ✅ Create schema before table
            conn.catalog.create_schema("Extract")

            # Create table inside schema
            conn.catalog.create_table(table)

            # Insert data
            with Inserter(conn, table) as inserter:
                inserter.add_rows(df.values.tolist())
                inserter.execute()

        print(f"✅ Exported recommendations to {hyper_path}")


# -----------------------------
# 🚀 Main Execution
# -----------------------------
if __name__ == "__main__":
    print("Starting batched recommendation query...")

    rows = run_batched_recommendations(batch_size=50)

    if not rows:
        print("No new users to process — all users are already processed.")
    else:
        df = export_to_csv(rows)
        export_to_hyper(df)

    print("🎉 All done!")
