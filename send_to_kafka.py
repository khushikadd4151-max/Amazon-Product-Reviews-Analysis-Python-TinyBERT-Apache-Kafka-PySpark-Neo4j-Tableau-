import pandas as pd
from kafka import KafkaProducer
import json
import time
import os

# ------------------------------
# Config
# ------------------------------
csv_file = r"D:\mahis\AmazonReviewProject\amazon_reviews_sentiment_cleaned.csv"
kafka_topic = "amazon_reviews"
kafka_bootstrap_servers = ['localhost:9092']
batch_size = 1000
progress_file = "kafka_send_progress.txt"  # store last sent row

# ------------------------------
# Initialize Kafka producer
# ------------------------------
producer = KafkaProducer(
    bootstrap_servers=kafka_bootstrap_servers,
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    batch_size=32768,  # 32 KB per batch
    linger_ms=50
)

# ------------------------------
# Load CSV
# ------------------------------
df = pd.read_csv(csv_file, low_memory=False)
total_rows = len(df)
print(f"Total rows in CSV: {total_rows}")

# ------------------------------
# Determine starting row
# ------------------------------
if os.path.exists(progress_file):
    with open(progress_file, "r") as f:
        start_row = int(f.read().strip())
    print(f"Resuming from row {start_row + 1}")
else:
    start_row = 139500  # resume after already sent rows
    print(f"No progress file found. Starting from row {start_row + 1}")

# ------------------------------
# Send in batches
# ------------------------------
for start in range(start_row, total_rows, batch_size):
    end = min(start + batch_size, total_rows)
    batch_df = df.iloc[start:end]
    records = batch_df.to_dict(orient='records')
    
    for record in records:
        producer.send(kafka_topic, value=record)
    
    producer.flush()
    print(f"✅ Sent rows {start+1} to {end}")
    
    # Save progress
    with open(progress_file, "w") as f:
        f.write(str(end))
    
    time.sleep(0.1)  # tiny delay to avoid overloading Kafka

print("\n🎉 All remaining rows sent to Kafka successfully!")
producer.close()
