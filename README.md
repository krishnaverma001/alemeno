# ALEMENO - Credit Approval System

A comprehensive Django REST API system for managing customer credit approvals and loan processing with intelligent credit scoring algorithms.

---

Get the entire system running with just 3 commands:

```commandline
git clone https://github.com/krishnaverma001/alemeno.git
cd alemeno
docker-compose up --build
```

---

Create a '.env' file for database and celery setup:
```commandline
SECRET_KEY=
DEBUG=True
NAME=postgres
USER=name
PASSWORD=password
HOST=localhost
PORT=5432
CELERY_BROKER_URL=redis://localhost:6379/0
```

---

The system automatically:

- Creates admin super user account.
  - User: 'admin', 
  - Email: 'admin@alemeno.com', 
  - Password: 'admin123'
- Loads sample customer and loan data.
- Starts Redis for background tasks.
- Launches the Django API server.

---

## Tech Stack

- Backend: Django (4+) + Django REST Framework
- Database: PostgreSQL 15
- Message Broker: Redis 7
- Background Tasks: Celery
- Containerization: Docker + Docker Compose
- Data Processing: Pandas, openpyxl

---

## API Endpoints

### 1. Customer Registration

```commandline
POST /api/register/
```

Request:
```commandline
{
    "first_name": "John",
    "last_name": "Doe",
    "age": 30,
    "monthly_income": 50000,
    "phone_number": 9876543210
}
```

Response:
```commandline
{
    "customer_id": 301,
    "name": "John Doe",
    "age": 30,
    "monthly_income": "50000.00",
    "approved_limit": "1800000.00",
    "phone_number": 9876543210
}
```
### 2. Loan Eligibility Test
```commandline
POST /api/check-eligibility/
```
Request:
```commandline
{
    "customer_id": 101,
    "loan_amount": 200000,
    "interest_rate": 10.0,
    "tenure": 24
}
```
Response:
```commandline
{
    "customer_id": 101,
    "approval": true,
    "interest_rate": 10.0,
    "corrected_interest_rate": 12.0,
    "tenure": 24,
    "monthly_installment": "9456.25"
}
```
### 3. Loan Creation
```
POST /api/create-loan/
```
Request:
```commandline
{
    "customer_id": 101,
    "loan_amount": 150000,
    "interest_rate": 12.0,
    "tenure": 18
}
```
Response:
```commandline
{
    "loan_id": 1,
    "customer_id": 101,
    "loan_approved": true,
    "message": "Loan approved successfully",
    "monthly_installment": "9456.25"
}
```

### 4. View Loan Details
```commandline
GET /api/view-loan/{loan_id}/
```
Response:
```commandline
{
    "loan_id": 1,
    "customer": {
        "customer_id": 101,
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": 9876543210,
        "age": 30
    },
    "loan_amount": "150000.00",
    "interest_rate": "12.00",
    "monthly_installment": "9456.25",
    "tenure": 18,
    "repayments_left": 15
}
```
### 5. View Customer Loans
```
GET /api/view-loans/{customer_id}/
```
Response:
```
[
    {
        "loan_id": 1,
        "loan_amount": "150000.00",
        "interest_rate": "12.00",
        "monthly_installment": "9456.25",
        "repayments_left": 15
    }
]
```
---

## DATABASE SCHEMA

### 1. Customer
```commandline
customer_id (AutoField, Primary Key)
first_name (CharField)
last_name (CharField) 
age (PositiveIntegerField)
phone_number (BigIntegerField)
monthly_salary (DecimalField)
approved_limit (DecimalField)
current_debt (DecimalField)
created_at (DateTimeField)
updated_at (DateTimeField)
```
### 2. Loan
```commandline
loan_id (AutoField, Primary Key)
customer (ForeignKey to Customer)
loan_amount (DecimalField)
tenure (IntegerField)
interest_rate (DecimalField)
monthly_repayment (DecimalField)
emis_paid_on_time (IntegerField)
start_date (DateField)
end_date (DateField)
is_active (BooleanField)
created_at (DateTimeField)
updated_at (DateTimeField)
```