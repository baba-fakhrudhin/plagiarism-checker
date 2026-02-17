# ============================================
# Multi-stage build for React frontend
# ============================================

# Stage 1: Build React app
FROM node:18-alpine as builder

WORKDIR /app

# Set build arguments
ARG REACT_APP_API_URL=http://localhost:5000/api

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build React app
RUN npm run build

# ============================================
# Stage 2: Serve with Nginx
FROM nginx:alpine

# Install curl for health checks
RUN apk add --no-cache curl

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built app from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Create directory for uploads
RUN mkdir -p /usr/share/nginx/html/uploads

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Add a simple health endpoint
RUN echo "OK" > /usr/share/nginx/html/health

# Start nginx in foreground
CMD ["nginx", "-g", "daemon off;"]