from neo4j import GraphDatabase
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time

# ----------------------------
# Neo4j Connection
# ----------------------------
URI = "bolt://localhost:7687"  # Default Neo4j Bolt port
AUTH = ("neo4j", "1234")       # Change if needed
DATABASE = "reviews"           # ✅ your database name

driver = GraphDatabase.driver(URI, auth=AUTH)

# ----------------------------
# CONFIGURATION
# ----------------------------
BATCH_SIZE = 200        # users per batch
MAX_WORKERS = 6         # threads
MAX_USERS = 2000        # max total users to process
SLEEP_BETWEEN_BATCHES = 2  # seconds delay between batches

# ----------------------------
# MULTIHOP RECOMMENDATION QUERY
# ----------------------------
MULTIHOP_QUERY = """
MATCH (u:User {user_id: $user_id})
MATCH (u)-[:WROTE]->(:Review)-[:REVIEWS]->(p:Product)<-[:REVIEWS]-(:Review)<-[:WROTE]-(other:User)
WHERE u <> other
WITH DISTINCT other AS potential_users
MATCH (potential_users)-[:WROTE]->(:Review)-[:REVIEWS]->(rec_prod:Product)
WHERE NOT (u)-[:WROTE]->(:Review)-[:REVIEWS]->(rec_prod)
RETURN DISTINCT rec_prod.asin AS recommended_asin
LIMIT 10
"""

# ----------------------------
# FETCH USERS TO PROCESS
# ----------------------------
def fetch_users_to_process(limit=MAX_USERS):
    with driver.session(database=DATABASE) as session:
        result = session.run("""
            MATCH (u:User)
            WHERE u.processed IS NULL
            RETURN u.user_id AS user_id
            LIMIT $limit
        """, limit=limit)
        return [r["user_id"] for r in result]

# ----------------------------
# PROCESS ONE USER
# ----------------------------
def process_user(user_id):
    with driver.session(database=DATABASE) as session:
        try:
            recs = session.run(MULTIHOP_QUERY, user_id=user_id)
            recommended_asins = [r["recommended_asin"] for r in recs]

            session.run("""
                MATCH (u:User {user_id: $user_id})
                SET u.recommendations = $recs, u.processed = true
            """, user_id=user_id, recs=recommended_asins)

            return f"✅ {user_id} ({len(recommended_asins)} recs)"
        except Exception as e:
            return f"❌ {user_id}: {e}"

# ----------------------------
# MAIN PARALLEL EXECUTION
# ----------------------------
def process_batches():
    all_users = fetch_users_to_process()
    total_users = len(all_users)
    print(f"\nTotal users to process: {total_users}\n")

    for i in range(0, total_users, BATCH_SIZE):
        batch = all_users[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        print(f"\n🧩 Batch {batch_num}: Processing {len(batch)} users...")

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(process_user, u) for u in batch]

            for f in tqdm(as_completed(futures), total=len(futures), desc=f"Batch {batch_num}", ncols=100):
                result = f.result()
                tqdm.write(result)

        print(f"✅ Batch {batch_num} done.\n")
        time.sleep(SLEEP_BETWEEN_BATCHES)

# ----------------------------
# RUN SCRIPT
# ----------------------------
if __name__ == "__main__":
    start_time = time.time()
    process_batches()
    print(f"\n🎯 Completed in {round(time.time() - start_time, 2)} seconds.")
    driver.close()
