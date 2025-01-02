#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status.

echo "Applying migrations..."
python manage.py makemigrations
python manage.py migrate


#echo "Creating superuser..."
#python manage.py createsuperuser --noinput \
#  --username niki \
#  --email niki@gmail.com

#echo "Setting superuser password..."
#python manage.py shell -c "
#from django.contrib.auth import get_user_model;
#User = get_user_model();
#try:
#    user = User.objects.get(username='niki');
#    user.set_password('1234');
#    user.save();
#    print('Password updated successfully.')
#except User.DoesNotExist:
#    print('Superuser does not exist, skipping password setup.');
#"


echo "Starting server..."
python manage.py runserver 0.0.0.0:8000
