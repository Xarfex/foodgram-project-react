# Foodgram
![Xarfex](https://github.com/Xarfex/foodgram-project-react/actions/workflows/main.yml/badge.svg)

## Адрес
```https://valeryanichx.hopto.org```
```Superuser: login: testuser@mail.ru password: testpass```

## Что это такое
- Данный проект - это возможность посмотреть на всякую вкуснятину
- Можно делиться своими или семейными рецептами
- Рассказать про особенности и собрать нужное количество ингредиентов
- Так же можете скачать файл с заранее подготовленным списком покупок, необходимые товары будут добавлены в удобный список

## Инструментарий
- *Языки*: Python, HTML, CSS, JavaScript, Django, React, YAML-словарь
- *Сервисы*: Nginx, Workflow, GitHub Actions(CI/CD), Docker

## Как развернуть проект
В этом проекте мы используем методику CI/CD, так что файл workflow триггерит на "push" в любую ветку репозитория и разворачивает проект на сервере.
Но если мы говорим про локальную разработку:
- Установим Docker(Linux):
`sudo apt update`
`sudo apt install curl`
Скрипт для установки Docker
`curl -fSL https://get.docker.com -o get-docker.sh`
Запуск скрипта `sudo sh ./get-docker.sh`
Дополнительно к Docker установите утилиту Docker Compose: `sudo apt-get install docker-compose-plugin`

- Качаем образы с Docker Hub:
Добавим в корневую директорию проекта файл .env(необходимые параметры указаны ниже)
Образ PostgreSQL `docker run --name db \
                --env-file .env \
                -v pg_data:/var/lib/postgresql/data \
                postgres:13.10`
Изменить файл settings.py, чтобы он использовал переменные окружения:
```
# Добавьте import
import os

...
# Этими строчками замените текущую настройку DATABASES
DATABASES = {
    'default': {
        # Меняем настройку Django: теперь для работы будет использоваться
        # бэкенд postgresql
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'django'),
        'USER': os.getenv('POSTGRES_USER', 'django'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', ''),
        'PORT': os.getenv('DB_PORT', 5432)
    }
}
...
```
Собираем образы: 
```
cd foodgram_frontend  # В директории frontend...
docker build -t username/foodgram_frontend .  # ...сбилдить образ, назвать его taski_frontend
cd ../foodgram_backend  # То же в директории backend...
docker build -t username/foodgram_backend .
cd ../foodgram_gateway  # ...то же и в gateway
docker build -t username/foodgram_gateway .
```
Делаем локальный файл docker-compose.yml:
```
version: '3'

volumes:
  pg_data:

services:
  db:
    image: postgres:13.10
    env_file: .env
    volumes:
      - pg_data:/var/lib/postgresql/data
  backend:
    build: ./foodgram_backend/
    env_file: .env
  frontend:
    env_file: .env
    build: ./foodgram_frontend/
# Добавляем новый контейнер: gateway.
  gateway:
    # Сбилдить и запустить образ, 
    # описанный в Dockerfile в папке gateway
    build: ./foodgram_gateway/
    # Ключ ports устанавливает
    # перенаправление всех запросов с порта 8000 хоста
    # на порт 80 контейнера.
    ports:
      - 8000:80
```
- Шлюз в сеть контейнеров готов: `sudo docker compose up`
- Подготавливаем статику в settings.py и docker-compose.yml:
```
# Собрать статику Django
docker compose exec backend python manage.py collectstatic
# Статика приложения в контейнере backend 
# будет собрана в директорию /app/collected_static/.

# Теперь из этой директории копируем статику в /app/static/;
# эта статика попадёт на volume static в папку /static/:
docker compose exec backend cp -r /app/collected_static/. /app/static/
```
- Перезапуск Docker Compose: `docker compose stop && docker compose up --build`


## Файл .env
Файл с переменными окружения ожидает следующие значения:
- TOKEN "Секретный токен"
- POSTGRES_USER=postgres
- POSTGRES_PASSWORD=password
- POSTGRES_DB=postgres
- DB_HOST=db
- DB_PORT=5432
- DEBUG "True - для локальной разработки"
- HOSTS "Allowed hosts"

## Автор
Сычев Валерий, профиль на Github: `https://github.com/Xarfex/`
