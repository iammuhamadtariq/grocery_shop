from django.db import models
from .category import Category

class Product(models.Model):
    product_name = models.CharField(max_length=100)
    product_price = models.IntegerField(default=0)
    product_catagory = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    product_description = models.CharField(max_length=250, default='', null=True, blank=True)
    product_image = models.ImageField(upload_to='upload/products/')

    def __str__(self):
            return self.product_name



