FROM python:3.9
WORKDIR /app
#RUN pip install gunicorn==20.1.0
COPY package*.json ./
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
RUN npm ci
COPY . .
FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend.wsgi"]
