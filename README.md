# Photo Saving service "VixenSnapZ"
# About
Сервис хранения фотографий в S3 хранилище `min.io`, с использованием `postgresql` и `FastAPI`.
# Built with
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)

![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
# RoadMap
- [x] Начать проект
- [x] Интегрировать Min.IO
- [x] Развернуть docker compose
- [x] Написать Frames-методы
- [x] Добавить авторизацию и доступы
- [x] Оптимизировать код
- [x] Написать документацию
- [x] Написать unittests
# Excamples
В этом разделе мы рассмотрим несколько основных примеров использования API, созданного с использованием FastAPI в рамках этого проекта.
### Регистрация пользователя
POST /api/v1/registration/
BODY
```json
{
  "username": "darklorian",
  "password": "54zJDn9gH"
}
```
В случае успеха, ответ будет:

HTTP/1.1 201 Created
```json
{
  "id": "5f77ac60-0e7b-42ba-bbaf-73739d1fec9a",
  "username": "darklorian"
}
```
### Авторизация пользователя 
POST /api/v1/login/
BODY
```json
{
  "username": "darklorian",
  "password": "54zJDn9gH"
}
```
В случае успеха, ответ будет:

HTTP/1.1 200 OK
```json
{
  "access_token": "5f77ac60-0e7b-42ba-bbaf-73739d1fec9a"
}
```
### Отправка файлов 
POST /api/v1/frames/

authorization `Bearer 5f77ac60-0e7b-42ba-bbaf-73739d1fec9a`

files
```python
files=[('files', "1.png"),('files', "2.png"),('files', "3.png"),]
```
В случае успеха, ответ будет:

HTTP/1.1 201 Created
```json
[
    {
        "server_name": "3aefff9b-18a9-444f-80e4-e9b787ae1aa5",
        "filename": "1.jpg"
    },
      {
        "server_name": "3aefff9b-18a9-555f-80e4-e9b787ae1aa5",
        "filename": "2.jpg"
    },
      {
        "server_name": "4ae9239b-18a9-444f-80d4-e9b787ee1aa6",
        "filename": "3.jpg"
    }
]
```

### Получение всех файлов 
GET /api/v1/frames/

authorization `Bearer 5f77ac60-0e7b-42ba-bbaf-73739d1fec9a`

В случае успеха, ответ будет:

HTTP/1.1 200 OK
```json
[
    {
        "uploaded": "20.05.2023 21:15:56",
        "uuid": "3aefff9b-18a9-444f-80e4-e9b787ae1aa5",
        "filename": "1.jpg"
    },
      {
        "uploaded": "20.05.2023 21:15:56",
        "uuid": "3aefff9b-18a9-555f-80e4-e9b787ae1aa5",
        "filename": "2.jpg"
    },
      {
        "uploaded": "20.05.2023 21:15:56",
        "uuid": "4ae9239b-18a9-444f-80d4-e9b787ee1aa6",
        "filename": "3.jpg"
    }
]
```

### Получение одного файла 
GET /api/v1/frames/3aefff9b-18a9-444f-80e4-e9b787ae1aa5/

authorization `Bearer 5f77ac60-0e7b-42ba-bbaf-73739d1fec9a`

В случае успеха, ответ будет:

HTTP/1.1 200 OK
```json
{
    "uploaded": "20.05.2023 21:32:57",
    "filename": "1.jpg",
    "uuid": "fcb30112-19a9-4bea-87c3-8cbfee9c11f4"
}
```

### Удаление файла
DELETE /api/v1/frames/3aefff9b-18a9-444f-80e4-e9b787ae1aa5/

authorization `Bearer 5f77ac60-0e7b-42ba-bbaf-73739d1fec9a`

В случае успеха, ответ будет:

HTTP/1.1 204 NO CONTENT

# Install
### Linux
Клонируем репозиторий:
```bash
$ git clone https://github.com/DarkLorianPrime/VixenSnapZ
$ cd VixenSnapZ
$ tree 
.
├── backend
│   ├── app
│   │   ├── libraries
│   │   │   ├── authenticator.py
│   │   │   ├── database.py
│   │   │   ├── depends.py
│   │   │   └── s3_handler.py
│   │   ├── main.py
│   │   └── routers
│   │       ├── authorization
│   │       │   ├── authorization.py
│   │       │   ├── models.py
│   │       │   ├── pydantic_models.py
│   │       │   ├── responses.py
│   │       │   ├── service.py
│   │       │   └── validators.py
│   │       └── frames
│   │           ├── frames.py
│   │           ├── models.py
│   │           ├── pydantic_models.py
│   │           ├── responses.py
│   │           └── service.py
│   ├── Dockerfile
│   └── tests
│       └── photos
│           ├── 2.jpg
│           ├── 4_2.jpg
│           ├── 6.jpg
│           ├── â\200\224Pngtreeâ\200\22480 s seamless pattern background_1158091.png
│           ├── ficus.png
│           ├── galina-n-miziNqvJx5M-unsplash 1.png
│           ├── Mask Group.png
│           └── WzhUKeyhtpg.jpg
├── docker-compose.yml
└── README.md
```
- Устанавливаем ENV
```bash
mv .example.env .env
nano .env

--.env--
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=
POSTGRES_NAME=

MINIO_USER=
MINIO_PASSWORD=

ACCESS_KEY= # КЛЮЧ ДЛЯ ШИФРОВАНИЯ
--------
```
- Запускаем docker-compose
```bash
$ docker-compose up -d --build
```
Вы должны увидеть надписи
```
Creating vixensnapz_database_1 ... done
Creating vixensnapz_minio_1    ... done
Creating vixensnapz_backend_1  ... done
```

Сервис запущен и готов к работе. Можно подключать к nginx и зарабатывать миллионы лисобаксов.

# Contacts
Grand developer - [@darklorianprime](https://vk.com/darklorianprime) - kasimov.alexander.ul@gmail.com