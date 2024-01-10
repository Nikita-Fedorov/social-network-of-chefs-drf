#  Foodgram - ваша новая книга рецептов, а также это социальная сеть для любителей кушать и готовить.

В Foodgram Вы можете делиться своими любимыми рецептами и добавлять понравившиеся Вам рецепты в избранное. Подписываться на любимых авторов. Особенностью Foodgram является возможность добавить рецепт в список покупок. В него будут добавлены названия и количество ингредиентов для приготовления блюда. Вы сможете скачать список ингредиентов и их количество, которое понадобится для приготовления блюда. А если блюд несколько, а ингредиенты повторяются, то они будут суммироваться.

Проект доступен по адресу:

http://foodgram-blog.sytes.net/recipes (сервер неактивен)

Доступ в админ панель:

Email:
admin@admin.ru
Password:
admin

## Как запустить проект на сервере:
- Клонировать репозиторий:

    git clone git@github.com:Nikita-Fedorov/foodgram-project-react.git

- В репозитории на GitHub перейдите в раздел "Settings", затем перейдите в раздел "Secrets and Variables". Затем нажмите на кнопку "Actions" и добавьте следующие секреты:

DOCKER_PASSWORD=<Ваш пароль на DockerHub>
DOCKER_USERNAME=<Логин DockerHub>
HOST=<IP адрес вашего сервера>
SSH_KEY=<SSH key private>
SSH_PASSPHRASE=<passphrase>

Создайте файл .env на сервере

    sudo nano .env

Добавить в него:

- POSTGRES_USER=foodgram_user
- POSTGRES_PASSWORD=admin
- POSTGRES_DB=foodgram
- DB_HOST=db
- DB_PORT=5432
- SECRET_KEY = 'SECRET_KEY из settings.py'
- DEBUG = False
- TIME_ZONE = 'UTC'

Создайте файл конфигураций Nginx:

    sudo nano /etc/nginx/sites-enabled/default

Добавьте в файл следующий код:

    server {
        server_name foodgram-blog.sytes.net;
        server_tokens off;
        
        location / {
            proxy_set_header        Host $http_host;
            proxy_set_header        X-Real-IP $remote_addr;
            proxy_set_header        X-Forwarded-Proto $scheme;
            proxy_pass              http://backend:8080;
        }
    }

Если у Вас не установлен докер, установите его:

https://eternalhost.net/base/vps-vds/ustanovka-docker-linux

## Запуск проекта

В терминале на вкладке 'foodgram-project-react' выполните команды:

    git add .
    git commit -m ''
    git push

### Затем перейдите на сервер и выполните следующие команды:

Создайте суперюзера для создания Tags (тэгов) для рецептов:

    sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser


## Технологии

- Python 3.9
- Django 3.2
- Django REST framework
- PostgreSQL
- Nginx
- Docker
- GitHub Actions

Автор Backend & DevOps: Никита Федоров(github.com/Nikita-Fedorov)
