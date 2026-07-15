# Saf Shikan — Customer Data & Management Portal ⚫

This repository contains the enterprise-grade **Customer Data & Management Portal** for **SAF SHIKAN**, designed to be seamlessly integrated as an active tab inside the **AGRON Admin Dashboard**.

The portal serves as a high-density, production-ready directory and analytical console focusing exclusively on the **6 Core Data Categories** of registered farmers across Pakistani cities/districts (`Name`, `Phone`, `Crop_Type`, `Crop_Area`, `Season`, and `Location`), completely free of lead scoring or ML clustering logic.

---

## 🌟 Key Enterprise Features

### 1. Farmer Directory & Ingestion Console
* **6 Core Categories:** Cleanly tracks Name, Phone, Crop Type, Farm Area (Acres), Growing Season, and City/District.
* **Batch Import & Client-Side Ingestion:** To maintain strict data privacy and security without committing sensitive `customers.csv` records to public GitHub repositories, administrators can batch upload or sync local CSV files directly inside the live session.
* **Manual "Other" Crop Support:** Select from primary crops (`Wheat`, `Cotton`, `Rice`, `Sugarcane`, `Maize`, `Orchard`, `Vegetables`) or specify custom crops via dynamic text input.
* **Strict Phone Validation:** Enforces standard Pakistani mobile contact format (`0XXX-XXXXXXX`).
* **Non-Blocking Toasts:** Clean `st.toast()` notifications on record commit and data synchronization.

### 2. Multi-Dimensional Pivot & Aggregation Engine
* **Count-Only Grouping:** Group records by `Location` (City), `Crop_Type`, `Season`, or `Farm_Scale` with instant farmer count and acreage totals.
* **Interactive Heatmaps:** Styled gradient data tables for rapid executive review.

### 3. Visual Analytics Module
* **City-Wise Concentration:** Bar charts mapping farmer distribution across unique districts/cities.
* **Crop Portfolio Breakdown:** Interactive donut and bar charts showing total acreage and farmer share per crop.
* **Seasonal Cultivation Breakdown:** Clear split between `Rabi`, `Kharif`, and `Perennial` seasons.
* **City-Crop Distribution Matrix:** Stacked bar visualization for the top 10 cities.

### 4. Security & Audit Trail Console
* **End-to-End Encryption:** Enforced HTTPS / TLS 1.3 across all client-server traffic.
* **Plain English Audit Log:** Human-readable activity cards recording every page navigation, filter application, record ingestion, and CSV/Excel export without technical HTML leakage.
* **Session Tracking:** Unique session identifier tagging across all logged events.

---

## 📁 Directory Structure

```text
saf-shikan-customer-leads/
├── customer-leads/
│   ├── dashboard/
│   │   ├── app.py              ← Main enterprise Streamlit portal application
│   │   └── audit_logger.py     ← Security and Plain English audit logging engine
│   ├── data/
│   │   └── raw/
│   │       └── customers.csv   ← Local data repository (Ignored by Git for security)
│   ├── requirements.txt        ← Project dependencies
│   └── README.md               ← Documentation
└── .gitignore                  ← Git exclusion rules for CSV data and temporary files
```

---

## 🚀 Getting Started Locally

### 1. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/MAbdullahSarwar31/saf-shikan-customer-leads.git
cd saf-shikan-customer-leads/customer-leads
pip install -r requirements.txt
```

### 2. Launching the Portal
Run the Streamlit application:
```bash
streamlit run dashboard/app.py
```
Open `http://localhost:8501` in your web browser.

> **Security & Privacy Note:** By default, `.gitignore` excludes all `*.csv` files to prevent accidentally committing sensitive customer phone numbers or personal data to GitHub. When running freshly on Streamlit Cloud or locally without an existing `customers.csv`, the application automatically initializes a clean base structure or allows client-side CSV upload via the **Batch Import** console.

---

## ☁️ Streamlit Cloud Deployment

1. Push this repository (`main` branch) to GitHub.
2. Log in to [share.streamlit.io](https://share.streamlit.io).
3. Click **New App** and select `MAbdullahSarwar31/saf-shikan-customer-leads`.
4. Set the main file path to: `customer-leads/dashboard/app.py`.
5. Click **Deploy!**
