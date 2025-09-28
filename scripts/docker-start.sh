#!/bin/bash
echo "🚀 Starting Credit Approval System..."

echo "Setting up database..."

python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Loading Excel data..."
python manage.py load

# Create admin user
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@alemeno.com', 'admin123')
    print('✅ Admin user created: admin/admin123')
"

echo "Setup completed! Starting server..."
python manage.py runserver 0.0.0.0:8000