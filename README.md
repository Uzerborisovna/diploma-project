Backend для автоматизации закупок в розничной сети

Дипломный проект по курсу «Python-разработчик».

Описание
Сервис представляет собой REST API для автоматизации закупок. 
Реализован на Django + Django REST Framework.

Функционал
- Модели: магазины, категории, товары, характеристики, заказы, контакты.
- Импорт товаров из YAML-файлов.
- API для просмотра товаров.
- Авторизация по токену (TokenAuthentication).
- Создание заказа с отправкой email клиенту и администратору (накладная).
- Регистрация и аутентификация пользователей.
- Подтверждение email при регистрации.
- Сброс пароля.
- Редактирование статуса заказа.

Установка и запуск

1. Клонируйте репозиторий:
git clone https://github.com/Uzerborisovna/diploma-project.git
cd diploma-project

2. Создайте и активируйте виртуальное окружение:
python3 -m venv venv
source venv/bin/activate

3. Установите зависимости:
pip install -r requirements.txt

4. Создайте файл .env (пример в .env.example):
cp .env.example .env
и укажите в нём свой SECRET_KEY.

5. Примените миграции:
python3 manage.py migrate

6. Импортируйте товары (пример в shop1.yaml):
python3 scripts/import_products.py

7. Запустите сервер:
python3 manage.py runserver 0.0.0.0:8000

8. API доступно по адресу: http://127.0.0.1:8000/api/

Важно
- Email: В настройках используется EMAIL_BACKEND = console. Это значит, что все письма (подтверждение регистрации, сброс пароля, уведомления о заказе) выводятся в консоль, а не отправляются на реальный email. Для проверки сценария с email смотрите вывод в терминале (там будут токены и текст писем).
- DEBUG: Для разработки оставлен DEBUG = True. В продакшене его нужно отключить.
- ALLOWED_HOSTS: Для разработки разрешены все хосты (['*']). В продакшене нужно указать конкретные домены.

Основные эндпоинты
- POST /api/register/ — регистрация.
- POST /api/register/confirm/ — подтверждение email.
- POST /api/login/ — получение токена.
- POST /api/password_reset/ — запрос на сброс пароля.
- POST /api/password_reset/confirm/ — подтверждение сброса пароля.
- GET /api/products/ — список товаров.
- GET /api/products/<id>/ — детали товара.
- GET /api/categories/ — список категорий.
- GET /api/shops/ — список магазинов.
- GET /api/contacts/ — список контактов (только для авторизованных).
- POST /api/contacts/ — создание контакта.
- GET /api/cart/ — просмотр корзины.
- POST /api/cart/ — добавление товара в корзину.
- DELETE /api/cart/<item_id>/ — удаление товара из корзины.
- GET /api/orders/ — список заказов (только для авторизованных).
- POST /api/orders/create/ — создание заказа.
- PATCH /api/orders/<id>/status/ — изменение статуса заказа.