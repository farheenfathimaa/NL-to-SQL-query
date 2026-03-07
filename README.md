# 📊 NL → SQL Query Assistant

A powerful Natural Language to SQL assistant that allows users to query a PostgreSQL database using plain English. Built with FastAPI, LangChain, Streamlit, and Gemini 1.5 Pro.

## 🚀 Features

- **Natural Language Querying**: Type questions like "What are the total sales by region?" and get SQL results.
- **Plain English Explanations**: The assistant explains the SQL results back to you in clear, simple English.
- **E-commerce Data Schema**: Includes a structured dataset with regions, sales reps, products, and orders.
- **Full Stack Dockerization**: Easily deploy the entire system (Database, Backend, Frontend) with a single command.

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **AI/LLM**: LangChain + Google Gemini 1.5 Pro
- **Frontend**: Streamlit
- **Database**: PostgreSQL
- **Infrastructure**: Docker & Docker Compose

## 🏃 How to Run

### 1. Prerequisites
- Docker & Docker Compose installed on your machine.
- A Google API Key (for Gemini).

### 2. Setup Environment Variables
Create a `.env` file in the root directory (or use the one already provided) with the following content:
```env
GOOGLE_API_KEY=your_google_api_key_here
```

### 3. Spin up the Containers
Run the following command to build and start the services:
```bash
docker-compose up --build
```

### 4. Initialize the Database (Mock Data)
Once the containers are running, populate the database with mock e-commerce data by executing:
```bash
docker-compose exec backend python models.py
```

### 5. Access the App
- **Streamlit UI**: [http://localhost:8501](http://localhost:8501)
- **FastAPI Backend (Docs)**: [http://localhost:8000/docs](http://localhost:8000/docs)

## 📂 Project Structure

- `/backend`: FastAPI service, SQLAlchemy models, and LangChain logic.
- `/frontend`: Streamlit application for the user interface.
- `docker-compose.yml`: Orchestrates the PostgreSQL, Backend, and Frontend services.

## 🧪 Example Queries
- "Show me total sales by region for last quarter"
- "Who is the top sales rep by total sales value?"
- "List all electronic products and their prices"
- "How many orders were placed in the last 30 days?"