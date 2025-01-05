# Team Roles

| Member                  | Role             | Formal Role            |
|-------------------------|------------------|------------------------|
| Laiba (ls2092)          | Frontend         | Organizational Manager |
| Razin (rm2131)          | Frontend         | Reporter               |
| Rhea (RheaDcosta5)      | Frontend         | Process Designer       |
| Aadi (AADISDEV)         | Frontend/Backend | Project Administrator  |
| Gaurav (GauravHw2028)   | Frontend/Backend | Project Researcher     |
| Nawid (MohammadNawid)   | Frontend/Backend | Usability Analyst      |
| Matthew (MatthewBerry1) | Backend          | Liaison                |
| Matin (dzh-ma)          | Backend          | Technical Manager      |

---

# Tech Stack

## Frontend

1. **React.js**
    - Ensure compatibility with existing UI libraries and mockups.
    - Validate reusability of components and support for dynamic user interfaces.
2. **CSS Frameworks (e.g., Tailwind CSS, Bootstrap)**
    - Ensure responsiveness across various screen sizes.
    - Validate support for theme customization and accessibility compliance.

## Backend

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
    - Ensure seamless communication between devices and the backend.

## Infrastructure

1. **Docker**
    - Configure containerized environments for all components.
    - Test orchestration with Docker Compose to ensure smooth interactions between containers (e.g., backend, frontend, middleware).

## Security

1. **OAuth2** (User Authentication)
    - Validate token generation, revocation, and session expiration functionalities.
    - Ensure proper handling of role-based access control.
2. **SSL/TLS** (Data Encryption)
    - Verify secure communication between frontend, backend, and third-party integrations using certificates.

## Usability Tools

1. **Figma**
    - Validate UI mockups against stakeholder requirements and user feedback.
    - Incorporate usability testing feedback to improve design iterations.
2. **Grafana**
    - Configure dashboards to visualize real-time and historical energy consumption metrics.

## Testing Frameworks

1. **Unit Testing**
    - Test individual FastAPI endpoints and React components for expected functionality.
    - Use tools like `pytest` for Python and `Jest` for React.
2. **Integration Testing**
    - Ensure seamless communication between frontend, backend, and the database.
    - Use tools like `Postman` or `Cypress` for API and end-to-end testing.
3. **Performance Testing**
    - Simulate load tests using tools like `Apache JMeter` or `k6` to evaluate system scalability and fault tolerance.

---

# Sprints

## Sprint 7: Technical Preparation

**Goal**
- Ensure all technical tools, libraries, and environments are installed, configured, and tested for smooth development.

**Tasks**
- Set up and test tools like IDEs, Docker, Node-RED, React, and FastAPI.
- Prototype UI/UX review to validate alignment with requirements.

*Start Date*: 15/12/2024  
*End Date*: 20/12/2024  

### Steps To Completion

1. *Technical Preparation.*
    - Ensure all necessary technical tools are installed & configured.
        1) **IDEs**: Configure NeoVim to support necessary tools.
        2) **Docker**: Set up containers for backend (FastAPI), frontend (React) & tools like Node-RED
        3) **Node-RED**: Test integration for automation workflows.
        4) **FastAPI & React**: Verify that these frameworks are operational in your development environment.
    - Test libraries & modules to ensure compatibility with the project requirements.
2. *Prototype Validation.*
    - Conduct UI/UX prototype reviews.
        - Validate that the prototype meets functional requirements such as accessibility features, intuitive design & navigation.
        - Address areas of improvement based on mockups & usability feedback.
3. *Team Coordination.*
    - Assign specific tools to team members based on their roles.
    - Schedule stand-ups to report progress, blockers & resolutions.

### Key Deliverables

1. **Functional development environments.**
    - Fully configured IDEs tailored to the project's tech stack.
    - Docker environments set up for backend (FastAPI), frontend (React) & middleware (Node-RED).
    - Verified integrations for libraries & modules critical to development.
2. **Validated prototype.**
    - UI/UX prototype reviewed & confirmed to meet functional requirements (e.g., accessibility, intuitive navigation).
    - Feedback from mockups & usability testing incorporated into the design.
3. **Technical readiness documentation.**
    - Clear documentation of environment setup steps.
    - Tool usage instructions for team members.
    - List of resolved & pending issues from prototype reviews.

### Risk Mitigation Strategies

| Risk                                          | Mitigation                                                                           |
|-----------------------------------------------|--------------------------------------------------------------------------------------|
| Tools & libraries not functioning as expected | Test each tool & library in isolation before integration & maintain fallback options |
| Misalignment between prototype & requirements | Regular prototype reviews with team feedback loops                                   |
| Delays in setting up Docker environments      | Assign experienced membesr to oversee Docker setup.                                  |
| Team members unfamiliar with specific tools   | Conduct mini-training sessions or share tutorials on the tools                       |

### Required Tools

1. **Developemnt tools.**
    - *IDEs*: NeoVim configured with plugins for Python (FastAPI) & JavaScript (React).
    - *Version control*: GitHub for collaborative coding & issue tracking.
    - *Package managers*: `pip` for Python, `npm`/`yarn` for Node.js & React.
2. **Containerization.**
    - *Docker*: For isolated development environments.
    - *Docker Compose*: To manage multi-container setups for the backend, frontend & middleware.
3. **Middleware & Frameworks.**
    - *Node-RED*: For workflow automation & testing device integrations.
    - *FastAPI*: Backend framework for building REST APIs.
    - *React*: Frontend framework for UI/UV components.
4. **Testing & Validation.**
    - *Postman*: API testing.
    - *Selenium*: UI functionality testing.
    - *Cypress*: End-to-end testing for React components.
5. **Documentation & Prototyping.**
    - *Figma*: UI/UX Prototype.
    - *Markdown*: For documenting setup processes & team guidelines.

## Sprint 8: User Registration and Login Workflow

**Goal**
- Implement and test user authentication functionalities.

**Tasks**
- Implement user registration, email verification, and password setup.
- Enable login functionality and document the process.
- Conduct end-to-end testing.

*Start Date*: 20/12/2024  
*End Date*: 04/01/2025  

### Steps To Completion

1. *User Registration (FR 1-1, FR 1-2).*
    - **Task**: Code the user registration feature.
        - Implement fields for email & password.
        - Validate email format & password strength.
    - **Assigned team members**: Aadi, Matin, Gaurav, Nawid.
2. *Email Verification (FR 1-3).*
    - **Task**: Implement email verification.
        - Generate & send verification emails upon registration.
        - Create endpoints for email verification link validation.
    - **Assigned team members**: Aadi, Matin, Laiba.
3. *End-to-End Registration Testing.*
    - **Task**: Validate the entire registration workflow.
        - Test edge cases (e.g., invalid email formats, short passwords).
        - Ensure seamless user flow from registration to email verification.
    - **Assigned team members**: Gaurav, Laiba, Rhea.
4. *User login (FR 1-4).*
    - **Task**: Enable login functionality.
        - Authenticate user credentials against the database.
        - Implement session management (e.g., JWT or OAuth2).
    - **Assigned team members**: Aadi, Matin.
5. *Documentation.*
    - **Task**: Document the entire user registration & login workflow.
        - Include API endpoints, payload formats & example responses.
        - Detail error handling mechanisms for developers & testers.
6. *Final End-to-End Testing.*
    - **Task**: Conduct comprehensive tests.
        - Perform usability testing to validate ease of use.
        - Verify security measures (e.g., input sanitization, session expiration).
    - **Assigned team members**: All members for testing.

### Key Deliverables

1. **Fully functional user authentication system.**
    - Registration with email/password.
    - Email verification flow.
    - Login & session management.
2. **Technical documentation.**
    - API endpoint details, workflows & error handling.
3. **End-to-End test reports.**
    - Usability & functionality testing results.

### Risk Management

| Risk                              | Mitigation                                          |
|-----------------------------------|-----------------------------------------------------|
| Email delivery issues             | Use a robust email service like SendGrid or AWS SES |
| Delayed completion due to holiday | Schedule tasks flexibly & prepare fallback plans    |

### Required Tools

- **Backend**: FastAPI, Docker & NoSQL database.
- **Frontend**: React for form handling & validation.
- **Testing**: Postman (API testing) & Selenium (UI testing).

## Sprint 9: Profile Creation and Management

**Goal**
- Develop and validate profile-related features.

**Tasks**
- Code and test functionalities for profile creation, editing, and password management.
- Document the workflow.

*Start Date*: 03/01/2025  
*End Date*: 10/01/2025  

### Steps To Completion

1. *Profile Creation (FR 2-1, FR 2-5).*
    - **Task**: Code the profile creation feature.
        - Develop forms for the user details input (e.g., name, age, profile type).
        - Implement admin optinos to create child & adult profiles.
        - Ensure all data is securely stored in the database.
    - **Assigned team members**: Aadi, Matin, Nawid & Matthew.
2. *Profile Editing (FR 2-2, FR 2-3).*
    - **Task**: Implement editing functionality.
        - Allow admins to update profile details.
        - Ensure proper validation for edited fields.
        - Implement backend logic to update database entires seamlessly.
    - **Assigned team members**: Aadi, Nawid, Matthew.
3. *Password Management (FR 2-3, FR 2-4, FR 2-5).*
    - **Task**: Code password setup & update features.
        - Create a flow for admins to set or update passwords for individual profiles.
        - Implement password validation rulse (e.g., length, complexity).
        - Provide options for resetting passwords securely.
    - **Assigned team members**: Aadi, Gaurav, Matin.
4. *End-to-End Testing.*
    - **Task**: Validate all profile-related functionalities.
        - Test profile creation, editing & password management workflows.
        - Include edge case testing (e.g., invalid inputs, large data).
        - Ensure no regressions from Sprint 8 features.
    - **Assigned team members**: Gaurav, Laiba, Rhea.
5. *Documentation.*
    - **Task**: Document the profile creation & management workflow.
        - Detail API endpoints & parameters for profile-related operations.
        - Create user & developer documentation for the implemented features.
    - **Assigned team members**: Matthew, Razin, Gaurav.
6. *Final Validation & Deployment.*
    - **Task**: Conduct final validation.
        - Perform usability testing to confirm intuitive design.
        - Deploy tested features to the staging environment for further review.
    - **Assigned team members**: All members for final validation.

### Key Deliverables

1. **Fully functional profile features.**
    - Profile creation, editing & password management functionalities.
2. **Documentation.**
    - API details, workflows & user guides.
3. **End-to-End test reports.**
    - Usability & functionality testing outcomes.

### Risk Management

| Risk                                      | Mitigation                                                                      |
|-------------------------------------------|---------------------------------------------------------------------------------|
| Profile data inconsistency in database    | Strict validation & database transaction management                             |
| Overlapping tasks from Sprint 8 or delays | Assign priority-based tasks & schedule buffer time for critical functionalities |

### Required Tools

- *Backend*: FastAPI, MongoDB (NoSQL).
- *Frontend*: React for forms & profile UI.
- *Testing*: Postman (API testing) & Cypress/Selenium (UI testing).

## Sprint 10: Profile Access and Device Control

**Goal**
- Enable access control and remote device management.

**Tasks**
- Implement access controls for profiles.
- Develop features for device control and automation.
- Test and validate workflows.

*Start Date*: 10/01/2025  
*End Date*: 19/01/2025  

### Steps To Completion

1. *Implement profile creation access control (FR 3-1 to 3-4).*
    - **Task**: Enable role-based access for profiles.
        - Admin access to manage devices, notifications & data.
        - Child & guest profiles with restricted or view-only permissions.
    - **Subtasks**:
        1) Develop UI to configure access settings.
        2) Create backend logi to enforce role-based access.
        3) Validate database schema to handle role-based permissions.
    - **Assigned team members**: Aadi, Matin & Nawid.
2. *Develop device control features (FR 4-1 to 4-2).*
    - **Task**: Allow users to remotely manage devices.
        - Turn devices on/off, schedule operations & adjust settings.
    - **Subtasks**:
        1) Create UI components for device listing & actionponents for device listing & actions.
        2) Implement API endpoints for device state management.
        3) Develop middleware logic for scheduling & automation.
    - **Assigned team members**: Aadi, Gaurav & Matthew.
3. *Implement automation rules (FR 5-1 to 5-2).*
    - **Task**: Enable device automation based on user-defined schedules.
        - Add options to configure schedules (daily, custom).
        - Integrate scheduling logic with the backend & devices.
    - **Subtasks**:
        1) Build a scheduling interface in the UI.
        2) Extend backend to handle-time 
        3) Test middleware communication with devices for schedule execution.
    - **Assigned team members**: Gaurav, Matin & Nawid.
4. *End-to-end testing.*
    - **Task**: Validate the workflows for access control, device control & automation.
        - Test UI for intuitive navigation & usability.
        - Verify backend logic & middleware.
    - **Subtasks**:
        1) Perform unit tests on each functionality.
        2) Conduct integration tests between UI, backend & middleware.
        3) Simulate real-world scenarios (e.g., multiple user roles managing devices).
    - **Assigned team members**: Rhea, Laiba & Razin.
5. *Documentation.*
    - **Task**: Document access control & device management workflows.
        - Include API endpoints, expected inputs/outputs & examples.
        - Provide user guide for configuring access & managing devices.
    - **Subtasks**:
        1) Write technical documentation for developers.
        2) Create user-facing guides with visuals.
    - **Assigned team members**: Matthew & Razin.

### Key Deliverables

1. **Fully role-based access control.**
    - Configurable profile-based access settings.
2. **Remote device management features.**
    - UI & backend support for managing & automating devices.
3. **End-to-end testing reports.**
    - Functional & usability test results for all features.
4. **Documentation.**
    - Technical & user facing documentation for implemented features.

### Risk Management

| Risk                                                            | Management                                              |
|-----------------------------------------------------------------|---------------------------------------------------------|
| Misconfigured access permissions leading to unauthorized access | Implement rigorous validation & role-specific tasks     |
| Automation schedules failing under specific scenarios           | Add extensive logging & debugging options for schedules |

### Required Tools

- *Development.*
    - FastAPI for backend API.
    - React for frontend development
    - Node-RED for testing automation logic.
- *Testing.*
    - Postman for API testing.
    - Cypress/Selenium for UI testing.
    - Docker for isolated environment testing.
- *Documentation.*
    - Markdown for technical documentation.
    - Figma for user guides & visuals.

## Sprint 11: Advanced Features and Summaries

**Goal**
- Add scheduling for device automation and energy consumption summaries.

**Tasks**
- Develop scheduling and summary features.
- Validate through testing.
- Document all functionalities.

*Start Date*: 19/01/2025  
*End Date*: 29/01/2025  

### Steps To Completion

1. *Develop scheduling features (FR 5-1 to 5-2).*
    - **Task**: Enable users to schedule device operations.
        - Add UI for creating, updating & deleting schedules.
        - Backend support for time-based triggers.
    - **Subtasks**:
        1) Build a calendar or list-based interface for scheduling in the frontend.
        2) Develop backend logic to store & process schedule configurations.
        3) Integrate middleware to execute device actions based on the schedule.
    - **Assigned team members**: Aadi, Matin & Gaurav.
2. *Develop energy consumption summary features (FR 6-1 to 6-3).*
    - **Task**: Create energy consumption summary dashboards.
        - Include historical data visualization & insights.
        - Provide comparisons across time periods (e.g., daily, weekly, monthly).
    - **Subtasks**:
        1) Build interactive charts & tables using a visualization tool (e.g., Grafana, Chart.js).
        2) Implement backend endpoints to aggregate & fetch energy data.
        3) Design algorithms for generating actionable insights based on energy trends.
    - **Assigned team members**: Gaurav, Laiba & Razin.
3. *End-to-end testing.*
    - **Task**: Validate scheduling & energy summary functionalities.
        - Test features for usability, accuracy & performance.
    - **Subtasks**:
        1) Conduct unit tests for individual scheduling & summary modules.
        2) Perform integration testing between UI, backend & middleware.
        3) Simulate scenarios (e.g., overlapping schedules, large data sets).
    - **Assigned team members**: Rhea, Nawid & Razin.
4. *Documentation.*
    - **Task**: Document scheduling & energy summary workflows.
        - Provide API documentation for developers & guides for users.
    - **Subtasks**:
        1) Write API documentation detailing endpoints.
        2) Create user guides with screenshots or diagrams.
    - **Assigned team members**: Matthew & Razin.
5. *Final review & deployment*:
    - **Task**: Conduct final review & deploy to staging.
        - Validate user experience with stakeholders & team members.
    - **Subtasks**:
        1) Perform usability testing with a small group of users.
        2) Deploy features to the staging environment for feedback.
    - **Assigned team members**: All team members.

### Key Deliverables

1. **Scheduling features.**
    - Fully functional scheduling UI & backend integration.
2. **Energy consumption summary.**
    - Interactive & informative dashboards with energy usage trends.
3. **End-to-end testing reports.**
    - Comprehensive test results for scheduling & summary features.
4. **Documentation.**
    - API documentation & user guides for the new functionalities.

### Risk Mitigation

| Risk                                         | Mitigation                                                          |
|----------------------------------------------|---------------------------------------------------------------------|
| Scheduling conflicts or execution failures   | Implement conflict detection logic & extensive error handling       |
| Large datasets impacting summary performance | Optimize database queries & implement caching for frequent data     |
| User interface complexity for summaries      | Simplify UI design with clear labels & user friendly visualizations |

### Required Tools

1. *Development.*
    - FastAPI for backend APIs.
    - React for frontend scheduling & dashboards.
    - Node-RED for automation testing.
2. *Visualization.*
    - Grafana or Chart.js for energy data visualizations.
3. *Testing.*
    - Postman for API validation.
    - Cypress/Selenium for UI tests.
    - JMeter for performance testing.
4. *Documentation.*
    - Markdown for technical docs.
    - Figma for creating user guides.

## Sprint 12: Energy Data and Reporting

**Goal**
- Implement energy visualization and reporting functionalities.

**Tasks**
- Create data visualization features.
- Conduct testing and finalize documentation.

*Start Date*: 26/01/2025  
*End Date*: 05/02/2025  

### Steps To Completion

1. *Develop scheduling features (FR 5-1 to 5-2).*
    - **Task**: Enable users to schedule device operations.
        - Add UI for creating, updating & deleting schedules.
        - Backend support for time-based triggers.
    - **Subtasks**:
        1) Build a calendar or list-based interface for scheduling in the frontend.
        2) Develop backend logic to store & process schedule configurations.
        3) Integrate middleware to execute device actions based on the schedule.
    - **Assigned team members**: Aadi, Matin & Gaurav.
2. *Develop energy consumption summary features (FR 6-1 to 6-3).*
    - **Task**: Create energy consumption summary dashboards.
        - Include historical data visualization & insights.
        - Provide comparisons across time periods (e.g., daily, weekly, monthly).
    - **Subtasks**:
        1) Build interactive charts & tables using a visualization tool (e.g., Grafana, Chart.js).
        2) Implement backend endpoints to aggregate & fetch energy data.
        3) Design algorithms for generating actionable insights based on energy trends.
    - **Assigned team members**: Gaurav, Laiba, Razin.
    - **Assigned team members**: Rhea, Nawid, Razin.
3. *Reporting functionality.*
    - **Task**: Develop downoadable reports summarizing energy usage.
        - Generate PDFs or CSV files with detailed metrics & trends.
    - **Subtasks**:
        1) Build bakcend support for generating report files.
        2) Design a frontend interface for users to request & download reports.
        3) Include key metrics like energy cost estimates & savings suggestions.
    - **Assigned team members**: Aadi, Matthew.
4. *Conduct testing.*
    - **Task**: Validate the visualization & reporting features.
        - Test for accuracy, performance & usability.
    - **Subtasks**:
        1) Perform unti testing for backend data processing & APIs.
        2) Conduct integration testing between frontend visualization & backend.
        3) Test large datasets for performance & scalability.
    - **Assigned team members**: Rhea, Razin.
5. *Documentation.*
    - **Task**: Document energy data & reporting workflows.
        - Provide technical API documentation & user guides for visualization features.
    - **Subtasks**:
        1) Write detailed documentation for backend API usage (e.g., endpoints, parameters).
        2) Create user manuals explaining how to use visualizations & generate reports.
    - **Assigned team members**: Matthew, Gaurav.
6. *Final validation & deployment.*
    - **Task**: Conduct final review & deploy to the staging environment.
        - Validate usability & recieve feedback from stakeholders.
    - **Subtasks**:
        1) Perform final usability testing with a small group of users.
        2) Deploy visualizations & reporting features to staging.
    - **Assigned team members**: All team members.

### Key Deliverables

1. **Interactive data visualizations.**
    - Charts & graphs for energy usage trends with dynamic filtering.
2. **Reporting features.**
    - Downloadable energy reports with detailed metrics & insights.
3. **Documentation.**
    - API documentation & user guides for data visualization & reporting.
4. **Testing reports.**
    - Comprehensive results from performance, usability & integration testing.

### Risk Management

| Risk                                                 | Mitigation                                                      |
|------------------------------------------------------|-----------------------------------------------------------------|
| Performance isues with lareg datasets                | Use efficient database queries & caching mechanisms             |
| Visualizations not user friendly                     | Incorporate feedback from usability testing & improve UI design |
| Reports missing key metrics or incorrectly formatted | Validate report content & formats through detailed testing      |

### Required Tools

- *Development.*
    - FastAPI for backend APIs.
    - React for frontend visualizations & reporting interface.
- *Visualizations.*
    - Chart.js, Grafana or D3.js for creating charts & graphs.
- *Testing.*
    - Postman for API testing.
    - JMeter for performance testing.
    - Selenium or Cypress for UI testing.
- *Documentation.*
    - Markdown for technical documentation.
    - Figma or similar tools for creating user guides.

## Sprint 13: Implement NFRs – Reliability & Performance

**Goal**
- Focus on system uptime, fault tolerance, and scalability.

**Tasks**
- Implement monitoring and crash recovery mechanisms.
- Test reliability and recovery mechanisms.

*Start Date*: 04/02/2025  
*End Date*: 09/02/2025  

## Sprint 14: Implement NFRs – Security and Usability

**Goal**
- Enhance system security and accessibility.

**Tasks**
- Add encryption, backups, and WCAG-compliant features.
- Validate these features.

*Start Date*: 09/02/2025  
*End Date*: 13/02/2025  

## Sprint 15: Final Testing

**Goal**
- Conduct comprehensive system integration and performance testing.

**Tasks**
- Perform system integration testing.
- Validate performance under realistic conditions.
- Final usability testing.

*Start Date*: 13/02/2025  
*End Date*: 16/02/2025  

## Sprint 16: Marketing

**Goal**
- Develop and finalize marketing strategies and materials.

**Tasks**
- Conduct audience research and create marketing materials.
- Refine and finalize the strategy.

*Start Date*: 26/02/2025  
*End Date*: 26/02/2025  

## Sprint 17: Report Formatting and Submission

**Goal**
- Compile and submit the final report.

**Tasks**
- Consolidate all sections into one document.
- Format and proofread the report.
- Submit the completed work.

*Start Date*: 26/02/2025  
*End Date*: 28/02/2025  

---
