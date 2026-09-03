**Foodgram** — это онлайн‑платформа для публикации и поиска рецептов.
Пользователи могут:

* регистрироваться и авторизоваться;
* добавлять рецепты с ингредиентами и инструкциями;
* просматривать и фильтровать рецепты по тегам;
* сохранять понравившиеся рецепты в избранное;
* отправить ссылку на рецепт другу;
* получить список необходимых покупок для реализации рецепта.

## Ссылки на проект

* [Сайт](https://food.jo3.org/)
* [Админка](https://food.jo3.org/admin/)
* [Дока к API сервера](https://food.jo3.org/api/docs/)

## Исходный код

GitHub: [123vovantus-cpu/foodgram](https://github.com/123vovantus-cpu/foodgram.git)

## Архитектура

* **Backend** — Django + DRF (REST API)
* **Frontend** — React (production build)
* **База данных** — PostgreSQL
* **Хранение медиа** — Docker volumes
* **Веб‑сервер** — Nginx
* **CI/CD** — GitHub Actions, деплой по SSH

---

## Содержимое .env-файла для запуска

```env
SECRET_KEY=django-insecure-e-ozv70#2=cpq8(*b+qfzmf3x2f2cwlev*0l0&!_ee=m&c!e74
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,158.160.165.233,food.jo3.org,backend
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=mypassword
DB_HOST=db
DB_PORT=5432
Файл .env нужно создать в папке infra/ рядом с docker-compose.yml.

Запуск на сервере с Docker-контейнерами (CI/CD)
Для запуска этого процесса нужно руками сделать следующее
создать репозиторий на GitHub и аккаунт на DockerHub
получить сервер, на котором будет размещён сайт
Добавить на GitHub Repository secrets
Settings → Secrets and variables → Actions:

DOCKER_PASSWORD — пароль на DockerHub
DOCKER_USERNAME — логин на DockerHub
HOST_IP — IP-адрес вашего сервера
HOST_SSH_KEY — закрытый ключ для подключения к серверу
HOST_USER — логин на сервере
TELEGRAM_TO — строка вида 123456789
TELEGRAM_TOKEN — строка вида 7814787497:****...****gk
Поместить на сервер файлы из папки server
Подключение к серверу по SSH (образец):

bash
ssh -i "C:/Users/Bigben/.ssh/user_key" ubuntu@158.160.165.233
Файл default поместить в папку /etc/nginx.

Запуск проекта на сервере
bash
cd ~/foodgram/
В этой папке должны лежать:

.env (пример выше)
ingredients.json (из папки foodgram/data)
Поднимаем контейнеры:

bash
sudo docker compose -f docker-compose.production.yml up -d
Заходим в контейнер backend:

bash
sudo docker exec -f docker-compose.production.yml -it foodgram-backend-1 bash
Выполняем миграции:

bash
python manage.py migrate
Собираем статику:

bash
python manage.py collectstatic --noinput
Создаём администратора:

bash
python manage.py createsuperuser
Копируем файл с данными внутрь контейнера (с хоста):

bash
sudo docker cp ingredients.json foodgram-backend-1:/app/
Запускаем импорт данных:

bash
python manage.py load_ingredients_json ingredients.json
Переходим по ссылке
Локальный запуск Backend + Frontend
Backend
Клонировать репозиторий:

bash
git clone git@github.com:123vovantus-cpu/foodgram.git
cd foodgram/backend
Создать и активировать виртуальное окружение:

bash
# Ubuntu
python3 -m venv env
source env/bin/activate

# Windows
py -3.9 -m venv env
source ./env/Scripts/activate
Обновить pip и установить зависимости:

bash
python -m pip install --upgrade pip
pip install -r requirements.txt
Создать файл .env в папке foodgram/:

env
# Локальный вариант (без Docker, SQLite)
SECRET_KEY=django-insecure-e-ozv70#2=cpq8(*b+qfzmf3x2f2cwlev*0l0&!_ee=m&c!e74
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
Выполнить миграции:

bash
python manage.py migrate
Заполнить справочники:

bash
python manage.py load_ingredients_json ../data/ingredients.json
Создать администратора:

bash
python manage.py createsuperuser
Запустить сервер:

bash
python manage.py runserver
Админка доступна по адресу: 

Остановить сервер — Ctrl+C.

Запуск Frontend (вариант 1 — без Docker)
Нужно одновременно запустить фронтенд и бэкенд. Открой папку /frontend/ в отдельном терминале и выполни:

bash
npm install --legacy-peer-deps
npm start
Фронтенд откроется по адресу 

Запуск Frontend (вариант 2 — через Docker)
Находясь в папке infra, выполни:

bash
sudo docker compose up
Контейнер frontend подготовит файлы, необходимые для работы фронтенд‑приложения, а затем прекратит свою работу.

Фронтенд:  Спецификация API: 

Примеры запросов к API
Создание рецепта
POST /api/recipes/

Тело запроса:

json
{
  "ingredients": [
    {"id": 1, "amount": 200},
    {"id": 2, "amount": 3}
  ],
  "tags": [1, 2],
  "image": "data:image/png;base64,iVBORw0KGgo...",
  "name": "Борщ",
  "text": "Классический рецепт борща",
  "cooking_time": 60
}
Ответ (201):

json
{
  "id": 1,
  "name": "Борщ",
  "image": "https://food.jo3.org/media/recipes/recipe_1.png",
  "cooking_time": 60,
  "author": {
    "email": "user@example.com",
    "username": "chef",
    "first_name": "Иван",
    "last_name": "Поваров",
    "is_subscribed": false,
    "avatar": null
  },
  "ingredients": [
    {"id": 1, "name": "Свёкла", "measurement_unit": "г", "amount": 200},
    {"id": 2, "name": "Лук", "measurement_unit": "шт", "amount": 3}
  ],
  "is_favorited": false,
  "is_in_shopping_cart": false
}
Добавление в избранное
POST /api/recipes/{id}/favorite/

Ответ (201):

json
{
  "id": 1,
  "name": "Борщ",
  "image": "https://food.jo3.org/media/recipes/recipe_1.png",
  "cooking_time": 60
}
Скачивание списка покупок
GET /api/recipes/download_shopping_cart/

Ответ (200): текстовый файл shopping_list.txt:

text
Список покупок
Дата: 03.09.2026
Пользователь: chef

Свёкла (г) — 400
Лук (шт) — 6