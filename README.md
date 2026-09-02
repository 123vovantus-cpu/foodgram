Foodgram
Онлайн‑платформа для публикации и поиска рецептов. Пользователи могут регистрироваться, добавлять рецепты, фильтровать по тегам, добавлять в избранное и формировать список покупок.

1. Подготовка сервера
bash
# подключение по SSH
ssh -i ~/.ssh/your_key user@server_ip
Поместите файл default.conf в /etc/nginx/sites-enabled/, файл .env — в ~/foodgram/, а также скопируйте данные для загрузки:

bash
scp -i ~/.ssh/your_key ./data/ingredients.json user@server_ip:~/foodgram/
scp -i ~/.ssh/your_key ./data/tags.json user@server_ip:~/foodgram/
Пример .env:

env
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=ваш_пароль
POSTGRES_DB=foodgram
DB_HOST=db
DB_PORT=5432
SECRET_KEY=ваш_секретный_ключ
DEBUG=False
ALLOWED_HOSTS=food.jo3.org,127.0.0.1,localhost

2. Запуск контейнеров
bash
cd ~/foodgram
docker compose -f docker-compose.production.yml up -d

3. Инициализация проекта
bash
# миграции и суперпользователь
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser


4. GitHub Actions (CI/CD)
В Settings → Secrets and variables → Actions добавьте:

DOCKER_PASSWORD, DOCKER_USERNAME — доступ к Docker Hub
HOST_IP, HOST_USER, HOST_SSH_KEY, SSH_PASSPHRASE — доступ к серверу
TELEGRAM_TO, TELEGRAM_TOKEN — уведомления о деплое
Локальный запуск
Backend
bash
git clone git@github.com:Dumskii-Artem/foodgram.git
cd foodgram/backend

python -m venv env
source env/bin/activate          # Windows: ./env/Scripts/activate

pip install --upgrade pip
pip install -r requirements.txt
Создайте .env в папке проекта:

env
POSTGRES_USER=none
POSTGRES_PASSWORD=none
POSTGRES_DB=none
DB_HOST=
DB_PORT=5432
SECRET_KEY=django-insecure-ваш_ключ
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
USE_SQLITE=True


bash
python manage.py migrate
python manage.py load_ingredients_json ../data/ingredients.json
python manage.py load_tags_json ../data/tags.json
python manage.py createsuperuser
python manage.py runserver
Админка: http://127.0.0.1:8000/admin/

Frontend
bash
cd foodgram/frontend
npm install --legacy-peer-deps
npm start
Фронтенд доступен на http://localhost:3000.

Локальный запуск через Docker
bash
cd foodgram/infra
docker compose up
Сайт: http://localhost, документация API: http://localhost/api/docs/.

