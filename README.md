# Social Network API

A modern, high-performance RESTful API for a social network platform, supporting user management, posts, followers, and likes. Built leveraging asynchronous programming with FastAPI and PostgreSQL.

## Project Purpose & Core Features

The primary purpose of this project is to serve as a robust, scalable, and secure asynchronous **Back-End Engine** for a modern social network platform. It handles the core business logic, data persistence, and security protocols required to power a dynamic user ecosystem.

This project implements and demonstrates the following core functionalities:

- **User Management & Security:** Secure user registration and authentication utilizing encrypted password hashing (bcrypt) and transient JWT (JSON Web Tokens) for stateless session handling.
- **Content Management (Posts):** Full CRUD (Create, Read, Update, Delete) capabilities for user-generated posts, enabling interactive content feeds.
- **Social Graph (Follows):** A dynamic relationship system managing follower/following connections between users to build personalized networks.
- **Interactions (Likes):** Real-time tracking and management of user interactions (likes) on platform posts.

### Technical Objectives

From a developer standpoint, this repository is designed to showcase proficiency in production-ready back-end patterns:

1. **Asynchronous Architecture:** Utilizing `FastAPI` and `asyncpg` to build a non-blocking, event-driven API capable of handling concurrent traffic with low latency.
2. **Modular Design:** Demonstrating a clean architecture by separating route handling (`routers`), database definitions (`models`), data validation (`schemas`), and business logic.
3. **Database Efficiency:** Implementing advanced object-relational mapping using `SQLAlchemy 2.0` with asynchronous session management for highly efficient PostgreSQL queries.

---

## Stack & Dependencies

| Component | Technology | Version |
|---|---|---|
| Language | Python | 3.11+ |
| Framework | FastAPI | 0.110.0 |
| ASGI Server | Uvicorn | 0.27.0 |
| ORM | SQLAlchemy | 2.0.23 |
| Database Driver | Asyncpg | 0.29.0 |
| Data Validation | Pydantic | 2.5.2 |

---

## Project Structure

```text
social-network/
│
├── .env                  # Environment configurations (Database, JWT)
├── requirements.txt      # Python dependencies
├── README.md             # Documentation
│
└── app/
    ├── __init__.py
    ├── main.py           # Application Entrypoint
    ├── config.py         # App configuration schema
    ├── db.py             # Database session setup
    ├── models.py         # SQLAlchemy database models
    ├── schemas.py        # Pydantic validation schemas
    ├── auth.py           # Security & JWT Token generation
    ├── utils.py          # Helper functions
    │
    ├── templates/        # UI Layer
    │   └── index.html    # Interactive Dashboard Root page
    │
    └── routers/
        ├── __init__.py
        ├── users.py      # Registration, login, and profile endpoints
        ├── posts.py      # Post creation, retrieval, and interactions
        └── follows.py    # User connections and follower networking
```

---

## Environment Configuration

Create a `.env` file in the root directory of the project and populate it with the following configuration:

```env
DATABASE_URL=postgresql+asyncpg://postgres:123456@localhost:5432/social_network
SECRET_KEY=teste123456789
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> **Note:** Ensure you have created a local PostgreSQL database named `social_network` before initializing the server.

---

## Getting Started (Step-by-Step)

Follow these steps to set up the environment and run the API server locally:

### 1. Clone the repository and navigate to the project directory

```bash
cd social-network
```

### 2. Create a Python 3.11 virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

**Windows (Command Prompt):**
```dos
.venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
source .venv/bin/activate
```

### 4. Upgrade pip and install dependencies

If you encounter compilation issues installing binary components like `asyncpg` or `pydantic-core` on Windows, make sure you upgrade your setup tools first:

```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 5. Run the application

Start the Uvicorn ASGI development server:

```bash
uvicorn app.main:app --reload
```

The application will be served locally at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

---

## API Documentation & UI

Once the application is running, you can access the interactive UI interfaces directly through your web browser:

| Interface | URL | Description |
|---|---|---|
| Interactive Dashboard | [http://127.0.0.1:8000/](http://127.0.0.1:8000/) | Custom landing page |
| Swagger UI | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) | Interactive API testing |
| ReDoc | [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) | Structured documentation |
| OpenAPI Specification | [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json) | Raw OpenAPI schema |

---

## Requirements

Ensure your `requirements.txt` matches exactly this content:

```text
fastapi==0.110.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.23
asyncpg==0.29.0
pydantic==2.5.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
jinja2>=3.1.2
```

> `jinja2` was added at the end because it's required by FastAPI to serve the custom `index.html` template via `Jinja2Templates`.
