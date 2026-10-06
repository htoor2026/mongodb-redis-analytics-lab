# MongoDB & Redis Analytics Lab

**Exploring time-series analytics, query performance, caching, and event processing with public health and NYC taxi data.**

Built as an Advanced Data Systems coursework project at Conestoga College. This repository brings together a runnable taxi-data importer and a technical report containing MongoDB aggregation pipelines, execution-plan screenshots, Atlas Charts, and Redis exercises.

## Project at a glance

| Area | Work covered | Where to inspect it |
| --- | --- | --- |
| Data ingestion | Parquet loading, field selection, timestamp conversion, and MongoDB inserts | [Python importer](import_tlc_trips.py) |
| Public health analytics | Rolling case averages, surge comparisons, and annual country metrics | [Project report](docs/project-report.pdf), Tasks 1–2 |
| Materialized results | Country-year summaries written with `$merge` and a unique compound index | Report, Task 3 |
| Visualization | Country comparisons, time trends, and vaccination scatter plots | Report, Task 4 |
| Taxi analytics | Hourly trip counts, revenue, approximate 95th percentiles, and moving averages | Report, Task 5 |
| Query performance | Baseline, indexed, and rewritten aggregation exercises with `explain()` | Report, Task 6 |
| Redis | Cache keys and TTLs; Streams, consumer groups, and acknowledgements | Report, R1–R2 |

**Scope:** The importer runs independently. The remaining exercises are documented in the report; standalone analytics scripts, a running dashboard, and a complete stream consumer are not included.

## Questions explored

- How can window functions reveal changes in reported COVID-19 cases?
- How can annual summaries be stored for reuse in charts and queries?
- How do taxi demand and recorded revenue change across hourly buckets?
- How do indexes and aggregation structure affect query execution?
- How can Redis support expiring analytical results and simulated trip events?

## Data and tools

| Dataset | Format and coverage | Use |
| --- | --- | --- |
| [Our World in Data COVID-19 data](https://github.com/owid/covid-19-data) | Daily country-level CSV records | Public health time-series exercises |
| [NYC TLC yellow taxi records](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) | September 2024 Parquet; first 200,000 rows used in the coursework | Trip ingestion, hourly demand, and revenue analytics |

The taxi importer retains pickup/drop-off timestamps, pickup/drop-off location IDs, passenger count, trip distance, fare amount, total amount, and payment type. Source datasets are downloaded separately and excluded from Git.

**Stack:** Python · pandas · PyArrow · PyMongo · MongoDB · Redis · MongoDB Compass · Atlas Charts

## Run the taxi importer

### 1. Install dependencies

Use Python 3.10 or newer, with access to a MongoDB instance you control.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 2. Download the data

Download [September 2024 yellow taxi trips](https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-09.parquet) and place `yellow_tripdata_2024-09.parquet` in the repository root. The script also accepts a different file path.

### 3. Configure MongoDB

For a local MongoDB instance:

```bash
export MONGODB_URI='mongodb://localhost:27017/'
```

For another instance, supply its connection URI through the same environment variable. Database and collection names default to `global_lab` and `tlc_trips`; override them with `MONGODB_DATABASE` and `MONGODB_COLLECTION`.

### 4. Import the sample

```bash
python import_tlc_trips.py
```

Optional arguments:

```bash
python import_tlc_trips.py --file /path/to/trips.parquet --limit 10000
python import_tlc_trips.py --help
```

The importer checks the required columns, converts missing values to BSON-compatible nulls, and inserts records in batches. It **appends** to the target collection: running it twice inserts the sample twice. Use a fresh collection for a repeatable lab run.

The row limit applies after loading the Parquet file, so memory usage depends on the full source file. It is a row selection limit, not a streaming reader.

## Read the analytical work

Open the [project report](docs/project-report.pdf) for the queries and screenshots. The coursework used these index patterns:

| Collection | Index pattern | Intended workload |
| --- | --- | --- |
| `owid_daily` | `{ location: 1, date: 1 }` | Country/date filtering and ordered time-series work |
| `owid_daily` | `{ continent: 1, date: 1 }` | Continent/date queries |
| `tlc_trips` | `{ tpep_pickup_datetime: 1 }` | Pickup-time range filters |
| `tlc_trips` | `{ PULocationID: 1, tpep_pickup_datetime: 1 }` | Zone/time filtering |
| `risk_annual_v1` | `{ location: 1, year: 1 }`, unique | Country-year identity for `$merge` |

Evaluate these against the actual query plan and data distribution. The report contains execution-plan comparisons, rather than a reproducible benchmark suite or a verified speedup figure.

## Design notes and next improvements

The coursework demonstrates database techniques, with several limits to address before extending it into an application:

- The first 200,000 taxi rows are a convenience subset, not a representative random sample of the month.
- The COVID-19 risk score is an illustrative composite metric. The annual-analysis and materialization sections use different formulas; they need alignment before the results can be compared.
- Redis acknowledgements are shown, but crash recovery and idempotent database writes still need implementation and validation.

See [technical notes](docs/technical-notes.md) for details and focused follow-up work.

## Repository files

| File | Purpose |
| --- | --- |
| `import_tlc_trips.py` | Configurable taxi-data importer |
| `requirements.txt` | Python dependencies |
| `docs/project-report.pdf` | Original coursework analysis, queries, and screenshots |
| `docs/technical-notes.md` | Methodological limits and engineering improvements |
| `.gitignore` | Excludes local data, credentials, environments, and generated Python files |

## Author

**Harkamal Singh Toor** · [GitHub](https://github.com/htoor2026) · [LinkedIn](https://www.linkedin.com/in/harkamal-s/)

Originally completed for Advanced Data Systems, Conestoga College, December 2025.
