# Amazon-Product-Reviews-Analysis-Python-TinyBERT-Apache-Kafka-PySpark-Neo4j-Tableau-

## 📌 Overview

E-commerce platforms like Amazon host millions of customer reviews containing rich insights about product quality, user satisfaction, and feature-level opinions. However, manually analyzing such massive unstructured data is inefficient and impossible at scale.

This project builds an **end-to-end Big Data & Business Intelligence pipeline** that extracts, processes, and visualizes insights from Amazon reviews using:

* **TinyBERT** for sentiment analysis
* **Apache Kafka & Apache Spark** for distributed data streaming
* **Neo4j** for graph-based recommendation modeling
* **Tableau** for real-time BI visualization

The system processes over **1 million reviews**, generates personalized recommendations, and provides visual insights for business decision-making.

---

## 📝 Problem Statement

Amazon product reviews are an "untapped goldmine," yet organizations face challenges such as:

* Processing millions of unstructured text reviews
* Extracting feature-level sentiments
* Identifying relationships among users, products, and sentiments
* Visualizing actionable insights for decision-making

This project solves these challenges through an automated multi-stage analytical pipeline.

---

## 🎯 Objectives

* Preprocess large-scale Amazon review datasets
* Perform review-level and aspect-level sentiment analysis
* Extract frequently mentioned product features
* Build a Neo4j-based recommendation engine
* Create a real-time Tableau dashboard for insights and recommendations

---

## 📂 Dataset Description

Source: **Amazon Customer Reviews Dataset (AWS Open Data)**
Used: ~50,000 reviews per category from 24 categories

Key fields include:
`asin`, `user_id`, `rating`, `title_y`, `review_text`, `summary`, `timestamp`, `category`

---

## 🔧 System Architecture

### **End-to-End Pipeline**

```
AWS Open Data → Spark Preprocessing → TinyBERT Sentiment Model 
→ Kafka Streaming → Neo4j Graph Storage → Tableau Visualization
```

### **Technologies Used**

* **Big Data**: Apache Spark, Apache Kafka
* **NLP**: TinyBERT, NLTK, Scikit-learn
* **Database**: Neo4j Graph Database
* **Visualization**: Tableau
* **Languages**: Python, Cypher
* **Dataset**: AWS Amazon Reviews

---

## 🛠️ Methodology

### **1. Data Ingestion & Preprocessing**

* Loaded data from AWS S3
* Removed duplicates/missing fields
* Applied NLP preprocessing (tokenization, stopwords, lemmatization)
* Used Pandas, NumPy, PySpark for scalable data handling

---

### **2. Sentiment Analysis (Review-level + Aspect-level)**

* Implemented baseline ML models: Logistic Regression, SVM (TF-IDF)
* Fine-tuned **TinyBERT**, achieving ~90% accuracy
* Extracted:

  * `review_sentiment` (positive/negative/neutral)
  * `aspect_sentiments` (feature-level sentiment scores)

---

### **3. Streaming + Graph Storage (Kafka, Spark, Neo4j)**

* Kafka streams sentiment-tagged reviews
* Spark batches & processes the streaming data
* Stored in Neo4j with nodes:

  * **User (Blue)**
  * **Review (Yellow)**
  * **Product (Red)**

**Relationships**

```
(User)-[:WROTE]->(Review)
(Review)-[:REVIEWS]->(Product)
```

Dataset in Neo4j:

* **1,013,616+ Nodes**
* **1,056,354+ Relationships**

Indexes created for optimization:

```cypher
CREATE INDEX user_id_index FOR (u:User) ON (u.user_id);
CREATE INDEX product_asin_index FOR (p:Product) ON (p.asin);
```

---

### **4. Recommendation Engine (Content + Collaborative Filtering)**

#### **Content-Based Filtering**

* Used sentiment-weighted textual similarity
* Recommended similar products with positive sentiment patterns

#### **Collaborative Filtering**

* Identified similar users based on shared review history
* Recommended products reviewed positively by similar users

Cypher queries retrieved multi-hop recommendations using user → product → similar users → new products exploration.

---

### **5. Tableau Dashboard Visualization**

Connected Tableau directly to Neo4j for real-time updates.
Dashboard features include:

* **Sentiment Distribution** across categories
* **Review Counts** by product/category
* **Average Rating vs Review Sentiment**
* **Rating Effectiveness Metric** (detect rating–sentiment mismatch)
* **User-Specific Recommendations**

The dashboard acts as a dynamic decision support tool.

---

## 📊 Results

* Processed **1+ million reviews**
* Achieved **~90% sentiment accuracy** with TinyBERT
* Extracted feature-level sentiments for recurring themes
* Built a Neo4j graph with over **1M nodes & relationships**
* Developed a hybrid recommendation engine (content + collaborative)
* Delivered real-time insights through Tableau visualizations

The pipeline demonstrates how unstructured text can be transformed into **actionable business intelligence**.

---

## 💼 Business Applications

* Product line improvement
* Customer dissatisfaction tracing
* Targeted ad campaigns
* Persona-based personalization
* User clustering & behavior pattern discovery
* Market trend analysis

---

## 🚀 Future Scope

* Deploying pipeline on AWS Glue or Databricks for fully real-time processing
* Multilingual sentiment analysis
* Adding multimodal data (image/voice reviews)
* Advanced Neo4j graph analytics (community detection, influence propagation)
* Deploying recommendations as an API service




