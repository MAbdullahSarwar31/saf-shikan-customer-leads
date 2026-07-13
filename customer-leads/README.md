# SAF SHIKAN Customer Lead Scoring and Segmentation System 🛸

This repository contains the end-to-end Customer Lead Scoring and Segmentation system designed for **SAF SHIKAN**, an agro-drone startup based in Islamabad, Pakistan. 

The goal of the system is to help the sales team identify the highest-potential farmers and agribusinesses for drone spraying services, ensuring they call the most prospective candidates first.

---

## 📁 Directory Structure

```text
customer-leads/
  data/
    raw/
      customers.csv        ← Generated synthetic customer dataset (500 records)
    processed/
      customers_clean.csv  ← Processed data with engineered feature scores
      customers_clustered.csv ← Data with K-Means segment labels
      customers_final.csv  ← Final scored, categorized, and ranked sales list
  src/
    data_generator.py      ← Generates realistic Pakistani farm records
    preprocessor.py        ← Cleans data and normalizes feature scores
    clustering.py          ← Evaluates and segments customers (K-Means, PCA)
    scorer.py              ← Calculates lead scores and formats outputs
    utils.py               ← Helper module for directory initialization and file I/O
  dashboard/
    app.py                 ← Main Streamlit dashboard application
    components/
      charts.py            ← Plotly chart generation module
      filters.py           ← Interactive sidebar filter module
      tables.py            ← Interactive table displays & in-memory Excel exporter
  reports/
    Customer_Leads_SAF_SHIKAN.xlsx ← Colored, formatted Excel workbook for sales
    figures/
      elbow_curve.png      ← K-Means Elbow evaluation plot
      silhouette_scores.png ← Silhouette score evaluation plot
      cluster_scatter_2d.png ← PCA 2D segment scatter plot
  requirements.txt         ← Python project dependencies
  README.md                ← Project documentation
  .gitignore               ← Git exclusion file
  config.py                ← Centralized project configuration and weights
```

---

## ⚡ Lead Scoring & Machine Learning

### 1. Feature Engineering
Four features are mapped to a 1.0 - 10.0 scale during preprocessing:
- **Drone Service Potential** (35% weight): Based on crop suitability for drone spraying (e.g. Cotton=10, Rice=9, Sugarcane=8, Wheat=7, Others=5).
- **Area Score** (30% weight): Min-max normalized crop area in acres.
- **Season Score** (20% weight): Kharif seasons have higher pest pressure (Both=10, Kharif=7, Rabi=5).
- **Region Score** (15% weight): Operational coverage scores (Punjab=10, Sindh=8, KPK=6).

### 2. Lead Score Formula
$$Lead\ Score = (Potential \times 0.35 + Area \times 0.30 + Season \times 0.20 + Region \times 0.15) \times 10$$

### 3. Lead Categories
- **HOT LEAD 🔥** (Score $\ge$ 75): Call within 48 hours — high drone service need.
- **WARM LEAD ✅** (Score 50-74): Schedule call this month — good potential.
- **COLD LEAD ❄️** (Score 25-49): Add to WhatsApp broadcast list.
- **LOW PRIORITY** (Score $<$ 25): Add to monthly newsletter only.

### 4. Machine Learning Segmentation
Unsupervised K-Means clustering was executed for $K=2$ to $10$. Incorporating the business rule that **no segment can have fewer than 50 customers**, $K=5$ was dynamically selected as the mathematical optimum (Silhouette Score: `0.384`):
* `Large-scale Cotton Growers (Punjab - Both)`
* `Medium-scale Rice Growers (Punjab - Kharif)`
* `Medium-scale Wheat Growers (Punjab - Both)`
* `Medium-scale Wheat Growers (Punjab - Rabi)`
* `Medium-scale Wheat Growers (Kpk - Rabi)`

---

## 🚀 Getting Started

### Prerequisites
Make sure Python 3.10+ is installed.

### Installation
1. Clone the repository and navigate to the project directory:
   ```bash
   git clone https://github.com/MAbdullahSarwar31/saf-shikan-customer-leads.git
   cd saf-shikan-customer-leads/customer-leads
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Execution Pipeline
To run the full end-to-end processing pipeline sequentially:

1. **Generate Synthetic Data**:
   ```bash
   python src/data_generator.py
   ```
2. **Preprocess and Clean**:
   ```bash
   python src/preprocessor.py
   ```
3. **Run ML Clustering**:
   ```bash
   python src/clustering.py
   ```
4. **Run Lead Scoring**:
   ```bash
   python src/scorer.py
   ```

### Run Dashboard Locally
To launch the Streamlit dashboard on your machine:
```bash
streamlit run dashboard/app.py
```
Open `http://localhost:8501` in your browser.

---

## ☁️ Streamlit Cloud Deployment

This portal is designed to deploy seamlessly to Streamlit Cloud.
1. Push the repository to GitHub.
2. Visit [share.streamlit.io](https://share.streamlit.io) and log in.
3. Click **New App**, select this repository (`saf-shikan-customer-leads`), branch `main`.
4. Set the main file path to: `customer-leads/dashboard/app.py`.
5. Click **Deploy!**
