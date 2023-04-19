# dz18

```bash
    ./manage.py migrate
```


# Create 50-blogs, 10-users, 150-comments
```bash
    ./manage.py create_data_v2
```


# celery -A core worker --loglevel=INFO
```bash
    celery -A core worker --loglevel=INFO
```