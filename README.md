[![Foodgram workflow](https://github.com/NikoKozeev/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/NikoKozeev/foodgram-project-react/actions/workflows/main.yml)

## Ссылка Репозиторий - NikoKozeev(https://github.com/NikoKozeev/foodgram-project-react)
## Ссылка на проект - Foodgram(https://foodgramov.sytes.net/)

## О проекте

Foodgram это сайт рецептов и социальная сеть, в которой пользователи могут обмениваться любимыми рецептами

## Основные особенности

- Возможность создать свой собственный аккаунт на сайте
- Возможность поделиться любимыми рецептами с другими исскушенными пользователями и любителями вкусно покушать
- Возможность подписаться на любимого автора и не пропускать ни одного его кулинарного шедевра

## О скрипте для переноса ингридиентов в базу данных
database_script используется для заполнения базы данных данными из файла CSV.
Разместите файл в папке 'data' в корне проекта.
Для запуска используйте следующую команду:
python manage.py runscript database_script

### Локальное развертывание

1. Клонируйте репозиторий на вашем локальном компьютере:

   ```bash
   git clone git@github.com:NikoKozeev/foodgram-project-react.git
   cd foodgram-project-react
   py manage.py makemigrations
   py manage.py migrate
   py manage.py runscript database_script
   py manage.py runserver

2. Установите зависимости для бэкенда и запустите сервер разработки:
   ```bash
   cd ../frontend
   npm install
   npm start
Откройте браузер и перейдите по адресу http://127.0.0.1, чтобы использовать локальную версию Foodgram.


### Удаленное развертывание
1. Подключитесь по SSH ключу к удаленному серверу и откройте в директорию проекта.
2. Подготовьте окружение на удаленном сервере (Docker, Docker Compose и т.д.).
3. Выполните команду fork, на своём аккаунте github из этого репозитория.
## Ссылка Репозиторий - NikoKozeev https://github.com/NikoKozeev/foodgram-project-react
4. Клонируйте репозиторий на удаленном сервере:
   ```bash
   git clone git@github.com:NikoKozeev/foodgram-project-react.git
   cd foodgram-project-react
5. Выполните скачивание и развертывание продакшн версии:
```bash
   docker-compose -f docker-compose.production.yml pull
   docker-compose -f docker-compose.production.yml up -d
```
6. Для успешного развертывания проекта необходимо в главной директории создать файл .env, где будут указаны следуюшие параметры:
- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD
- DB_NAME
- DB_HOST
- DB_PORT
- DEBUG
- SECRET_KEY
- ALLOWED_HOSTS

7. Для создания пользователя с правами администратора необходимо в терминале выполнить команду:
```bash
   cd backend
   py manage.py createsuperuser
```

### Автор

NikoKozeev https://github.com/NikoKozeev Николай Козеев

### Используемые технологии

Python, Django, PostgreSQL, Django Rest Framework, Djoser
