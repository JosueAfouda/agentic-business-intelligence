# Agentic BI Frontend

React + Vite frontend for the Agentic BI backend API.

## Local development

1. Install dependencies:
   `npm install`
2. Copy `.env.example` to `.env.local` if you want to point to a remote backend.
3. Start the FastAPI backend from the repository root:
   `uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000`
4. Start the frontend:
   `npm run dev`

When `VITE_API_BASE_URL` is empty, Vite proxies `/api` requests to `http://127.0.0.1:8000`.
