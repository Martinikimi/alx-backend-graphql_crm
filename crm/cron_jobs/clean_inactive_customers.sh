#!/bin/bash
echo "Starting customer cleanup at $(date)" >> /tmp/customer_cleanup_log.txt

# CHANGE THIS LINE - Use your actual Windows path
cd /c/Users/maryw/Desktop/alx-backend-graphql_crm

python manage.py shell << EOF
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer, Order

one_year_ago = timezone.now() - timedelta(days=365)
deleted_count = 0

for customer in Customer.objects.all():
    recent_orders = Order.objects.filter(customer=customer, order_date__gte=one_year_ago)
    if not recent_orders.exists():
        customer.delete()
        deleted_count += 1

print(f"Deleted {deleted_count} inactive customers")
EOF

echo "Finished customer cleanup at $(date)" >> /tmp/customer_cleanup_log.txt