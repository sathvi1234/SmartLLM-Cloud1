# SmartLLM Cloud - Backend API

## Setup Instructions

1. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup**
   Ensure PostgreSQL is running and accessible at the connection string in `app/core/config.py` or `.env`.
   
   Generate initial migration:
   ```bash
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

4. **Run Development Server**
   ```bash
   uvicorn app.main:app --reload
   ```

## Swagger Documentation
Once running, visit:
`http://localhost:8000/docs`
