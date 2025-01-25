# Team Roles

| Member                  | Role             | Formal Role            |
|-------------------------|------------------|------------------------|
| Laiba (ls2092)          | Front-end         | Organizational Manager |
| Razin (rm2131)          | Front-end         | Reporter               |
| Rhea (RheaDcosta5)      | Front-end         | Process Designer       |
| Aadi (AADISDEV)         | Front-end/Back-end | Project Administrator  |
| Gaurav (GauravHw2028)   | Front-end/Back-end | Project Researcher     |
| Nawid (MohammadNawid)   | Front-end/Back-end | Usability Analyst      |
| Matthew (MatthewBerry1) | Back-end          | Liaison                |
| Matin (dzh-ma)          | Back-end          | Technical Manager      |

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
        1) **IDEs**: Configure respective IDE to support necessary tools.
        2) **Docker**: Set up containers for back-end (FastAPI), front-end (React) & tools like Node-RED
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
    - Docker environments set up for back-end (FastAPI), front-end (React) & middleware (Node-RED).
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

1. **Development tools.**
    - *IDEs*: NeoVim configured with plugins for Python (FastAPI) & JavaScript (React).
    - *Version control*: GitHub for collaborative coding & issue tracking.
    - *Package managers*: `pip` for Python, `npm`/`yarn` for Node.js & React.
2. **Containerization.**
    - *Docker*: For isolated development environments.
    - *Docker Compose*: To manage multi-container setups for the back-end, front-end & middleware.
3. **Middleware & Frameworks.**
    - *Node-RED*: For workflow automation & testing device integrations.
    - *FastAPI*: Back-end framework for building REST APIs.
    - *React*: Front-end framework for UI/UV components.
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

- **Back-end**: FastAPI, Docker & NoSQL database.
- **Front-end**: React for form handling & validation.
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
        - Implement back-end logic to update database entires seamlessly.
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

- *Back-end*: FastAPI, MongoDB (NoSQL).
- *Front-end*: React for forms & profile UI.
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
        2) Create back-end logi to enforce role-based access.
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
        - Integrate scheduling logic with the back-end & devices.
    - **Subtasks**:
        1) Build a scheduling interface in the UI.
        2) Extend back-end to handle-time 
        3) Test middleware communication with devices for schedule execution.
    - **Assigned team members**: Gaurav, Matin & Nawid.
4. *End-to-end testing.*
    - **Task**: Validate the workflows for access control, device control & automation.
        - Test UI for intuitive navigation & usability.
        - Verify back-end logic & middleware.
    - **Subtasks**:
        1) Perform unit tests on each functionality.
        2) Conduct integration tests between UI, back-end & middleware.
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
    - UI & back-end support for managing & automating devices.
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
    - FastAPI for back-end API.
    - React for front-end development
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
        - Back-end support for time-based triggers.
    - **Subtasks**:
        1) Build a calendar or list-based interface for scheduling in the front-end.
        2) Develop back-end logic to store & process schedule configurations.
        3) Integrate middleware to execute device actions based on the schedule.
    - **Assigned team members**: Aadi, Matin & Gaurav.
2. *Develop energy consumption summary features (FR 6-1 to 6-3).*
    - **Task**: Create energy consumption summary dashboards.
        - Include historical data visualization & insights.
        - Provide comparisons across time periods (e.g., daily, weekly, monthly).
    - **Subtasks**:
        1) Build interactive charts & tables using a visualization tool (e.g., Grafana, Chart.js).
        2) Implement back-end endpoints to aggregate & fetch energy data.
        3) Design algorithms for generating actionable insights based on energy trends.
    - **Assigned team members**: Gaurav, Laiba & Razin.
3. *End-to-end testing.*
    - **Task**: Validate scheduling & energy summary functionalities.
        - Test features for usability, accuracy & performance.
    - **Subtasks**:
        1) Conduct unit tests for individual scheduling & summary modules.
        2) Perform integration testing between UI, back-end & middleware.
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
    - Fully functional scheduling UI & back-end integration.
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
    - FastAPI for back-end APIs.
    - React for front-end scheduling & dashboards.
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

### Steps to Success

1. *Data Aggregation and Backend Preparation*
    Task: Implement backend logic to process energy data for visualization and reporting.
        Design database queries to aggregate and summarize energy data.
        Develop API endpoints for fetching processed data.
    Subtasks:
        Design efficient database schemas for historical and real-time data storage.
        Create endpoints to support data retrieval for visualizations.
        Ensure backend handles data filtering (e.g., by time periods or devices).
    Assigned Team Members: Matin, Aadi, Gaurav
    Timeline: 26/01/2025 - 29/01/2025
2. *Develop Data Visualization Features*
    Task: Build frontend components to display energy data visually.
        Create interactive charts and graphs for energy usage trends.
        Add filtering and comparison options (e.g., daily, weekly, monthly views).
    Subtasks:
        Design UI components for data visualization using a library (e.g., Chart.js, Grafana).
        Integrate visualization components with backend APIs.
        Implement dynamic filtering and sorting options for user interaction.
    Assigned Team Members: Laiba, Razin, Nawid
    Timeline: 29/01/2025 - 02/02/2025
3. *Reporting Functionality*
    Task: Develop downloadable reports summarizing energy usage.
        Generate PDFs or CSV files with detailed metrics and trends.
    Subtasks:
        Build backend support for generating report files.
        Design a frontend interface for users to request and download reports.
        Include key metrics like energy cost estimates and savings suggestions.
    Assigned Team Members: Aadi, Matthew
    Timeline: 31/01/2025 - 03/02/2025
4. *Conduct Testing*
    Task: Validate the visualization and reporting features.
        Test for accuracy, performance, and usability.
    Subtasks:
        Perform unit testing for backend data processing and APIs.
        Conduct integration testing between frontend visualizations and backend.
        Test large datasets for performance and scalability.
    Assigned Team Members: Rhea, Razin
    Timeline: 02/02/2025 - 03/02/2025
5. *Documentation*
    Task: Document energy data and reporting workflows.
        Provide technical API documentation and user guides for visualization features.
    Subtasks:
        Write detailed documentation for backend API usage (e.g., endpoints, parameters).
        Create user manuals explaining how to use visualizations and generate reports.
    Assigned Team Members: Matthew, Gaurav
    Timeline: 03/02/2025 - 04/02/2025
6. *Final Validation and Deployment*
    Task: Conduct final review and deploy to the staging environment.
        Validate usability and receive feedback from stakeholders.
    Subtasks:
        Perform final usability testing with a small group of users.
        Deploy visualizations and reporting features to staging.
    Assigned Team Members: All team members
    Timeline: 04/02/2025 - 05/02/2025

### Key Deliverables

1. **Interactive Data Visualizations:**
    - Charts and graphs for energy usage trends with dynamic filtering.
2. **Reporting Features:**
    - Downloadable energy reports with detailed metrics and insights.
3. **Documentation:**
    - API documentation and user guides for data visualization and reporting.
4. **Testing Reports:**
    - Comprehensive results from performance, usability, and integration testing.

### Risk Management

- Risk: Performance issues with large datasets.
    - Mitigation: Use efficient database queries and caching mechanisms.
- Risk: Visualizations not intuitive or user-friendly.
    - Mitigation: Incorporate feedback from usability testing and improve UI design.
- Risk: Reports missing key metrics or incorrectly formatted.
    - Mitigation: Validate report content and formats through detailed testing.

### Required Tools

- **Development:**
    1. FastAPI for backend APIs.
    2. React for frontend visualizations and reporting interface.
- **Visualization:**
    1.  Chart.js, Grafana, or D3.js for creating charts and graphs.
- **Testing:**
    1. Postman for API testing.
    2. JMeter for performance testing.
    3. Selenium or Cypress for UI testing.
- **Documentation:**
    1. Markdown for technical documentation.
    2. Figma or similar tools for creating user guides.

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
