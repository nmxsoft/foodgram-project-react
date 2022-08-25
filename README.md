![WORKFLOW_STATUS](https://github.com/nmxsoft/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

# ***Foodgram-project-react***

API для проекта Foodgram - приложение «Продуктовый помощник - FOODGRAM»: сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд. 
- API проекта позволяет: 
    - регистрироваться и получать токен пользователям;
    - управлять своими постами;
    - добавлять в Избранное полюбившиеся рецепты;
    - длу удобства, пользователь может скачать список продуктов, необходимых для приготовления того или иного рецепта.

### Dev режим:
1. Клонируйте репозиторий:
    *$ git clone https://github.com/nmxsoft/foodgram-project-react.git*
 
2. Создайте виртуальное окружение:
    *$ python -m venv venv*
 
3. Установите зависимости:
    *$ pip install -r requirements.txt*

4. Создайте и примените миграции:
    *$ python manage.py makemigrations*
    *$ python manage.py migrate*

5. Запустите django сервер:
    *$ python manage.py runserver*

### Демо версия:
   - Сайт http://ip/signin
   - Админка доступна по адресу http://ip/admin/
   - API доступна по адресу http://ip/api/

## **Автор:**
Max Nikulin

