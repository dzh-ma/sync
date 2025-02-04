---
author: dzh-ma
---

# Tech Stack

## Front-end

1. **React.js**
    - Ensure compatibility with existing UI libraries and mock-ups.
    - Validate re-usability of components and support for dynamic user interfaces.
2. **CSS Frameworks (e.g., Tailwind CSS, Bootstrap)**
    - Ensure responsiveness across various screen sizes.
    - Validate support for theme customization and accessibility compliance.

## Back-end

1. **FastAPI**
    - Test endpoint performance under varying loads.
    - Verify asynchronous handling for real-time device communication and high concurrency.
2. **MongoDB (NoSQL Database)**
    - Validate schema design for scalability and fault tolerance.
    - Test performance for time-series data storage and retrieval.
3. **Python**
    - Ensure seamless integration with FastAPI.
    - Verify database operations, authentication, and data processing functionalities.

## Middleware

1. **Node-RED**
    - Simulate and test workflows for device automation.
    - Ensure seamless communication between devices and the back-end.

## Infrastructure

1. **Docker**
    - Configure containerized environments for all components.
    - Test orchestration with Docker Compose to ensure smooth interactions between containers (e.g., back-end, front-end, middleware).

## Security

1. **OAuth2** (User Authentication)
    - Validate token generation, revocation, and session expiration functionalities.
    - Ensure proper handling of role-based access control.
2. **SSL/TLS** (Data Encryption)
    - Verify secure communication between front-end, back-end, and third-party integrations using certificates.

## Usability Tools

1. **Figma**
    - Validate UI mock-ups against stakeholder requirements and user feedback.
    - Incorporate usability testing feedback to improve design iterations.
2. **Grafana**
    - Configure dashboards to visualize real-time and historical energy consumption metrics.

## Testing Frameworks

1. **Unit Testing**
    - Test individual FastAPI endpoints and React components for expected functionality.
    - Use tools like `pytest` for Python and `Jest` for React.
2. **Integration Testing**
    - Ensure seamless communication between front-end, back-end, and the database.
    - Use tools like `Postman` or `Cypress` for API and end-to-end testing.
3. **Performance Testing**
    - Simulate load tests using tools like `Apache JMeter` or `k6` to evaluate system scalability and fault tolerance.

---
