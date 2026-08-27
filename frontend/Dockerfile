# build env
FROM node:21.7.1-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --legacy-peer-deps
COPY . ./
RUN npm run build
FROM nginx:alpine
#CMD cp -r build result_build
COPY --from=builder /app/build /usr/share/nginx/html

#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend.wsgi"]
#CMD ["npx", "-y", "http-server", "-p", "8000", "/app/build"]