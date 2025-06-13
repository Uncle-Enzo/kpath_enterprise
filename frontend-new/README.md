# KPath Enterprise Frontend

This is the frontend application for KPath Enterprise, built with SvelteKit and Tailwind CSS.

## Features

- **Authentication**: JWT-based authentication with secure token storage
- **Service Management**: Full CRUD operations for services
- **Search Testing**: Interactive interface to test semantic search
- **API Key Management**: Generate and manage API keys
- **User Management**: Admin interface for user management
- **Dashboard**: Overview of system metrics and status

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Environment Variables

Create a `.env` file in the root directory:

```env
PUBLIC_API_URL=http://localhost:8000
```

## Project Structure

```
src/
├── routes/          # SvelteKit routes
├── lib/
│   ├── api/        # API client modules
│   ├── components/ # Reusable Svelte components
│   ├── stores/     # Svelte stores for state management
│   └── types/      # TypeScript type definitions
├── app.html        # HTML template
└── app.css         # Global styles with Tailwind
```

## Authentication

The app uses JWT tokens for authentication:

1. Tokens are stored in localStorage
2. The API client automatically includes the token in requests
3. Unauthorized requests redirect to login
4. Token refresh is handled automatically

## API Integration

All API calls go through the centralized client in `src/lib/api/client.ts`:

- Automatic token injection
- Error handling
- Request/response interceptors
- Type-safe API methods

## Styling

The app uses Tailwind CSS with custom components:

- `.btn` - Button styles
- `.card` - Card container
- `.input` - Form input styles

## Routes

- `/` - Dashboard
- `/login` - Authentication
- `/services` - Service management
- `/search` - Search testing
- `/api-keys` - API key management
- `/users` - User management (admin only)
