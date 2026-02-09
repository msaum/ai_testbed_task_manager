# Local Task Manager - Frontend

A React + TypeScript + Vite frontend application for the Local Task Manager.

---

## Features

- Modern React 19 with TypeScript
- Component-based architecture
- Responsive design with CSS
- API integration with FastAPI backend
- Task filtering and sorting
- Light/Dark theme support

---

## Project Structure

```
frontend/
├── src/
│   ├── components/       # Reusable UI components
│   ├── pages/            # Page components
│   ├── layout/           # Layout components (Header, Sidebar, etc.)
│   ├── types/            # TypeScript type definitions
│   ├── hooks/            # Custom React hooks
│   ├── constants/        # Application constants
│   ├── utils/            # Utility functions
│   ├── App.tsx           # Main application component
│   ├── main.tsx          # Application entry point
│   └── index.css         # Global styles
├── public/               # Static assets
├── dist/                 # Build output (generated)
├── Dockerfile            # Docker configuration
├── nginx.conf            # Nginx configuration for production
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

---

## Getting Started

### Prerequisites

- Node.js 18 or later
- npm or pnpm

### Development Setup

1. **Install dependencies:**

```bash
npm install
# or
pnpm install
```

2. **Start the development server:**

```bash
npm run dev
# or
pnpm dev
```

The frontend will be available at http://localhost:5173

3. **Build for production:**

```bash
npm run build
# or
pnpm build
```

4. **Preview the production build:**

```bash
npm run preview
# or
pnpm preview
```

---

## Available Scripts

| Script         | Description                            |
| -------------- | -------------------------------------- |
| `dev`          | Start Vite development server with HMR |
| `build`        | Build the application for production   |
| `preview`      | Preview the production build locally   |
| `lint`         | Run ESLint                             |
| `lint:fix`     | Run ESLint with auto-fix               |
| `format`       | Format code with Prettier              |
| `format:check` | Check code formatting with Prettier    |

---

## Development

### TypeScript Configuration

The project uses TypeScript with strict mode enabled. See `tsconfig.json` for configuration details.

### Vite Configuration

Vite is configured in `vite.config.ts`. Key settings:

- React plugin for Fast Refresh
- TypeScript support
- Environment variable support

### API Integration

The frontend connects to the backend API at `/api/v1`. The API URL can be configured via environment variables:

```bash
# Create .env.local file
API_URL=http://localhost:8000/api/v1
```

---

## Docker

### Build the Docker image

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose Integration

```yaml
frontend:
  build: ./frontend
  container_name: taskmgr-frontend
  ports:
    - '5173:80'
  environment:
    - API_URL=http://localhost:8000/api/v1
```

---

## Styling

The project uses plain CSS with CSS modules where appropriate. Key styling files:

- `src/index.css` - Global styles and CSS variables
- `src/App.css` - Application-level styles
- Component-specific styles in respective component directories

---

## Testing

Currently using ESLint for code quality. Unit tests can be added with Vitest:

```bash
npm test
```

---

## Troubleshooting

### Port already in use

If port 5173 is already in use:

```bash
# Change the port in vite.config.ts
# Or kill the process using the port
lsof -i :5173
kill -9 <PID>
```

### Build errors

Clear the build cache:

```bash
rm -rf node_modules dist
npm install
npm run build
```

---

## License

This project is provided as-is for educational and testing purposes.
