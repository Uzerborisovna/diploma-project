# Backend для автоматизации закупок в розничной сети

Дипломный проект по курсу «Python-разработчик».

## Описание
Сервис представляет собой REST API для автоматизации закупок. 
Реализован на Django + Django REST Framework.

## Функционал
- Модели: магазины, категории, товары, характеристики, заказы, контакты.
- Импорт товаров из YAML-файлов.
- API для просмотра товаров.
- Авторизация по токену (TokenAuthentication).
- Создание заказа с отправкой email клиенту и администратору (накладная).
- Регистрация и аутентификация пользователей.

## Установка и запуск

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/Uzerborisovna/diploma-project.git
   cd diploma-project

2.Создайте и активируйте виртуальное окружение:

bash
python3 -m venv venv
source venv/bin/activate

3.Установите зависимости:

bash
pip install django djangorestframework pyyaml requests

4.Примените миграции:

bash
python3 manage.py migrate

5.Импортируйте товары (пример в shop1.yaml):

bash
python3 scripts/import_products.py

6.Запустите сервер:

bash
python3 manage.py runserver 0.0.0.0:8000
API доступно по адресу: http://127.0.0.1:8000/api/

Основные эндпоинты
POST /api/register/ — регистрация.

POST /api/login/ — получение токена.

GET /api/products/ — список товаров.

GET /api/products/<id>/ — детали товара.

GET /api/categories/ — список категорий.

GET /api/shops/ — список магазинов.

GET /api/contacts/ — список контактов (только для авторизованных).

POST /api/contacts/ — создание контакта.

GET /api/orders/ — список заказов (только для авторизованных).

POST /api/orders/create/ — создание заказа.
