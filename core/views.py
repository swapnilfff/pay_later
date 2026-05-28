from django.shortcuts import render, redirect
# from .models import Merchant, Customer
from django.contrib import messages
from .utils import render_to_pdf
from .admin import ADMIN_USERNAME, ADMIN_PASSWORD
from django.http import JsonResponse
from .models import (
    Merchant,
    Customer,
    CreditTransaction,
    Payment,
    Notification
)

def index(request):
    return render(request, 'index.html')


def register(request):

    if request.method == "POST":

        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        business_name = request.POST.get('business_name')
        password = request.POST.get('password')

        Merchant.objects.create(
            name=name,
            email=email,
            phone=phone,
            business_name=business_name,
            password=password
        )

        return redirect('/login/')

    return render(request,
    'merchant/register.html')


def login_view(request):

    if request.method == "POST":

        email = request.POST.get('email')
        password = request.POST.get('password')

        try:

            merchant = Merchant.objects.get(
                email=email,
                password=password
            )

            # Check approval

            if merchant.status != "Approved":

                messages.error(request,
                "Your account is pending approval")

                return redirect('/login/')

            # Session Create

            request.session['merchant_id'] = merchant.id

            return redirect('/dashboard/')

        except:

            messages.error(request,
            "Invalid Email or Password")

            return redirect('/login/')

    return render(request,
    'merchant/login.html')


def dashboard(request):

    merchant_id = request.session.get('merchant_id')

    if not merchant_id:

        return redirect('/login/')

    merchant = Merchant.objects.get(id=merchant_id)

    customers = Customer.objects.filter(
        merchant=merchant
    )

    customer_count = customers.count()

    credits = CreditTransaction.objects.filter(
        customer__merchant=merchant
    )

    payments = Payment.objects.filter(
        customer__merchant=merchant
    )

    total_credit = sum(
        float(i.amount) for i in credits
    )

    total_payment = sum(
        float(i.amount) for i in payments
    )

    outstanding = total_credit - total_payment

    recent_credits = credits.order_by(
        '-id'
    )[:5]

    context = {

        'merchant': merchant,

        'customer_count': customer_count,

        'total_credit': total_credit,

        'total_payment': total_payment,

        'outstanding': outstanding,

        'recent_credits': recent_credits

    }

    return render(request,
    'merchant/dashboard.html',
    context)


def logout_view(request):

    if 'merchant_id' in request.session:

        del request.session['merchant_id']

    return redirect('/login/')


def admin_login(request):

    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

            request.session['admin'] = username

            return redirect('/admin-dashboard/')

        else:

            messages.error(request,
            "Invalid Admin Credentials")

            return redirect('/admin-login/')

    return render(request,
    'admin/admin_login.html')


def admin_dashboard(request):

    if not request.session.get('admin'):

        return redirect('/admin-login/')

    total_merchants = Merchant.objects.count()

    pending_merchants = Merchant.objects.filter(
        status='Pending'
    ).count()

    approved_merchants = Merchant.objects.filter(
        status='Approved'
    ).count()

    context = {

        'total_merchants': total_merchants,
        'pending_merchants': pending_merchants,
        'approved_merchants': approved_merchants

    }

    return render(request,
    'admin/dashboard.html',
    context)

def merchant_requests(request):

    if not request.session.get('admin'):

        return redirect('/admin-login/')

    merchants = Merchant.objects.all()

    return render(request,
    'admin/merchant_requests.html',
    {'merchants': merchants})

def approve_merchant(request, id):

    if not request.session.get('admin'):

        return redirect('/admin-login/')

    merchant = Merchant.objects.get(id=id)

    merchant.status = "Approved"

    merchant.save()

    return redirect('/merchant-requests/')


def reject_merchant(request, id):

    if not request.session.get('admin'):

        return redirect('/admin-login/')

    merchant = Merchant.objects.get(id=id)

    merchant.status = "Rejected"

    merchant.save()

    return redirect('/merchant-requests/')


def admin_logout(request):

    if 'admin' in request.session:

        del request.session['admin']

    return redirect('/admin-login/')


def add_customer(request):

    merchant_id = request.session.get('merchant_id')

    if not merchant_id:

        return redirect('/login/')

    merchant = Merchant.objects.get(id=merchant_id)

    if request.method == "POST":

        customer_name = request.POST.get('customer_name')

        phone = request.POST.get('phone')

        notes = request.POST.get('notes')

        file = request.FILES.get('file')

        Customer.objects.create(

            merchant=merchant,
            customer_name=customer_name,
            phone=phone,
            notes=notes,
            file=file

        )

        return redirect('/customers/')

    return render(request,
    'merchant/add_customer.html')


def customers(request):

    merchant_id = request.session.get('merchant_id')

    if not merchant_id:

        return redirect('/login/')

    search = request.GET.get('search')

    customer_list = Customer.objects.filter(
        merchant_id=merchant_id
    )

    if search:

        customer_list = customer_list.filter(
            customer_name__icontains=search
        )

    context = {

        'customers': customer_list

    }

    return render(request,
    'merchant/customers.html',
    context)


def edit_customer(request, id):

    merchant_id = request.session.get('merchant_id')

    if not merchant_id:

        return redirect('/login/')

    customer = Customer.objects.get(id=id)

    if request.method == "POST":

        customer.customer_name = request.POST.get(
            'customer_name'
        )

        customer.phone = request.POST.get(
            'phone'
        )

        customer.notes = request.POST.get(
            'notes'
        )

        if request.FILES.get('file'):

            customer.file = request.FILES.get('file')

        customer.save()

        return redirect('/customers/')

    return render(request,
    'merchant/edit_customer.html',
    {'customer': customer})


def delete_customer(request, id):

    merchant_id = request.session.get('merchant_id')

    if not merchant_id:

        return redirect('/login/')

    customer = Customer.objects.get(id=id)

    customer.delete()

    return redirect('/customers/')



def add_credit(request, id):

    merchant_id = request.session.get('merchant_id')

    if not merchant_id:

        return redirect('/login/')

    customer = Customer.objects.get(id=id)

    if request.method == "POST":

        amount = request.POST.get('amount')

        note = request.POST.get('note')

        file = request.FILES.get('file')

        CreditTransaction.objects.create(

            customer=customer,
            amount=amount,
            note=note,
            file=file

        )


        Notification.objects.create(
            merchant=customer.merchant,
            message=f'New credit of ₹ {amount} added for {customer.customer_name}'

)

        return redirect(f'/ledger/{id}/')

    return render(request,
    'merchant/add_credit.html')


def add_payment(request, id):

    merchant_id = request.session.get('merchant_id')

    if not merchant_id:

        return redirect('/login/')

    customer = Customer.objects.get(id=id)

    if request.method == "POST":

        amount = request.POST.get('amount')

        note = request.POST.get('note')

        Payment.objects.create(

            customer=customer,
            amount=amount,
            note=note

        )

        Notification.objects.create(
            merchant=customer.merchant,
            message=f'Payment of ₹ {amount} received from {customer.customer_name}'

)

        return redirect(f'/ledger/{id}/')

    return render(request,
    'merchant/add_payment.html')


def ledger(request, id):

    merchant_id = request.session.get('merchant_id')

    if not merchant_id:

        return redirect('/login/')

    customer = Customer.objects.get(id=id)

    credits = CreditTransaction.objects.filter(
        customer=customer
    )

    payments = Payment.objects.filter(
        customer=customer
    )

    total_credit = sum(
        float(i.amount) for i in credits
    )

    total_payment = sum(
        float(i.amount) for i in payments
    )

    outstanding = total_credit - total_payment

    context = {

        'customer': customer,
        'credits': credits,
        'payments': payments,
        'total_credit': total_credit,
        'total_payment': total_payment,
        'outstanding': outstanding

    }

    return render(request,
    'merchant/ledger.html',
    context)


def export_pdf(request, id):

    merchant_id = request.session.get(
        'merchant_id'
    )

    if not merchant_id:

        return redirect('/login/')

    customer = Customer.objects.get(id=id)

    credits = CreditTransaction.objects.filter(
        customer=customer
    )

    payments = Payment.objects.filter(
        customer=customer
    )

    total_credit = sum(
        float(i.amount) for i in credits
    )

    total_payment = sum(
        float(i.amount) for i in payments
    )

    outstanding = total_credit - total_payment

    context = {

        'customer': customer,

        'credits': credits,

        'payments': payments,

        'total_credit': total_credit,

        'total_payment': total_payment,

        'outstanding': outstanding

    }

    return render_to_pdf(
        'merchant/ledger_pdf.html',
        context
    )


def notifications(request):

    merchant_id = request.session.get(
        'merchant_id'
    )

    if not merchant_id:

        return redirect('/login/')

    data = Notification.objects.filter(
        merchant_id=merchant_id
    ).order_by('-id')

    return render(
        request,
        'merchant/notifications.html',
        {'notifications': data}
    )



def search_customer(request):

    merchant_id = request.session.get(
        'merchant_id'
    )

    if not merchant_id:

        return JsonResponse([], safe=False)

    keyword = request.GET.get('keyword')

    customers = Customer.objects.filter(
        merchant_id=merchant_id,
        customer_name__icontains=keyword
    )

    data = []

    for i in customers:

        data.append({

            'id': i.id,
            'name': i.customer_name,
            'phone': i.phone

        })

    return JsonResponse(data, safe=False)