# vaccine_slot_finder

##About Project: It can be use to call APISetu api's and work as per your need.
Current functionality: Simple communication via telegram bot.

Setup.
1) create virtual env and activate
2) Install Dependencies     `pip install -r installed_packages`
3) copy .env from .env_example and add your telegram bot api token
4) Run Commands: 

    `python manage.py migrate`
    
    `python manage.py installtasks`
    
    `python manage.py telebot`

5) Sync States and District

    ```
    from app.models import *
    States.sync()
    Disrtict.sync()
    ```

6) Create user for admin
    `python manage.py createsuperuser`
    
7) To Open Admin on browser http://127.0.0.1:8000

    `python manage.py runserver 0.0.0.0:8000`

