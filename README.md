# World of food
![Foodgram workflow](https://github.com/semenvanyushin/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg?event=push)
![Python](https://img.shields.io/badge/Python-3.10.9-green)
![Django](https://img.shields.io/badge/Django-4.1.6-blue)
![Django REST framework](https://img.shields.io/badge/Django%20REST%20framework-3.14.0-blue)
![Djoser](https://img.shields.io/badge/Djoser-2.1.0-blue)
![Gunicorn](https://img.shields.io/badge/Gunicorn-20.1.0-br)
![PostgreSQL](https://img.shields.io/badge/PosrgreSQL-14.6-blue)
![NGINX](https://img.shields.io/badge/NGINX-1.21.3-brightgreen)
![Docker](https://img.shields.io/badge/Docker-20.10.22-blue)


## Описание проекта:
World of food - вебсайт, который дает возможность публиковать свои и добавлять в избранные рецепты других авторов, подписываться на пользователей. Для приготовления избранных блюд доступен для загрузки список покупки ингредиентов в виде файла в формате .pdf.

## Запуск с использованием CI CD

### Установка Docker и Docker-compose на сервер ВМ:

```bash
ssh username@ip # username - имя вашего пользователя на сервере, ip - адрес вашего сервера
```
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install curl -y
```
```bash
sudo curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo rm get-docker.sh
```
```bash
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Копирование docker-compose.yml и default.conf на сервер ВМ:

Подготовка директории на сервере:
```bash
cd ~
```
```bash
mkdir infra
```
```bash
cd infra
```

Копирование с локального компьютера:
```bash
scp docker-compose.yml username@ip:/home/username/infra/ # username - имя вашего пользователя на сервере, ip - адрес вашего сервера
```
```bash
scp default.conf username@ip:/home/username/infra/ # username - имя вашего пользователя на сервере, ip - адрес вашего сервера
```

Заполните Secrets в GitHub Actions:
```bash
DB_ENGINE = django.db.backends.postgresql
DB_NAME = postgres
POSTGRES_USER = postgres # логин для подключения к базе данных
POSTGRES_PASSWORD = postgres # пароль для подключения к базе данных (установите свой)
DB_HOST = db
DB_PORT = 5432
HOST # ip сервера
USER  # имя вашего пользователя на сервере
SSH_KEY # приватный ключ доступа для подключению к серверу `cat ~/.ssh/id_rsa`
PASSPHRASE # серкретный ключ\фраза, если ваш ssh-ключ защищён фразой-паролем
TELEGRAM_TO # id пользователя. Ему бот будет отправлять результат успешного выполнения
TELEGRAM_TOKEN # токен бота телеграм, от имени которого будет приходить сообщение
DOCKER_USERNAME # Имя пользователя Docker для выгрузки образа в DockerHub
DOCKER_PASSWORD # Пароль пользоывателя Docker
SECRET_KEY # Ваш SECRET_KEY из settings.py
```

### Запуск с использованием Docker:

```bash
cd ~/infra
```
Создание и запуск контейнеров:
```bash
sudo docker-compose up -d
```
Выполнение миграций:
```bash
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate --noinput
```
Создание суперпользователя:
```bash
docker-compose exec backend python manage.py createsuperuser
```
Подключение статики:
```bash
docker-compose exec backend python manage.py collectstatic --no-input
```
Заполнение базы данных тегами и ингредиентами(по желанию):
```bash
docker-compose exec backend python manage.py load_tags
docker-compose exec backend python manage.py load_ingredients
```

### Запуск в режиме разработчика:

Создание и активация виртуального окружения:
```bash
python3 -m venv venv # MacOS и Linux
python -m venv venv # Windows
```
```bash
source /venv/bin/activated # MacOS и Linux
source venv\Scripts\activate # Windows
```
Установка зависимостей из файла requirements.txt:
```bash
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```
Выполнение миграций(выполняется из директории с файлом manage.py):
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```
Запуск сервера(выполняется из директории с файлом manage.py):
```bash
python3 manage.py runserver
```

## Проект доступен по адресам:

```bash
http://youhost/admin # администрирование сайта
http://youhost/recipes # стартовая страница сайта
```

## Документация к API доступна после запуска проекта по адресу:

http://127.0.0.1/api/docs/


Автор: [Семен Ванюшин](https://github.com/semenvanyushin)
