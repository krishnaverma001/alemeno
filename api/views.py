from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .serializers import *
from .utils import *
from datetime import datetime, timedelta

# from .tasks import load_customer_data, load_loan_data

@api_view(['POST'])
def register_customer(request):
    """Register a new customer"""
    serializer = CustomerRegistrationSerializer(data=request.data)

    if serializer.is_valid():
        # Calculate approved limit
        monthly_salary = serializer.validated_data['monthly_salary']
        approved_limit = calculate_approved_limit(monthly_salary)

        customer = Customer.objects.create(
            first_name=serializer.validated_data['first_name'],
            last_name=serializer.validated_data['last_name'],
            age=serializer.validated_data['age'],
            phone_number=serializer.validated_data['phone_number'],
            monthly_salary=monthly_salary,
            approved_limit=approved_limit,
        )

        response_serializer = CustomerRegistrationResponseSerializer(customer)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def check_loan_eligibility(request):
    """Check loan eligibility for a customer"""
    serializer = LoanEligibilitySerializer(data=request.data)

    if serializer.is_valid():
        customer_id = serializer.validated_data['customer_id']
        loan_amount = serializer.validated_data['loan_amount']
        interest_rate = serializer.validated_data['interest_rate']
        tenure = serializer.validated_data['tenure']

        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'},
                          status=status.HTTP_404_NOT_FOUND)

        # Calculate credit score
        credit_score = calculate_credit_score(customer_id)

        # Determine approval and corrected interest rate
        corrected_rate = get_interest_rate_by_credit_score(credit_score, interest_rate)

        if corrected_rate is None or credit_score <= 10:
            approval = False
            corrected_rate = interest_rate
        else:
            approval = True

        # Calculate monthly installment
        monthly_installment = calculate_monthly_installment(
            loan_amount, corrected_rate, tenure
        )

        # Check EMI constraint
        if approval and not check_emi_constraint(customer_id, monthly_installment):
            approval = False

        response_data = {
            'customer_id': customer_id,
            'approval': approval,
            'interest_rate': float(interest_rate),
            'corrected_interest_rate': float(corrected_rate),
            'tenure': tenure,
            'monthly_installment': float(monthly_installment)
        }

        response_serializer = LoanEligibilityResponseSerializer(data=response_data)
        if response_serializer.is_valid():
            return Response(response_serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_loan(request):
    """Create a new loan"""
    serializer = LoanCreateSerializer(data=request.data)

    if serializer.is_valid():
        customer_id = serializer.validated_data['customer_id']
        loan_amount = serializer.validated_data['loan_amount']
        interest_rate = serializer.validated_data['interest_rate']
        tenure = serializer.validated_data['tenure']

        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'},
                          status=status.HTTP_404_NOT_FOUND)

        # Check eligibility
        credit_score = calculate_credit_score(customer_id)
        corrected_rate = get_interest_rate_by_credit_score(credit_score, interest_rate)

        monthly_installment = calculate_monthly_installment(
            loan_amount, corrected_rate or interest_rate, tenure
        )

        loan_approved = False
        loan_id = None
        message = ""

        if corrected_rate is None or credit_score <= 10:
            message = "Loan not approved due to low credit score"
        elif not check_emi_constraint(customer_id, monthly_installment):
            message = "Loan not approved due to EMI constraint (>50% of monthly salary)"
        else:
            # Create the loan
            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=tenure * 30)  # Approximate

            loan = Loan.objects.create(
                customer=customer,
                loan_amount=loan_amount,
                tenure=tenure,
                interest_rate=corrected_rate,
                monthly_repayment=monthly_installment,
                start_date=start_date,
                end_date=end_date,
            )

            loan_approved = True
            loan_id = loan.loan_id
            message = "Loan approved successfully"

        response_data = {
            'loan_id': loan_id,
            'customer_id': customer_id,
            'loan_approved': loan_approved,
            'message': message,
            'monthly_installment': float(monthly_installment)
        }

        response_serializer = LoanCreateResponseSerializer(data=response_data)
        if response_serializer.is_valid():
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def view_loan(request, loan_id):
    """View specific loan details"""
    loan = get_object_or_404(Loan, loan_id=loan_id)
    serializer = LoanDetailSerializer(loan)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def view_customer_loans(request, customer_id):
    """View all loans for a customer"""
    try:
        customer = Customer.objects.get(customer_id=customer_id)
        loans = Loan.objects.filter(customer=customer, is_active=True)
        serializer = LoanListSerializer(loans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'},
                       status=status.HTTP_404_NOT_FOUND)

# @api_view(['POST'])                                               # MANUAL API ENDPOINT FOR LOADING CUST + LOAN DATA
# def load_data(request):                                           # CURRENTLY AUTO LOAD ON DOCKER BUILD
#     """Trigger background tasks to load initial data"""
#     load_customer_data.delay()
#     load_loan_data.delay()
#     return Response({'message': 'Data loading tasks started'},
#                     status=status.HTTP_200_OK)
