from django.db import models


class Customer(models.Model):
    customer_name = models.CharField(max_length=500)
    customer_email = models.EmailField()
    customer_password= models.CharField(max_length=100)
    customer_type = models.CharField(max_length=200, default="user")
    

    def __str__(self):
            return self.customer_name

