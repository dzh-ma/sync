```
author: dzh-ma
```

# Back-end Structure

This repository contains FastAPI back-end for the Sync Smart Home project.

## Project Structure

- `Dockerfile`: Configures a containerized environment for the back-end.
- `requirements.txt`: Specifies **Python dependencies & libraries needed** for the back-end to function.

## `app/` (Back-end Application)

- `__init__.py`: Marks the app directory as a Python package.
- `main.py`: **Entry point for the FastAPI back-end application.**

## `core/` (Application Core)

- `__init__.py`: Initializes the core module.
- `config.py`: Manages **application settings**, often using environment variables.
- `security.py`: Implements **security features.**

## `db/` (Database Management)

- `__init__.py`: Initializes database module.
- `database.py`: Handles **database connections.**

## `models/` (Data Models)

- `__init__.py`: Initializes **model definitions.**
- `user.py`: Defines the `User` model, including schema for **storing user data & handling authentication.**
- `energy_data.py`: Defines the `EnergyData` model, handling **energy consumption records.**

## `routes/` (API Endpoints)

- `__init__.py`: Initializes routing module.
- `user_routes.py`: Implements endpoints related to **user management.**
- `data_routes.py`: Implements endpoints for **energy data aggregation, filtering & analysis.**

## `tests/` (Testing Suite)

- `__init__.py`: Initializes the testing module.
- `test_users.py`: Contains unit tests for **user-related functionalities.**
- `test_data_routes.py`: Contains unit tests for **data aggregation, filtering & retrieval functionalities.**

---

# Features

+ **User Authentication** (FastAPI & OAuth2).
+ **Energy Data Aggregation** (filtering by *hourly, daily & weekly intervals*).
+ **MongoDB Integration** (NoSQL database).
+ **Secure API Endpoints** (JWT authentication & access control).
+ **Comprehensive Testing** (`pytest`).
+ **Containerization** (Docker).

---

# Setup & Running The Back-end

Install dependencies:
```bash
pip install -r requirements.txt
```

---

# Running Tests

To verify back-end functionality, run:
```bash
pytest app/tests/
```

---

# Generating Reports

## Generating CSV

```bash
curl -X 'POST' \
    'http://127.0.0.1:8000/api/v1/reports/report?format=csv'
```

## Generating PDF

```bash
curl -X 'POST' \
    'http://127.0.0.1:8000/api/v1/reports/report?format=pdf'
```

---
