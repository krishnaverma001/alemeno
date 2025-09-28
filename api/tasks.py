from celery import shared_task
import pandas as pd
from .models import Customer, Loan
from datetime import datetime
import os
from config import settings

BASE_DIR = settings.BASE_DIR

@shared_task
def load_customer_data():
    """Load customer data from Excel file with duplicate check"""
    file_path = os.path.join(BASE_DIR, 'data', 'customer_data.xlsx')

    if not os.path.exists(file_path):
        return f"File not found: {file_path}"

    try:
        df = pd.read_excel(file_path, header=0, index_col=None)
        created_count = 0

        for _, row in df.iterrows():
            customer, created = Customer.objects.get_or_create(
                customer_id=row['Customer ID'],
                defaults={
                    'first_name': row['First Name'],
                    'last_name': row['Last Name'],
                    'age': row['Age'],
                    'phone_number': row['Phone Number'],
                    'monthly_salary': row['Monthly Salary'],
                    'approved_limit': row['Approved Limit'],
                    'current_debt': row.get('Current Debt', 0)
                }
            )
            if created:
                created_count += 1

        return f"Successfully loaded {created_count} customers"

    except Exception as e:
        return f"Error loading customer data: {str(e)}"

@shared_task
def load_loan_data():
    """Load loan data from Excel file with duplicate check"""
    file_path = os.path.join(BASE_DIR, 'data', 'loan_data.xlsx')

    if not os.path.exists(file_path):
        return f"File not found: {file_path}"

    try:
        df = pd.read_excel(file_path)
        created_count = 0

        for _, row in df.iterrows():
            try:
                customer = Customer.objects.get(customer_id=row['Customer ID'])

                loan, created = Loan.objects.get_or_create(
                    loan_id=row['Loan ID'],
                    defaults={
                        'customer': customer,
                        'loan_amount': row['Loan Amount'],
                        'tenure': row['Tenure'],
                        'interest_rate': row['Interest Rate'],
                        'monthly_repayment': row['Monthly payment'],
                        'emis_paid_on_time': row['EMIs paid on Time'],
                        'start_date': pd.to_datetime(row['Date of Approval']).date(),
                        'end_date': pd.to_datetime(row['End Date']).date(),
                        'is_active': pd.to_datetime(row['End Date']).date() >= datetime.now().date()
                    }
                )
                if created:
                    created_count += 1

            except Customer.DoesNotExist:
                continue

        return f"Successfully loaded {created_count} loans"

    except Exception as e:
        return f"Error loading loan data: {str(e)}"
