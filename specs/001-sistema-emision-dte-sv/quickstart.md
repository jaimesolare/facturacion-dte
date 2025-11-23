# Quickstart: Sistema de Emisión de DTE

This guide provides instructions to set up and run the DTE emission system locally for development and testing.

**Technology Stack**:
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL 15+
- **Dependency Management**: Pip with `requirements.txt`

---

## 1. Prerequisites

- Python 3.11 or higher installed.
- PostgreSQL server running locally or accessible.
- Git installed.

## 2. Setup

### a. Clone the Repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### b. Create and Activate a Virtual Environment

It is highly recommended to use a virtual environment to manage project dependencies.

```bash
# For Windows
python -m venv venv
.\venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### c. Install Dependencies

Install all required Python packages.

```bash
pip install -r requirements.txt
```

### d. Configure Environment Variables

Create a `.env` file in the root of the project by copying the `.env.example` file. This file will contain the database connection string and credentials for the MH API.

```
# .env
DATABASE_URL="postgresql://user:password@localhost/dte_db"

# Credentials for MH Testing Environment
MH_AMBIENTE="PRUEBAS"
MH_NIT_USUARIO="YOUR_NIT"
MH_API_PASSWORD="YOUR_API_PASSWORD"
MH_CERT_PRIVATE_KEY_PATH="/path/to/your/private_key.pem"
MH_CERT_PUBLIC_KEY_PATH="/path/to/your/public_key.pem"
```

## 3. Database Setup

- Create a new PostgreSQL database (e.g., `dte_db`).
- Run the database migrations to create the necessary tables. The project will use a migration tool like Alembic.

```bash
alembic upgrade head
```

## 4. Running the Application

Use `uvicorn` to run the FastAPI application locally. It will provide hot-reloading for development.

```bash
uvicorn src.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## 5. Running Tests

Use `pytest` to run the test suite.

```bash
pytest
```
