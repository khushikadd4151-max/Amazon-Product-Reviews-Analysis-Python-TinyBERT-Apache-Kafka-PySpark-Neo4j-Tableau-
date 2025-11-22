import json
import time
import uuid
from kafka import KafkaConsumer
from neo4j import GraphDatabase

# --- Configuration ---
KAFKA_TOPIC = "amazon_reviews"
KAFKA_SERVER = "localhost:9092"
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "test1234"

# --- Connect to Neo4j ---
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# --- Kafka Consumer ---
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=[KAFKA_SERVER],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='neo4j-streaming-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("🎧 Listening to Kafka topic and streaming to Neo4j in batches...")

# --- Helper function to insert into Neo4j ---
def insert_batch(tx, reviews):
    for review in reviews:
        try:
            # Ensure review_id exists (for unique merge)
            if not review.get("review_id"):
                user = review.get("user_id", "unknown")
                asin = review.get("asin", "unknown")
                ts = review.get("timestamp", str(time.time()))
                review["review_id"] = f"{user}_{asin}_{ts}_{uuid.uuid4().hex[:6]}"

            tx.run("""
                MERGE (u:User {user_id: $user_id})
                MERGE (p:Product {asin: $asin})
                SET p.title = $title_y,
                    p.category = $category,
                    p.average_rating = toFloat($average_rating)
                MERGE (r:Review {review_id: $review_id})
                SET r.rating = toFloat($rating),
                    r.text = $text,
                    r.timestamp = $timestamp,
                    r.review_sentiment = $review_sentiment,
                    r.aspect_sentiments = $aspect_sentiments,
                    r.rating_sentiment = $rating_sentiment
                MERGE (u)-[:WROTE]->(r)
                MERGE (r)-[:REVIEWS]->(p)
            """, review)
        except Exception as e:
            print(f"⚠️ Error inserting review: {e}")

# --- Batch Insert ---
BATCH_SIZE = 2000
batch = []
count = 0

with driver.session() as session:
    for message in consumer:
        review = message.value
        batch.append(review)
        count += 1

        # When enough reviews collected, insert into Neo4j
        if len(batch) >= BATCH_SIZE:
            session.execute_write(insert_batch, batch)
            print(f"✅ Inserted batch of {len(batch)} reviews (total so far: {count})")
            batch = []

    # Insert remaining reviews
    if batch:
        session.execute_write(insert_batch, batch)
        print(f"✅ Final batch inserted. Total reviews: {count}")

print("🏁 Done streaming all reviews to Neo4j!")
driver.close()
