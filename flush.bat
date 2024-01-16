python manage.py flush --noinput
del /Q /S media\polls\*.*
python manage.py create_initial_data
python manage.py collectstatic --noinput
python manage.py runserver