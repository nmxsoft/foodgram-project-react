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
 
2. Создайте виртуальное окружение (venv) - должен быть флажок в начале строки:
    *$ python -m venv venv*
 
3. Установите зависимости:
    *$ pip install -r requirements.txt*

4. Создайте и примените миграции:
    *$ python manage.py makemigrations*
    *$ python manage.py migrate*

5. Запустите django сервер:
    *$ python manage.py runserver*

6. URLs сайта **FoodGram**:
   - Сайт http://51.250.21.86/signin
   - Админка доступна по адресу http://51.250.21.86/admin/
   - API архитектура доступна по адресу http://51.250.21.86/api/

## **Автор:**
Max Nikulin

