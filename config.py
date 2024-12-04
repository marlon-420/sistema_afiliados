import os

config = {
    'host': os.getenv('DATABASE_HOST'),
    'user': os.getenv('DATABASE_USERNAME'),
    'password': os.getenv('DATABASE_PASSWORD'),
    'database': os.getenv('DATABASE'),
    'ssl': {
        'ca': os.getenv('DATABASE_SSL_CA')
    }
}
