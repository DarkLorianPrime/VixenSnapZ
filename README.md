# About
Сервис хранения фотографий в S3 хранилище min.io, с использованием postgresql и fastapi-framework.
### СОВЕТУЮ ИСПОЛЬЗОВАТЬ TMUX\SCREEN ДЛЯ ЗАПУСКА MINIO и FASTAPI параллельно. (Хотя если фастапи будет сокетом - не нужно.)
# Install
### Linux
Установка питона: `sudo apt-get install python3.10`

Установка питона: `sudo apt-get install python3-dev`

Установка nginx: `sudo apt install nginx`

Установка min.io:
```shell
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio
```
Установка postgresql: `sudo apt -y install postgresql`

Установка этого проекта: `git clone https://github.com/DarkLorianPrime/greenatom_testcase/tree/main.git`


Общая настройка установленных модулей НЕ ПРИЛАГАЕТСЯ. Гугл и бог вам в помощь.

# Run project
```bash
cd greenatom_testcase
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd libraries
mv example.env .env
nano .env
```
Заполните все поля .env в соответствии со своими данными.
```dotenv
SHATOKEN= - ключ шифрования пароля (можно сделать через uuid.uuid4().hex)
user= - пользователь базы данных
DB= - название базы данных
password= - пароль базы данных
host= - хост базы данных (айпи\ссылка куда обращаться за данными)
minio_url= - хост MINIO
minio_login= - логин MINIO
minio_password= - пароль MINIO
```

Протестируйте наличие всех модулей DEV запуском фастапи (!НИКОГДА НЕ ИСПОЛЬЗУЙТЕ ЭТОТ ВИД ЗАПУСКА В ПРОДАКШЕНЕ!)

`uvicorn main:app —host="0.0.0.0" —port="need port"` (Возможно потребуется установка uvicorn)

При тестовом запросе на `/api/login` должен быть вывод

`INFO: TEST-IP - "POST /api/login/ HTTP/1.0" 422 Unprocessable Entity` - в консоль

```json
{
  "detail": [
    {
      "loc": [
        "body",
        "username"
      ],
      "msg": "field required",
      "type": "value_error.missing"
    },
    {
      "loc": [
        "body",
        "password"
      ],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```
- в ответ на запрос

# Установка на продакшен

Этот пункт не значит, что этот сайт можно выпускать на многомиллиардную аудиторию. Просто сайт будет работать в режиме, когда можно не столь сильно бояться за взлеты и падения. Для установки на продакшен нам понадобиться:

- Настроить MIN.IO
- Настроить Nginx
- Кинуть сокет Nginx-python

## Настройка MIN.IO
Переходим в папку с Min.io

Пишем команду: ./minio server data —console-address "need-server-url:need-server-port"

Есть возможность установить SSL HTTPS сертификаты, но я этим не занимался.

MINIO настроен. Теперь вам нужно посмотреть что вам выводит при запуске этой команды и скопировать API IP:PORT and login\password
![image](https://user-images.githubusercontent.com/66025673/173196717-a161dadc-6829-4906-ab47-abee37cc342c.png)
и добавить в ваш .env

## NGINX и GUNICORN
Перед выполнением действий из этого пункта - убедитесь что ваш .env полностью заполнен и ВСЕ методы отлично работают. Если что-то не работает - киньте пулл-реквест на фикс 👉🏻👈🏻

`nano /etc/systemd/system/pictures.service`

Вместо `/root/testgreen/` - ваш путь.

```service
[Unit]
Description=Gunicorn Daemons
Requires=pictures.socket
After=network.target

[Service]
User=root
WorkingDirectory=/root/testgreen/greenatom_testcase
ExecStart=/root/testgreen/greenatom_testcase/venv/bin/gunicorn -k uvicorn.workers.UvicornWorker —bind unix:/run/pictures.sock main:app

[Install]
WantedBy=multi-user.target
```

`nano /etc/systemd/system/pictures.socket`

```service
[Unit]
Description=Pictures-service

[Socket]
ListenStream=/run/pictures.sock

[Install]
WantedBy=sockets.target
```

`
sudo systemctl start pictures
sudo systemctl enable pictures
`

`nano /etc/nginx/sites-available/pictures-service.conf`

```nginx
server {
    proxy_read_timeout 5m;
    listen 80;
    server_name pictures.your-domen.hehe;
    location / {
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass http://unix:/run/pictures.sock;
    }
}
```
```shell
cd ../
ln -sf /etc/nginx/sites-available/pictures-service.conf /etc/nginx/sites-enabled/
ln -sf
/etc/nginx/sites-available/pictures-service.conf /etc/nginx/conf.d/
sudo systemctl restart nginx
```
## Поздравляю с первым задеплоеным проектом!

# Urls
Format: URL | METHOD\`S | NEED PARAMS | FORMDATA | HEADERS | NEED_AUTH

`/api/registration` | ["POST"] | [NOTHING] | username STRING, password STRING | [Authorization] | False

`/api/authorization` | ["POST"] | [NOTHING] | username STRING, password STRING | [Authorization] | False

`/api/checkauth` | ["GET"] | [NOTHING] | [NOTHING] | [Authorization] | T\F

`/api/frames` | ["GET", "POST"] | [NOTHING] | FOR POST: files FILES LIST | [Authorization] | True

`/api/frames`{frame_uuid} / ["GET", "DELETE"] | IN URL: frame_uuid STRING | [NOTHING] | [Authorization] | True

# Versions

[Python]
3.10

[MIN.IO]
RELEASE.2022-06-10T16-59-15Z

[Postgresql]
12.11

[Nginx]
1.18.0

[Gunicorn]
20.0.4
