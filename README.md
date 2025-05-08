**Survey Data Collection API**

**Project Overview**

This project is a modular, RESTful Flask API designed for robust offline-first field data collection in hard-to-reach communities. It supports complex, skip-logic-driven surveys across multiple thematic sections such as Education, Economic Empowerment, Access to Assistive Technology, GBV Awareness, Digital Inclusion, and more.

**Key Features**

**User Authentication**: Secure JWT-based login for enumerators and admins.

**Role-Based Access Control**: Enumerators can register participants and submit responses; admins have extended permissions.

**Dynamic Survey Structure**: Supports skip logic and follow-up questions, with questions grouped by section and phase (Baseline/Endline).

**Offline-First**: Mobile frontend can cache questions and submit responses offline, syncing when internet is available.

**Batch Sync**: Supports batch upload of responses for efficient offline data collection.

**Survey Structure and Logic**

The survey is organized into multiple sections, each with its own set of questions, options, and logical flows. Below is a sample of the Education section for the Baseline phase, illustrating how questions and follow-ups are structured.

**Education Section** – Example Flow
Q1. Are you currently enrolled in any of these educational programs? (Can select more than one)

Options: Formal, Vocational, Both, None

Logic:

If "Formal", "Vocational", or "Both" → Q1a

If "None" → Q1b

Q1a. How many hours do you spend on the program (If options 1, 2, or 3 is picked)

Options: Less than 5, 5-10, 10-15, More than 15

Q1b. If none, would you like to be enrolled?

Options: Yes, No

Logic:

If "Yes" → Q1c

Q1c. If Yes, which of them would you like to be enrolled in?

Options: Formal, Vocational

Q2. Have you received any assistive devices to help with your education?

Options: Yes, No

Q3. How often do you attend classes or educational sessions?

Options: Daily, Weekly, Monthly

Q4. How has the availability of assistive technologies (if any) impacted your ability to pursue education?

Options: Not impacted, Barely impacted, Moderately impacted, Greatly impacted

Q5. What challenges do you face in accessing education, especially as a person with a disability?

Options: Input box (open-ended)

Q6. What kind of support do you think would improve your access to education?

Options: Input box (open-ended)

**Survey Sections**

**Education**

**Economic Empowerment**

**Access to Assistive Technology**

**GBV Awareness and Protection**

**Digital Inclusion**

**Overall Well-being and Community Support**

**Financial Inclusion**

**Mentorship**

**Phases**

Baseline

Endline

**Skip Logic**

Questions can have follow-up questions based on specific answers (e.g., if "None" is selected in Q1, go to Q1b).

Options can trigger different branches in the survey flow.

Some questions (e.g., Q5, Q6) allow for open-ended responses.


**API Endpoints **(Sample)

POST /api/auth/login - User login

POST /api/participants/register - Register a new participant

GET /api/participants/questions?phase=Baseline - Load all questions for selected phase (with skip logic)

POST /api/participants/answers - Submit participant answers (supports batch)

GET /api/questions/flow?phase=Baseline - Get full question flow for offline caching

**Technologies**

Flask & Flask-RESTful

SQLAlchemy (PostgreSQL/Neon or SQLite)

Flask-JWT-Extended for authentication

Flask-Migrate for migrations

**Deployment**

Ready for deployment on Render.com or similar platforms.

Database can be local SQLite (for development) or Neon PostgreSQL (for production).

See .env.example for environment variable setup.

**Usage**
Clone the repo and install dependencies.

Set up your .env file with your database connection string.

**Run migrations**:
flask db upgrade

**Start the server**:
flask run

Use the API from your mobile frontend or API client.

**License**

MIT License

For more details, see the API documentation or contact the project maintainer.