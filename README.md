---
author: dzh-ma
---

# Project Setup Guide

This repository contains the **front-end & back-end** components of the project.

Follow the instructions below to set up & run both.

## Frontend Setup

The front-end is built with *React.js*.

1. **Install front-end dependencies**
```bash
npm install
```

2. **Run the front-end application**
```bash
npm run dev
```

3. **Access the application**
Once the front-end is running, open: `http://localhost:3000`.

## Backend Setup

The back-end is powered by *FastAPI* & *MongoDB*.

1. **Install back-end dependencies**
```bash
pip install -r backend/requirements.txt
```

2. **Ensure MongoDB is running**
```bash
sudo systemctl start mongodb
```

3. **Initialize the app using `uvicorn`**
```bash
uvicorn backend.main:app --reload 
```

4. **API documentation**
    Once the back-end is running, you may view the API by visiting: `http://127.0.0.1:8000/docs`

5. **Module documentation**
    You can find the documentation in PDF format ![here](./site/pdf/document.pdf)

---

# Running Tests

To verify back-end functionality, run:
```bash
pytest backend/app/tests/
```

---

# Generating Reports

## Generating CSV

```bash
# Generating access token (if using bash)
TOKEN=$(curl -s -X POST "http://127.0.0.1:8000/api/v1/users/token" \
    -d "username=test_user@example.com&password=TestPassword123!" \
    -H "Content-Type: application/x-www-form-urlencoded" | jq -r .access_token)

# Generating access token (if using fish)
set TOKEN $(curl -s -X POST "http://127.0.0.1:8000/api/v1/users/token" \
    -d "username=test_user@example.com&password=TestPassword123!" \
    -H "Content-Type: application/x-www-form-urlencoded" | jq -r .access_token)

# Executing command
curl -X POST "http://127.0.0.1:8000/api/v1/reports/report?format=pdf" \
    -H "Authorization: Bearer $TOKEN"
```

## Generating PDF

```bash
# Generating access token (if using bash)
TOKEN=$(curl -s -X POST "http://127.0.0.1:8000/api/v1/users/token" \
    -d "username=test_user@example.com&password=TestPassword123!" \
    -H "Content-Type: application/x-www-form-urlencoded" | jq -r .access_token)

# Generating access token (if using fish)
set TOKEN $(curl -s -X POST "http://127.0.0.1:8000/api/v1/users/token" \
    -d "username=test_user@example.com&password=TestPassword123!" \
    -H "Content-Type: application/x-www-form-urlencoded" | jq -r .access_token)

# Executing command
curl -X POST "http://127.0.0.1:8000/api/v1/reports/report?format=csv" \
    -H "Authorization: Bearer $TOKEN"
```

---
