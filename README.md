# E-Commerce Sales Analytics

An end-to-end sales analytics project: a synthetic (intentionally messy)
e-commerce dataset is cleaned, loaded into a SQL warehouse, analyzed with
pandas, and explored through both static charts and an interactive
Streamlit dashboard.

## What this demonstrates

- **Data cleaning** — deduplication, missing-value handling, type
  normalization, invalid-row detection, with a printed data-quality report
  (`src/data_cleaning.py`)
- **SQL** — a SQLite warehouse with hand-written analytical queries,
  including a window-function (`NTILE`) RFM calculation (`sql/queries.sql`)
- **Data analysis with pandas** — monthly revenue trends, top
  products/categories, RFM customer segmentation, and cohort retention
  analysis (`src/analysis.py`)
- **Data visualization** — matplotlib/seaborn charts (`src/visualize.py`)
  and a filterable, interactive Streamlit dashboard (`dashboard/app.py`)
- **Testing** — pytest unit tests against small fixture DataFrames
  (`tests/`)
- **Clean project structure** — a CLI entry point (`main.py`), a reusable
  `src/` package, and no notebook-only spaghetti

## Project structure

```
ecommerce-sales-analytics/
├── main.py                 # CLI: generate / clean / load-db / visualize / run-all
├── src/
│   ├── data_generator.py   # synthetic dataset (with intentional messiness)
│   ├── data_cleaning.py    # cleaning pipeline + data-quality report
│   ├── database.py         # loads cleaned data into SQLite
│   ├── analysis.py         # revenue, RFM, cohort retention (pure pandas)
│   └── visualize.py        # static PNG charts
├── sql/queries.sql         # sample analyst SQL queries against warehouse.db
├── dashboard/app.py        # Streamlit dashboard
├── tests/                  # pytest unit tests
├── data/                   # raw/, processed/, warehouse.db (generated, gitignored)
└── reports/figures/        # generated PNG charts (gitignored)
```

## Setup

Requires Python 3.9+.

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

## Run the pipeline

```bash
python main.py run-all
```

This generates the synthetic raw data, cleans it (printing a data-quality
report), loads it into `data/warehouse.db`, and saves charts to
`reports/figures/`. You can also run each step individually:

```bash
python main.py generate
python main.py clean
python main.py load-db
python main.py visualize
```

## Launch the dashboard

```bash
streamlit run dashboard/app.py
```

Filter by date range, category, and region; see live KPIs, revenue trends,
top products, and an RFM segment breakdown with a per-customer table.

## Run the tests

```bash
pytest
```

## Explore the SQL

```bash
sqlite3 data/warehouse.db < sql/queries.sql
```

Or open `data/warehouse.db` in any SQLite client (e.g. DB Browser for
SQLite) and run the queries in `sql/queries.sql` individually.

## Notes on the data

The dataset is synthetically generated (`src/data_generator.py`) rather
than downloaded, so the project is fully self-contained and reproducible
(fixed random seed). It's deliberately seeded with realistic messiness —
duplicate rows, missing regions, negative quantities, missing order
totals — so the cleaning step has genuine problems to solve rather than
running against already-tidy data.
