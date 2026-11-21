# E-Commerce Product Intelligence System

A Python-based e-commerce product intelligence and data extraction application designed to collect, process, validate, store and export structured product information.

The system demonstrates practical web scraping, data engineering, database management, automated testing and multi-format data export.

## 1. Project Overview

E-commerce businesses generate large amounts of product information across their online catalogues.

Collecting and organizing this information manually can be time-consuming and inefficient.

This project provides an automated workflow for extracting product information, processing records, eliminating duplicates, validating data and generating structured datasets for further analysis.

The application currently demonstrates its processing pipeline using locally stored HTML fixtures from perfume product categories.

Live extraction is designed to operate only against sources that authorize automated access.

## 2. Key Features

- HTTP request management using Python Requests.
- Reusable scraper architecture.
- Robots.txt permission checking.
- Request rate limiting.
- Pagination support.
- HTML parsing using BeautifulSoup.
- Product name extraction.
- Current and original price extraction.
- Product URL extraction.
- Data cleaning and normalization.
- Product validation.
- Duplicate detection.
- SQLite database storage.
- Database schema migration.
- Excel export.
- CSV export.
- JSON export.
- Structured logging.
- Automated testing with Pytest.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application |
| Requests | HTTP communication |
| BeautifulSoup4 | HTML parsing |
| SQLite | Database storage |
| Pandas | Data processing and export |
| OpenPyXL | Excel generation |
| Pytest | Automated testing |
| urllib.robotparser | Robots.txt compliance |
| Logging | Application monitoring |

## 4. System Architecture

The application follows a modular architecture.

```text
E-Commerce Product Intelligence
             |
             v
       Data Acquisition
             |
             v
        Base Scraper
             |
             v
       Product Parser
             |
             v
       Data Cleaning
             |
             v
       Data Validation
             |
             v
     Duplicate Detection
             |
             v
       SQLite Database
             |
             v
       Export Manager
             |
       +-----+-----+
       |     |     |
       v     v     v
     Excel  CSV   JSON
```

### Project Structure

```text
ecommerce-product-intelligence/
│
├── config/
│   └── logging_config.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── logs/
│
├── processors/
│   ├── cleaning.py
│   ├── pipeline.py
│   ├── product_parser.py
│   └── validation.py
│
├── scrapers/
│   ├── base_scraper.py
│   └── perfume_scraper.py
│
├── storage/
│   ├── database.py
│   ├── data_exporter.py
│   ├── excel_exporter.py
│   └── export_manager.py
│
├── tests/
│
├── check_robots.py
├── live_main.py
├── main.py
├── requirements.txt
└── README.md
```

## 5. Installation

### Prerequisites

- Python 3.11 or newer.
- Git.
- pip.

### Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ecommerce-product-intelligence.git

cd ecommerce-product-intelligence
```

### Create a virtual environment

Windows:

```powershell
python -m venv .venv
```

Activate:

```powershell
.venv\Scripts\Activate.ps1
```

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

## 6. Running the Application

The offline processing workflow uses locally stored HTML fixtures.

Execute:

```bash
python main.py
```

The application performs:

1. HTML fixture loading.
2. Product extraction.
3. Data cleaning.
4. Product validation.
5. Duplicate detection.
6. SQLite storage.
7. Excel, CSV and JSON export.

## 7. Database Storage

The application uses SQLite for structured product storage.

Database location:

```text
data/processed/products.db
```

The database stores product information and category associations.

## 8. Data Export

The application generates three output formats.

```text
data/processed/
│
├── products.db
├── products.xlsx
├── products.csv
└── products.json
```

### Excel

Suitable for spreadsheet analysis and reporting.

### CSV

Suitable for importing into other data analysis applications.

### JSON

Suitable for APIs, programmatic processing and integration with other systems.

## 9. Automated Testing

The project uses Pytest.

Run all tests:

```bash
python -m pytest -v
```

Run a concise test report:

```bash
python -m pytest -q
```

Current verified test baseline:

```text
35 passed
```

Tests cover the scraper, processing components and supporting functionality.

## 10. Responsible Data Collection

The project incorporates responsible scraping practices.

These include:

- Robots.txt permission checking.
- Configurable request delays.
- HTTP error handling.
- Request timeouts.
- Protection against unverified robots.txt responses.
- Explicit handling of HTTP 429 rate limits.

Automated extraction must only be performed against sources that authorize the activity.

The original demonstration website returned HTTP 429 bot protection during live testing. Consequently, live extraction from that source has not been verified.

The offline processing pipeline has been successfully demonstrated using saved HTML fixtures.

## 11. Current Demonstration Results

The latest successful offline execution processed:

| Metric | Result |
|---|---:|
| HTML pages processed | 3 |
| Products processed | 72 |
| Valid records | 72 |
| Invalid records | 0 |
| Duplicates removed | 0 |
| Excel records exported | 72 |
| CSV records exported | 72 |
| JSON records exported | 72 |

These results represent the saved demonstration dataset, not a live website extraction.

## 12. Future Development

Potential extensions include:

- Integration with additional authorized e-commerce sources.
- Product price monitoring.
- Historical price tracking.
- Product availability monitoring.
- Scheduled extraction.
- REST API integration.
- Product intelligence dashboards.
- Market trend analysis.
- Automated reporting.

## 13. Project Status

The core offline processing pipeline, database integration, exports and automated tests have been implemented and demonstrated.

Final documentation and authorized live-source integration are the remaining delivery milestones.

## 14. Author

Developed as a Python automation and data engineering portfolio project.

**Technologies:** Python | Web Scraping | Data Processing | SQLite | Automation | Data Export
```