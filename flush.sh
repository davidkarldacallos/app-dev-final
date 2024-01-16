#!/bin/bash

# Run Django management command to flush the database
python manage.py flush --noinput

# Check if media/polls directory exists before removing its contents
if [ -d "media/polls" ]; then
    rm -rf media/polls/*
else
    echo "media/polls directory does not exist."
fi

# Run Django management command to create initial data
python manage.py create_initial_data

# Run Django management command to collect static files
python manage.py collectstatic --noinput

# Run Django development server
# python manage.py runserver # dont do this in production
