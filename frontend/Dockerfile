# Frontend Dockerfile for Local Task Manager (React + Vite)
FROM node:20-alpine AS builder

# Set environment variables
ENV NODE_ENV=production

# Create working directory
WORKDIR /app

# Install all dependencies (including dev for build)
COPY package*.json ./
RUN npm install --include=dev && npm cache clean --force

# Copy source
COPY . .

# Build for production
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1

# Use entrypoint script for environment variable substitution
ENTRYPOINT ["/entrypoint.sh"]

# Run nginx
CMD ["nginx", "-g", "daemon off;"]
