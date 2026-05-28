from django.db import models

# Create your models here.
from django.db import models


class Merchant(models.Model):
    name = models.CharField(max_length=150)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    business_name = models.CharField(max_length=150)
    password = models.CharField(max_length=100)   # plain text
    status = models.CharField(max_length=20, default='Pending')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Customer(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)
    notes = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='customers/', blank=True, null=True)

    def __str__(self):
        return self.customer_name


class CreditTransaction(models.Model):

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE
    )

    amount = models.FloatField()

    note = models.TextField(
        blank=True,
        null=True
    )

    file = models.FileField(
        upload_to='credits/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

class Payment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.FloatField()
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):

    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE
    )

    message = models.TextField()

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.message