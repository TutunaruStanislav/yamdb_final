# yamdb_final

![Build Status](https://github.com/TutunaruStanislav/yamdb_final/workflows/Building/badge.svg)](https://github.com/TutunaruStanislav/yamdb_final/actions/workflows/yamdb_workflow.yml)

### Описание:
Api для проекта YaMDb, который собирает отзывы пользователей на произведения.

Проект позволяет выполнять следующие операции:
* Регистрация нового пользователя/получение JWT токена
* Получение списка всех пользователей
* Добавление пользователя
* Получение/изменение/удаление пользователя по username
* Получение/изменение своей учетной записи
* Получение списка всех отзывов
* Добавление нового отзыва
* Получение/редактирование/удаление отзыва
* Получение списка всех комментариев к отзыву
* Добавление комментария к отзыву
* Получение/редактирование/удаление комментария
* Получение списка всех категорий
* Добавление новой категории
* Удаление категории
* Получение списка всех жанров
* Добавление нового жанра
* Удаление категории
* Получение списка всех произведений
* Добавление произведения
* Получение/обновление/удаление произведения

### Стек технологий:
Python 3.7

Django 2.2.16

Postgres 13.0
### Как собрать и запустить проект:

Клонировать репозиторий:

```
git clone https://github.com/TutunaruStanislav/yamdb_final.git
```

Скопировать .env.example в .env и заполнить его:

```
cp .env.example ./infra/.env
```

Перейти в папку infra, собрать и запустить контейнеры:

```
cd infra
```

```
docker-compose up -d --build
```
Выполнить команды инициализации и применить миграции:

```
docker-compose exec web python manage.py migrate
```

```
docker-compose exec web python manage.py createsuperuser
```

```
docker-compose exec web python manage.py collectstatic --no-input
```

```
docker-compose exec web python manage.py loaddata fixtures.json
```

Проект будет доступен по следующему адресу:

http://localhost/

### Запросы / ответы:

* http://localhost/admin - панель администратора
* GET http://localhost/api/v1/categories/ - список всех категорий
```
HTTP Statuses: 200
```
```json lines
Response body
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "name": "test1",
            "slug": "test-1"
        }
    ]
}
```

* POST http://localhost/api/v1/categories/ - добавить категорию

```json lines
Authorization jwt
Request Body
{
    "name": "Категория новая",
    "slug": "category-new"
}
```
```
HTTP Statuses: 201, 400, 401, 403
```

* GET http://localhost/api/v1/genres/ - список всех жанров

```
HTTP Statuses: 200
```
```json lines
Response body
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "name": "genre1",
            "slug": "genre-1"
        }
    ]
}
```

* GET http://localhost/api/v1/titles/{titles_id}/ - получение информации о произведении

```
Path parameters:
titles_id: 1 (integer)
```
```
HTTP Statuses: 200, 404
```
```json lines
Response body
{
    "id": 1,
    "name": "title1",
    "year": 1999,
    "category": {
        "name": "test1",
        "slug": "test-1"
    },
    "genre": [
        {
            "name": "genre1",
            "slug": "genre-1"
        }
    ],
    "description": "title1 description",
    "rating": null
}
```

Более полная документация с описанием доступных запросов, ответов и статусов, расположена по адресу - http://localhost/api/redoc/

### Авторы:
Stanislav Tutunaru

### Лицензия:

MIT