# build env
# FROM node:21.7.1-alpine
# WORKDIR /app
# COPY package*.json ./
# RUN npm install --legacy-peer-deps
# COPY . ./
# RUN npm run build
# FROM nginx:alpine
# CMD cp -r build result_build
# COPY --from=builder /app/build /usr/share/nginx/html

# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend.wsgi"]
# CMD ["npx", "-y", "http-server", "-p", "8000", "/app/build"]


FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --legacy-peer-deps
COPY . .
RUN npm run build
FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
RUN echo "server { \
    listen 80; \
    server_name localhost; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files \$uri \$uri/ /index.html; \
    } \
}" > /etc/nginx/conf.d/default.conf