from django.core.management.base import BaseCommand
from django.db import connection
from api.models import Customer, Loan
from api.tasks import load_customer_data, load_loan_data

class Command(BaseCommand):
    help = 'Load Excel data automatically'

    def handle(self, *args, **options):
        self.stdout.write("Loading Excel data...")

        # Check if data exists
        if Customer.objects.count() == 0:
            self.stdout.write("Loading data from Excel files...")

            # Load data
            result1 = load_customer_data()
            self.stdout.write(f"Customers: {result1}")

            result2 = load_loan_data()
            self.stdout.write(f"Loans: {result2}")

            # Fix sequences
            with connection.cursor() as cursor:
                cursor.execute("SELECT setval(pg_get_serial_sequence('customer', 'customer_id'), COALESCE((SELECT MAX(customer_id) FROM customer), 0) + 1, false);")
                cursor.execute("SELECT setval(pg_get_serial_sequence('loan', 'loan_id'), COALESCE((SELECT MAX(loan_id) FROM loan), 0) + 1, false);")

            self.stdout.write("Data loaded successfully!")
        else:
            self.stdout.write("Data already exists")
