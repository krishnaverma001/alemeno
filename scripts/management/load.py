import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.tasks import load_customer_data, load_loan_data
from django.db import connection


def reset_sequences():
    """Fix auto-increment sequences after data loading"""
    print("\n🔧 Resetting sequences...")

    with connection.cursor() as cursor:
        # Reset customer sequence
        cursor.execute("""
            SELECT setval(
                pg_get_serial_sequence('customer', 'customer_id'),
                COALESCE((SELECT MAX(customer_id) FROM customer), 0) + 1,
                false
            );
        """)

        # Reset loan sequence
        cursor.execute("""
            SELECT setval(
                pg_get_serial_sequence('loan', 'loan_id'),
                COALESCE((SELECT MAX(loan_id) FROM loan), 0) + 1,
                false
            );
        """)

    print("✅ Sequences reset successfully!")


if __name__ == '__main__':
    print("Loading customer data...")
    result1 = load_customer_data()
    print(result1)

    print("Loading loan data...")
    result2 = load_loan_data()
    print(result2)

    # Fix sequences after loading
    reset_sequences()
