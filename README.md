# Simple user timelog app

REST API for a multi-user and multi-project work time tracking
application using Django and Django Rest Framework.


### Virtual Environment
1. Clone the project with ..
    ```
    https://github.com/raficsedu/timelog.git
    ```

2. Go to the project directory and run ..
    ```
    1. source env/bin/activate
    2. pip install -r requirements.txt
    3. python manage.py migrate
    4. python manage.py runserver
    ```

Now open up your browser and navigate to http://127.0.0.1:8000.

## Automatic Test

For running all the automatic test cases, run the following commands. You must need to be inside virtual environment or into docker container.
```
1. python manage.py test
```
