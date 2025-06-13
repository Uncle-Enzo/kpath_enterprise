# Running KPath Enterprise

## Prerequisites
- Python 3.9+ with pyenv
- Node.js 18+ and npm
- PostgreSQL database
- Redis (for future caching)

## Backend Setup

1. Activate Python environment:
```bash
pyenv activate torch-env
```

2. Navigate to project root:
```bash
cd /Users/james/claude_development/kpath_enterprise
```

3. Install backend dependencies (if needed):
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. Run database migrations:
```bash
alembic upgrade head
```

6. Start the backend server:
```bash
cd backend
python main.py
```

The backend API will be available at http://localhost:8000

## Frontend Setup

1. Open a new terminal and navigate to frontend:
```bash
cd /Users/james/claude_development/kpath_enterprise/frontend-new
```

2. Install dependencies:
```bash
npm install
```

3. Create environment file:
```bash
cp .env.example .env
# Edit if backend is not on localhost:8000
```

4. Start the development server:
```bash
npm run dev
```

The frontend will be available at http://localhost:5173

## Default Credentials

For testing, you can create a user via the API or use these steps:

1. Access the backend API docs: http://localhost:8000/docs
2. Use the `/api/v1/auth/register` endpoint to create a user
3. Login with those credentials in the frontend

## Testing the System

1. Login to the frontend
2. Navigate to Services and create a test service
3. Go to Search and test the semantic search
4. Generate an API key in the API Keys section
5. Test the API key with curl:

```bash
curl -H "X-API-Key: your_key_here" \
  "http://localhost:8000/api/v1/search?query=test"
```

## Troubleshooting

- If the frontend can't reach the backend, check CORS settings
- Ensure PostgreSQL is running and accessible
- Check that all required Python packages are installed
- Verify the backend is running on port 8000
- Check browser console for any JavaScript errors
