
DEBUG = True


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "localdata",  # دقیقا اسم دیتابیس لوکال
        "USER": "postgres",
        "PASSWORD": "meysam@@138100",
        "HOST": "localhost",
        "PORT": "5432",
    }
}