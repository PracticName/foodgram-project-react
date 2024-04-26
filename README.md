# praktikum_new_diplom

### _Логин суперпользователя:_ mesuper

### _пароль:_ foodgram1

## Описание

  Данный сервис предоставляет Вам возможность делиться своими _рецептаим_ с сообществом __foodgram__.
  Вы можете публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публиуации других авторов.Пользователям сайта также будет доступен сервис _Список покупок_»_. Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

  Чтобы использовать сервис, необходимо зарегестрироваться (```https://food.hopto.org/```).

## Как запустить проект:
1. На ```https://github.com/``` сделайте форк и клонируйте репозиторий:
   ```https://github.com/PracticName/foodgram-project-react```
2. Заполните следующие переменные в файле .env (файл создайте в корне проекта)
   Пример:
   POSTGRES_DB=django 
   POSTGRES_USER=django
   POSTGRES_PASSWORD=password
   DB_NAME=foodgram
   DB_HOST=db
   DB_PORT=5432
   SECRET_KEY=django
   ALLOWED_HOSTS=127.0.0.1,localhost,<ip сервера>,<твой домен>
   DEBUG=True
3. Запустите Docker
4. Запустите файл docker-compose.yml в корне проекта
   ```docker compose --build up```
   произойдет сборка образов и запуск контейнеров
5. Выполняем миграции и создайте пользователя
   ```docker compose exec backend pyhon manage.py migrate```
   ```docker compose exec backend pyhon manage.py createsuperuser```
6. Соберите статику
   ```docker compose exec backend pyhon manage.py collectstatic```
   ```docker compose exec backend backend cp -r /app/collected_static/. /backend_static```

Для деплоя на сервер на ```https://github.com/``` в репозитории проекта перейдите _Settings-->Secrets and variables-->Actions_.
Создайте следующие секреты через кнопку _New repository secret_
DOCKER_PASSWORD - пароль Docker
DOCKER_USERNAME - имя пользователя Docker
HOST - ip сервера
SSH_KEY - закрытый ключ для подключения к серверу
SSH_PASSPHRASE - пароль к закрытому кдючу
TELEGRAM_TO - ваш id telegram
TELEGRAM_TOKEN - ключ вашего бота в telegram
USER - имя пользователя на сервере

## Технологии

1. Полный список библиотек по фронтенду /frontend/package.json
2. Полный список библиотек по бекенду /backend/requirements.txt
3. Docker ```https://www.docker.com/```
4. Nginx ```https://nginx.org/```
5. Telegram ```https://telegram.org/```

## Дата-миграции
  
  Не забудьте переопределить константу ```CUR_DIR``` в _setting.py_, если хотите загружать данные из другой папки (по умолчанию это дириктория _backend_)

  Создайте пустую миграцию 
  ```python manage.py makemigrations --empty appname```

  Создается примерно такая миграция:
  ```
  import csv

  from django.conf import settings
  rom django.db import migrations

  class Migration(migrations.Migration):
      dependencies = []
      operations = []
  ```

   Далеее добавьте в operations операцию RunPython. Она запускает функцию, которую вы ей предадите. 

  ```operations = [migrations.RunPython(copy_ingredients),]```

  Осталось только написать эту функцию:

  ```
  import csv

  from django.conf import settings
  from django.db import migrations


 def copy_ingredients(apps, schema_editor):
      Ingredient = apps.get_model('recipes', 'Ingredient')
      with open(
          str(settings.CUR_DIR) + '/data/' + 'ingredients.csv',
          'r',
          encoding='utf-8'
      ) as csv_file:
          reader = csv.reader(csv_file, delimiter=',')
          for row in reader:
              Ingredient.objects.get_or_create(
                 name=row[0],
                  measurement_unit=row[1]
              )

  class Migration(migrations.Migration):
      dependencies = [('recipes', '0003_auto_20240412_1759'),]
      operations = [migrations.RunPython(copy_ingredients),]
  ```

## Примеры использования Api

- Список пользователей
  GET ```api/users/``` 
  **Ответ**
  ```
  {
    "count": 123,
    "next": "http://foodgram.example.org/api/users/?page=4",
    "previous": "http://foodgram.example.org/api/users/?page=2",
    "results": [
      {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Пупкин",
        "is_subscribed": false
      }
    ]
  }
  ```

- Создание пользователя
  POST ```api/users/```
  ```
  {
    "email": "vpupkin@yandex.ru",
    "username": "vasya.pupkin",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "password": "Qwerty123"
  }
  ```
  **Ответ**
  ```
  {
    "email": "vpupkin@yandex.ru",
    "id": 0,
    "username": "vasya.pupkin",
    "first_name": "Вася",
    "last_name": "Пупкин"
  }

- Профиль пользователя
  GET ```api/users/{id}/```
  **Ответ**
  ```
  {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "is_subscribed": false
  }
  ```
- Текущий пользователь
  GET ```api/users/me/```
  **Ответ**
  ```
  {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "is_subscribed": false
  }
  ```
- Изменение пароля
  POST ```api/users/set_password/```
  ```
  {
    "new_password": "string",
    "current_password": "string"
  }
  ```
- Получить токен авторизации
  POST ```api/auth/token/login/```
  ```
  {
    "password": "string",
    "email": "string"
  }
  ```
  **Ответ**
  ```
  {
    "auth_token": "string""
  }
  ```
- Удаление токена
  POST ```api/auth/token/logout/```
  ```
- Cписок тегова
  GET ```api/tags/```
  **Ответ**
  ```
  [
    {
      "id": 0,
      "name": "Завтрак",
      "color": "#E26C2D",
      "slug": "breakfast"
    }
  ]
  ```
- Получение тега
  GET ```api/tags/{id}/```
  **Ответ**
  ```
  [
    {
      "id": 0,
      "name": "Завтрак",
      "color": "#E26C2D",
      "slug": "breakfast"
    }
  ]
- Список рецептов
  GET ```api/recipes/```
  **Ответ**
  ```
  {
    "count": 123,
    "next": "http://foodgram.example.org/api/recipes/?page=4",
    "previous": "http://foodgram.example.org/api/recipes/?page=2",
    "results": [
      {
        "id": 0,
        "tags": [
            {
              "id": 0,
              name": "Завтрак",
              "color": "#E26C2D",
              "slug": "breakfast"
            }
        ],
        "author": {
            "email": "user@example.com",
            "id": 0,
            "username": "string",
            "first_name": "Вася",
            "last_name": "Пупкин",
            "is_subscribed": false
        },
        "ingredients": [
            {
              "id": 0,
              "name": "Картофель отварной",
              "measurement_unit": "г",
              "amount": 1
            }
        ],
        "is_favorited": true,
        "is_in_shopping_cart": true,
        "name": "string",
        "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
        "text": "string",
        "cooking_time": 1
      }
    ] 
  }
  ```
- Создание рецепта
  POST ```api/recipes/```
  ```
  {
    "ingredients": [
      {
        "id": 1123,
        "amount": 10
      }
    ],
    "tags": [
      1,
      2
    ],
    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/    S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
    "name": "string",
    "text": "string",
    "cooking_time": 1
  }
  ```
  **Ответ**
  ```
  {
    "id": 0,
    "tags": [
      {
        "id": 0,
        "name": "Завтрак",
        "color": "#E26C2D",
        "slug": "breakfast"
      }
    ],
    "author": {
      "email": "user@example.com",
      "id": 0,
      "username": "string",
      "first_name": "Вася",
      "last_name": "Пупкин",
      "is_subscribed": false
    },
    "ingredients": [
      {
          "id": 0,
          "name": "Картофель отварной",
          "measurement_unit": "г",
          "amount": 1
      }
    ],
    "is_favorited": true,
    "is_in_shopping_cart": true,
    "name": "string",
    "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
    "text": "string",
    "cooking_time": 1
  }
  ```
- Получение рецепта
  GET ```api/recipes/{id}/```
  **Ответ**
  ```
  {
    "id": 0,
    "tags": [
      {
        "id": 0,
        "name": "Завтрак",
        "color": "#E26C2D",
        "slug": "breakfast"
      }
    ],
    "author": {
      "email": "user@example.com",
      "id": 0,
      "username": "string",
      "first_name": "Вася",
      "last_name": "Пупкин",
      "is_subscribed": false
    },
    "ingredients": [
      {
          "id": 0,
          "name": "Картофель отварной",
          "measurement_unit": "г",
          "amount": 1
      }
    ],
    "is_favorited": true,
    "is_in_shopping_cart": true,
    "name": "string",
    "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
    "text": "string",
    "cooking_time": 1
  }
  ```
- Обновление рецепта
  PATCH ```api/recipes/{id}/```
  ```
  {
    "ingredients": [
      {
        "id": 1123,
        "amount": 10
      }
    ],
    "tags": [
      1,
      2
    ],
    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/    S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
    "name": "string",
    "text": "string",
    "cooking_time": 1
  }
  ```
  **Ответ**
  ```
  {
    "id": 0,
    "tags": [
      {
        "id": 0,
        "name": "Завтрак",
        "color": "#E26C2D",
        "slug": "breakfast"
      }
    ],
    "author": {
      "email": "user@example.com",
      "id": 0,
      "username": "string",
      "first_name": "Вася",
      "last_name": "Пупкин",
      "is_subscribed": false
    },
    "ingredients": [
      {
          "id": 0,
          "name": "Картофель отварной",
          "measurement_unit": "г",
          "amount": 1
      }
    ],
    "is_favorited": true,
    "is_in_shopping_cart": true,
    "name": "string",
    "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
    "text": "string",
    "cooking_time": 1
  }
  ```
- Удаление рецепта
  DELETE ```api/recipes/{id}/```
- Скачать список покупок
  GET ```api/recipes/download_shopping_cart/```
- Добавить рецепт в список покупок
  POST ```api/recipes/{id}/shopping_cart/```
  **Ответ**
  ```
  {
    "id": 0,
    "name": "string",
    "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
    "cooking_time": 1
  }
  ```
- Удаление рецепта
  DELETE ```api/recipes/{id}/shopping_cart/```
- Добавить рецепт в список покупок
  POST ```api/recipes/{id}/favorite/```
  **Ответ**
  ```
  {
    "id": 0,
    "name": "string",
    "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
    "cooking_time": 1
  }
  ```
- Мои подписки
  GET ```api/users/subscriptions/```
  **Ответ**
  ```
  {
     "count": 123,
     "next": "http://foodgram.example.org/api/users/subscriptions/?page=4",
     "previous": "http://foodgram.example.org/api/users/subscriptions/?page=2",
     "results": [
       {
         "email": "user@example.com",
         "id": 0,
         "username": "string",
         "first_name": "Вася",
         "last_name": "Пупкин",
         "is_subscribed": true,
         "recipes": [],
         "recipes_count": 0
      }
    ]
  }
  ```
- Подписаться на пользователя
  POST ```api/users/{id}/subscribe/```
  **Ответ**
  ```
  {    
     "email": "user@example.com",
     "id": 0,
     "username": "string",
     "first_name": "Вася",
     "last_name": "Пупкин",
     "is_subscribed": true,
     "recipes": [
      {
        "id": 0,
        "name": "string",
        "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
        "cooking_time": 1
      }
    ],
     "recipes_count": 0
  }
  ```
- Отписаться от пользователя
  DELETE ```api/users/{id}/subscribe/```
- Список ингредиентов
  GET ```api/ingredients/```
  **Ответ**
  ```
  [
    {
      "id": 0,
      "name": "Капуста",
      "measurement_unit": "кг"
    }
  ]
  ```
- Получение ингредиента
  GET ```pi/ingredients/{id}/```
  **Ответ**
  ```
  [
    {
      "id": 0,
      "name": "Капуста",
      "measurement_unit": "кг"
    }
  ]
  ```