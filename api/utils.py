from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from .models import Customer, Loan


def calculate_approved_limit(monthly_salary):
    # Calculate approved limit as 36 * monthly_salary rounded to nearest lakh

    limit = Decimal(str(monthly_salary)) * 36

    return (limit / 100000).quantize(Decimal('1'), rounding=ROUND_HALF_UP) * 100000  # Round off


def calculate_credit_score(customer_id):
    # Calculate credit score based on historical data

    try:
        customer = Customer.objects.get(customer_id=customer_id)
        loans = Loan.objects.filter(customer=customer)

        if not loans.exists():
            return 50  # Default score for new customers

        # Check if sum of current loans > approved limit

        current_loans = loans.filter(is_active=True)
        current_debt = sum(loan.loan_amount for loan in current_loans)
        if current_debt > customer.approved_limit:
            return 0

        credit_score = 0
        total_loans = loans.count()

        # Component 1: Past loans paid on time (40% weight)

        total_emis = sum(loan.tenure for loan in loans)
        total_paid_on_time = sum(loan.emis_paid_on_time for loan in loans)
        if total_emis > 0:
            on_time_ratio = total_paid_on_time / total_emis
            credit_score += on_time_ratio * 40

        # Component 2: Number of loans taken (20% weight)

        if total_loans <= 2:
            credit_score += 20
        elif total_loans <= 5:
            credit_score += 15
        elif total_loans <= 8:
            credit_score += 10
        else:
            credit_score += 5

        # Component 3: Loan activity in current year (20% weight)

        current_year_loans = loans.filter(start_date__year=datetime.now().year)

        if current_year_loans.count() <= 2:
            credit_score += 20
        elif current_year_loans.count() <= 4:
            credit_score += 15
        else:
            credit_score += 10

        # Component 4: Loan approved volume (20% weight)

        total_loan_amount = sum(loan.loan_amount for loan in loans)

        if total_loan_amount <= customer.approved_limit * Decimal('0.5'):
            credit_score += 20
        elif total_loan_amount <= customer.approved_limit:
            credit_score += 15
        else:
            credit_score += 5

        return min(100, max(0, int(credit_score)))

    except Customer.DoesNotExist:
        return 0


def calculate_monthly_installment(loan_amount, interest_rate, tenure):
    # Calculate EMI using compound interest formula

    principal = Decimal(str(loan_amount))
    rate = Decimal(str(interest_rate)) / 100 / 12  # Monthly rate
    n = Decimal(str(tenure))

    if rate == 0:
        return principal / n

    # EMI = P * r * (1+r)^n / ((1+r)^n - 1)

    power = (1 + rate) ** n
    emi = principal * rate * power / (power - 1)
    return emi.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def get_interest_rate_by_credit_score(credit_score, requested_rate):
    # Determine appropriate interest rate based on credit score

    if credit_score > 50:
        return max(requested_rate, Decimal('8.0'))
    elif credit_score > 30:
        return max(requested_rate, Decimal('12.0'))
    elif credit_score > 10:
        return max(requested_rate, Decimal('16.0'))
    else:
        return None  # Loan not approved


def check_emi_constraint(customer_id, additional_emi=0):
    # Check if total EMIs exceed 50% of monthly salary

    try:
        customer = Customer.objects.get(customer_id=customer_id)
        current_loans = Loan.objects.filter(customer=customer, is_active=True)
        total_emi = sum(loan.monthly_repayment for loan in current_loans) + additional_emi
        return total_emi <= customer.monthly_salary * Decimal('0.5')
    except Customer.DoesNotExist:
        return False
