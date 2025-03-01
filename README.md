---
author: dzh-ma
---

# Project Setup Guide

This repository contains the **front-end & back-end** components of the project.

Follow the instructions below to set up & run both.

## Front-end Setup

The front-end is built with *React.js*.

1. **Navigate to the front-end directory**
```bash
cd frontend/
```

2. **Install front-end dependencies**
```bash
npm install
```

3. **Run the front-end application**
```bash
npm run dev
```

4. **Access the application**
Once the front-end is running, open: `http://localhost:5173`.

## Back-end Setup

The back-end is powered by *FastAPI* & *MongoDB*.

1. **Navigate to the back-end directory**
```bash
cd backend/
```

2. **Install back-end dependencies**
```bash
pip install -r requirements.txt
```

3. **Ensure MongoDB is running**
```bash
sudo systemctl start mongodb
```

4. **Initialize the app using `uvicorn`**
```bash
uvicorn main:app --reload 
```

5. **API documentation**
    Once the back-end is running, you may view the API by visiting: `http://127.0.0.1:8000/docs`

6. **Module documentation**
    You can find the documentation in PDF format ![here](./backend/site/pdf/document.pdf)

## Node-RED Setup

1. **Install Node-RED globally**
```bash
sudo npm install -g --unsafe-perm node-red
```

2. **Navigate to the Node-RED directory**
```bash
cd 
```

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
