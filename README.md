---
author: dzh-ma
---

# Setup

## Front-end Setup

1. **Navigate to the Front-end Directory**:
   ```bash
   cd frontend/pdtest/src
   ```

2. **Install front-end dependencies**:
   ```bash
   npm install formik react-phone-input-2 react-select react-router-dom axios
   ```

3. **Run the front-end application**:
   ```bash
   npm start
   ```

## Back-end Setup


1. **Navigate to the back-end directory**:
    ```bash
    cd backend
    ```
2. **Install back-end dependencies**:
    ```bash
    pip install fastapi uvicorn motor passlib pydantic
    ```
3. **Initialize the app using `uvicorn`**:
    ```bash
    uvicorn main:app --reload 
    ```


---
