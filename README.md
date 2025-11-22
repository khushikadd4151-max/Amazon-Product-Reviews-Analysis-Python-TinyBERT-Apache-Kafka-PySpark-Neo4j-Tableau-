# Amazon-Product-Reviews-Analysis-Python-TinyBERT-Apache-Kafka-PySpark-Neo4j-Tableau-

Project Title: Personalized Product Recommendations Using Neo4j Graph Analytics and Tableau Visualization
1. Introduction
E-commerce platforms such as Amazon host millions of customer reviews across a wide range of product categories. These reviews represent one of the richest sources of customer insight available to businesses today. They capture opinions about product quality, satisfaction, and performance, offering valuable feedback that can inform product design, marketing, and strategic decision-making.
However, due to the sheer volume and unstructured nature of this textual data, manual analysis is neither efficient nor scalable. Traditional data processing systems are insufficient for uncovering complex relationships and sentiment patterns within such massive datasets.
This project addresses this problem by developing a Big Data and Business Intelligence pipeline that integrates Natural Language Processing (NLP), sentiment analysis, graph-based recommendation modeling, and real-time visualization. The solution combines TinyBERT for sentiment detection, Apache Kafka and Apache Spark for distributed streaming, Neo4j Graph Database for relationship storage and recommendation generation, and Tableau for dashboard visualization.
2. Problem Statement
Amazon’s product reviews are an untapped goldmine of information that businesses can use to understand their customers better. Yet, without an automated system capable of extracting, processing, and analyzing these reviews, organizations risk missing out on crucial insights.
Challenges include:
● Handling millions of unstructured text reviews efficiently.
● Extracting meaningful sentiment and feature-level insights.
● Detecting patterns and connections between users, products, and sentiments.
● Presenting findings in a way that supports quick, data-driven business actions.
The goal of this project is to develop an integrated analytical pipeline that addresses these issues by leveraging Big Data, NLP, and Business Intelligence technologies.
3. Objectives
The project was guided by the following key objectives:
● To collect and preprocess large-scale Amazon product review datasets for multiple categories.
● To perform sentiment analysis using state-of-the-art NLP models for classifying review polarity.
● To identify frequently mentioned product features, including both praised and criticized aspects.
● To design a graph-based recommendation engine that leverages sentiment and rating data.
● To develop an interactive Tableau dashboard for visualizing sentiment trends, key product insights, and recommendations.
4. Dataset Description
The project utilized the Amazon Customer Reviews Dataset available from AWS Open Data. The dataset includes over 100 million reviews spanning 24 product categories. Each record contains the following fields:
● asin: Amazon Standard Identification Number (Product ID)
● user_id: Unique identifier for the reviewer
● rating: User-provided product rating (1–5)
● title_y: Product name
● review_text: Main content of the customer review
● summary: Short description of the review
● timestamp: Date and time of review submission
● category: Product category
For this project, a representative sample of approximately 50,000 reviews per category was extracted and processed to ensure a balance of diversity and computational feasibility.
5. Methodology
The proposed methodology follows a structured five-step pipeline: Data Ingestion and Cleaning, Sentiment Analysis, Streaming and Storage, Recommendation Modeling, and Visualization.
5.1 Data Ingestion and Preprocessing
The datasets were first ingested from AWS S3 storage into the processing environment. Initial filtering was performed to remove missing values, duplicate reviews, and records with incomplete identifiers. The textual content was cleaned using standard NLP preprocessing steps, including tokenization, stopword removal, and lemmatization.
The cleaned data was then prepared for sentiment analysis. Python libraries such as Pandas, NumPy, and NLTK were used to handle data transformation, while PySpark was employed for distributed processing to manage the large dataset efficiently.
5.2 Sentiment Analysis
Two layers of sentiment analysis were applied to extract nuanced information from reviews. At the review level, each review was categorized into positive, negative, or neutral sentiments. At the aspect level, the system extracted specific product features (e.g., “battery,” “delivery,” “quality”) and associated sentiment with those aspects.
Initially, baseline models such as Logistic Regression and Support Vector Machines with TF-IDF vectorization were implemented to establish performance benchmarks. Later, an advanced transformer-based model, TinyBERT, was fine-tuned on the Amazon dataset. TinyBERT provided high accuracy while remaining computationally efficient—making it suitable for large-scale sentiment classification tasks.
The output of this stage included fields like review_sentiment (overall polarity) and aspect_sentiments (sentiment scores for individual aspects).
5.3 Streaming and Graph Storage (Kafka + Spark + Neo4j Integration)
Once the data was processed and labeled with sentiment information, it was streamed into the storage layer using Apache Kafka and Apache Spark. Kafka acted as the message broker that transmitted preprocessed and sentiment-tagged review data, while Spark performed transformations and batching before writing the results to the database.
The data was stored in a Neo4j Graph Database, which provided an ideal structure for modeling relationships between Users, Products, and Reviews. The graph schema was defined with three primary node types:
● User – Represents an individual customer.
● Review – Represents the review entity containing text, rating, and sentiment.
● Product – Represents the product being reviewed.
The relationships defined were:
● (User)-[:WROTE]->(Review)
● (Review)-[:REVIEWS]->(Product)
After successful data ingestion, the Neo4j instance contained 1,013,616 nodes and 1,056,354 relationships. Each node stored multiple attributes, as reflected by the property keys in the database, including: asin, aspect_sentiments, average_rating, category, rating_sentiment, review_sentiment, timestamp, title, and user_id.
Indexes were created to optimize query performance using Cypher commands such as:
CREATE INDEX user_id_index FOR (u:User) ON (u.user_id);
CREATE INDEX product_asin_index FOR (p:Product) ON (p.asin);
The creation logs confirmed the generation of over one million nodes and relationships, establishing a robust graph structure suitable for large-scale query processing and recommendation computation.
In graph, Blue node is user, Yellow node is review and Red node is product
In Relationships, Orange line is wrote and Blue line is Reviews
5.4 Recommendation Engine
The recommendation system was built on top of Neo4j’s graph structure. The advantage of using Neo4j lies in its ability to represent complex connections between users and products, making it easier to compute personalized recommendations.
Two primary approaches were implemented:
1. Content-Based Filtering: Recommendations were generated based on product similarity, using sentiment-weighted textual similarity scores derived from reviews.
2. Collaborative Filtering: Recommendations were made by identifying users with similar purchase and review patterns, then suggesting products those similar users rated positively.
These models leveraged both the review_sentiment and rating_sentiment fields to prioritize products with positive customer perceptions. The resulting recommendation network allowed for both individual and category-level product suggestions.
This Cypher script imports cleaned Amazon review data into Neo4j and builds a graph structure linking users, reviews, and products. It first creates indexes on key identifiers (user_id, asin, review_id) to speed up data loading. The CSV file containing reviews is then read, and a unique review ID is generated by combining user ID, product ID, and timestamp. For each record, the script merges (creates or reuses) nodes for User, Product, and Review, assigns their respective properties (like rating, sentiment, and category), and establishes relationships — (:User)-[:WROTE]->(:Review)-[:REVIEWS]->(:Product). The process runs in transactions for efficient large-scale data ingestion.
This Python–Cypher code block generates user-based collaborative product recommendations from the Neo4j graph database.
It works by repeatedly processing users in batches (while True loop). For each unprocessed user (target), it first finds all products they have reviewed. Then, it identifies other users who reviewed the same products (shared interests). Based on the number of shared products, it calculates a similarity score between users.
Next, it finds new products reviewed by those similar users that the target user has not yet reviewed, treating them as potential recommendations. For each recommended product, it computes the similarity score and the product’s average rating, ranking the results by both factors.
Finally, it returns the top 10 recommended products for each user along with their similarity scores and average ratings, forming the basis of the collaborative filtering recommendation engine.
This Cypher query implements a multi-hop recommendation approach in Neo4j to find products indirectly connected to a target user through similar users.
It starts by locating a given user (u) and the products they have reviewed. Then it identifies other users who have reviewed the same products — these act as “similar” or “like-minded” users. From these similar users, the query retrieves other products they have reviewed that the target user has not interacted with yet.
Finally, it returns up to 10 distinct product recommendations (recommended_asin) for the user. In essence, this query uses a two-hop traversal — from the user to similar users, then to new products — to suggest relevant items based on shared reviewing patterns.
5.5 Dashboard and Visualization in Tableau
An interactive Tableau dashboard was developed by establishing a live connection with the Neo4j database, ensuring that any new reviews, ratings, or sentiment updates were automatically reflected in real time. This integration allowed continuous synchronization between the analytical backend and the visualization layer, providing users with up-to-date insights derived from streaming data.
The dashboard was designed to present key business intelligence insights through a combination of sentiment analysis, product performance metrics, and recommendation data. The primary visual elements included:
● Sentiment Distribution View: Displaying the proportion of positive, negative, and neutral reviews across various product categories. This visualization enabled quick assessment of overall customer perception and helped identify product lines with higher
dissatisfaction rates.
● Count of Reviews by Category and Product: This view summarized the total volume of reviews for each category and product, offering a clear picture of customer engagement levels and helping to identify top-reviewed or under-discussed products.
● Review Sentiment and Average Rating Analysis: This visualization combined sentiment classification results with quantitative rating data, allowing comparison between customer emotion and numerical ratings. It revealed patterns such as products with high ratings but mixed sentiment, indicating potential inconsistencies in customer satisfaction.
● Rating Effectiveness Metrics: A custom measure was included to evaluate how effectively product ratings aligned with textual sentiment. This metric helped detect anomalies—such as inflated ratings for negatively worded reviews—thereby supporting quality assurance in rating systems.
● Recommendation Visualization: The dashboard also featured user-specific and sentiment-weighted product recommendations, generated from Neo4j’s collaborative filtering engine. Users could explore suggested products based on similar user preferences and historical review sentiments.
Overall, the Tableau dashboard served as a decision intelligence layer, translating complex analytical outputs into actionable, business-friendly visual insights. It enabled stakeholders to monitor sentiment trends, assess product reputation, and refine marketing or improvement strategies based on real customer feedback and behavior patterns.
6. System Architecture
The complete system was designed as an end-to-end Big Data pipeline. The workflow proceeds as follows:
1. Data Source: Amazon review datasets from AWS Open Data.
2. Processing Layer: Apache Spark for large-scale data cleaning and NLP preprocessing.
3. Sentiment Analysis: TinyBERT model for classifying and extracting aspect sentiments.
4. Streaming Layer: Apache Kafka to handle continuous data ingestion and transfer.
5. Storage Layer: Neo4j Graph Database to represent user-product-review relationships.
6. Visualization Layer: Tableau connected to Neo4j for business intelligence reporting.
This architecture ensured scalability, real-time insight generation, and the ability to handle future data expansion seamlessly.
7. Results and Insights
The developed Big Data and Business Intelligence pipeline successfully processed and analyzed over 1 million Amazon product reviews, integrating NLP-driven sentiment analysis, graph-based recommendations, and interactive visualization. The sentiment classification achieved an overall accuracy of approximately 90% using the TinyBERT model, which effectively categorized reviews into positive, negative, and neutral sentiments. Aspect-based sentiment analysis further provided deeper insights into the specific product features mentioned in reviews, revealing recurring themes such as delivery delays, packaging quality, and value-for-money perceptions.
The Neo4j graph database played a crucial role in structuring and managing the complex relationships between users, products, and reviews. The database contained over 1,013,616 nodes and 1,056,354 relationships, organized across three major entities: User, Product, and Review. Relationships such as WROTE (linking users to reviews) and REVIEWS (linking reviews to products) allowed efficient querying and visualization of interaction patterns. Property keys like review_sentiment, aspect_sentiments, average_rating, and timestamp enabled detailed filtering and analysis.
On top of this, a collaborative filtering recommendation engine was implemented within Neo4j. This component analyzed user-product interaction patterns and similar sentiment behavior to suggest personalized product recommendations. The system leveraged both content-based similarity (via review text and product attributes) and user-based collaborative filtering, ensuring that users with similar preferences or sentiment histories received more accurate and relevant suggestions.
The integration between Neo4j and Tableau enabled seamless visualization of graph data and analytical results. The Tableau dashboard transformed the raw data into actionable intelligence by providing:
● Interactive charts showing sentiment distribution across product categories.
● Temporal trends of positive and negative reviews over time.
● User-specific product recommendations generated dynamically from Neo4j queries.
This integrated ecosystem of Kafka, Spark, Neo4j, TinyBERT, and Tableau demonstrated the potential of a real-time, data-driven decision support system for e-commerce. Businesses can now quickly identify satisfaction drivers, pinpoint areas needing improvement, monitor sentiment fluctuations, and deliver personalized product suggestions to enhance customer experience. Overall, the system highlights how advanced NLP and graph analytics can turn unstructured review data into strategic business insights and intelligent recommendations.
8. Business Applications
This system provides significant strategic value for e-commerce platforms and sellers. By automating sentiment analysis and recommendation generation, businesses can continuously monitor customer satisfaction, identify underperforming product lines, and design targeted marketing campaigns.
The use of Neo4j adds relational depth, allowing for nuanced insights such as which user clusters tend to review similar product types or how sentiment around a specific feature evolves over time. Combined with Tableau’s interactive visualization, the system forms a comprehensive decision-support tool for product, marketing, and customer experience teams.
9. Tools and Technologies Used
● Big Data Processing: Apache Spark, Apache Kafka
● Machine Learning & NLP: TinyBERT, NLTK, Scikit-learn
● Database Management: Neo4j Graph Database
● Visualization: Tableau
● Programming Languages: Python, Cypher (for Neo4j queries)
● Data Source: AWS Open Data (Amazon Customer Reviews Dataset)
10. Conclusion
The project demonstrates how integrating Big Data technologies with NLP and Business Intelligence can unlock the full potential of user-generated content. The developed system successfully automates the process of collecting, analyzing, and visualizing millions of Amazon reviews.
By employing TinyBERT for accurate sentiment analysis, Neo4j for relationship-based modeling, and Tableau for visualization, the system transforms raw textual data into actionable insights. The architecture not only supports large-scale static analysis but can also be extended to real-time monitoring environments.
11. Future Scope
Future work could focus on deploying the pipeline in a real-time cloud environment such as AWS Glue or Databricks, enabling live ingestion and analysis of streaming review data. The sentiment models can be extended to support multilingual data, allowing for global market insights. Incorporating visual and voice reviews into the pipeline using multimodal AI would further enhance the comprehensiveness of customer understanding.
Additionally, advanced graph analytics techniques in Neo4j—such as community detection and influence propagation—could be applied to understand user behavior clusters and market influence patterns more deeply.
