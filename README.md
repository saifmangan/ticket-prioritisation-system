# Intelligent Support Ticket Prioritisation System

## Overview
An end-to-end machine learning pipeline that automatically classifies 
customer support tickets as **urgent vs non-urgent**, enabling faster 
triage and improved SLA compliance.

## Problem Statement
- High-priority tickets are buried in high ticket volumes
- Manual triage is inconsistent and doesn't scale
- Delayed responses reduce customer satisfaction and breach SLAs

## Dataset
- **Source:** Support Ticket Priority Dataset (50K records)
- **Type:** Synthetic but business-realistic customer support data
- **Class distribution:** ~59K non-urgent vs ~7K urgent (imbalanced)
- **Target variable:** `priority_bin` — 1 (Urgent), 0 (Non-urgent)

## Pipeline Architecture

### 1. Data Ingestion
- Loaded multiple CSV sources (tickets, issues, utterances)
- Unified schema via joins and aggregation

### 2. Cleaning & Preprocessing
- Missing value handling
- Text normalisation
- Timestamp conversion
- Deduplication

### 3. Feature Engineering
**Manual Features:**
| Feature | Description |
|---|---|
| feat_char_len | Message character length |
| feat_words | Word count |
| feat_excl | Exclamation mark frequency |
| feat_urgent | Urgency keyword presence |
| feat_positive | Positive sentiment indicators |

**NLP Features (TF-IDF):**
- TF-IDF vectorisation (3,000 features)
- Unigrams + bigrams
- English stop-word removal

### 4. Modelling
- **Algorithm:** Logistic Regression (baseline)
- **Train/Test Split:** 70/30
- **Class imbalance:** Handled via `class_weight="balanced"`
- **Evaluation focus:** Recall on urgent class — 
  missing a critical ticket is costlier than a false alarm

## Project Structure
```
ticket-prioritisation-system/
│
├── src/
│   ├── pipeline.py        # Data ingestion & cleaning
│   ├── features.py        # Manual feature engineering
│   ├── text_features.py   # TF-IDF vectorisation
│   └── model.py           # Model training & evaluation
│
├── data/
│   ├── raw/
│   └── processed/
│
├── main.py
└── README.md
```

## Tech Stack
- Python, Pandas, NumPy
- Scikit-Learn (TF-IDF, Logistic Regression)
- SciPy (sparse matrix combination)

## Future Improvements
- Transformer-based embeddings (BERT) for richer text features
- Multi-class priority prediction
- Real-time FastAPI serving layer
- Streamlit dashboard for support teams

## Skills Demonstrated
- Data Engineering (ETL, pipeline design)
- NLP (TF-IDF, text preprocessing)
- Machine Learning (classification, imbalanced datasets)
- Reproducible project structure
