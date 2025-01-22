from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Product(models.Model):
    product_name = models.CharField(max_length=100, null=False)
    product_description = models.CharField(max_length=250)
    product_price = models.IntegerField(null=False)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    posted_on = models.DateTimeField(default=now, editable=False)
    def __str__(self):
        return self.product_name
    
class Chat(models.Model):
    message = models.CharField(max_length=500, null=False)
    sent_by = models.IntegerField(null=False)
    sent_to = models.ForeignKey(User, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    message_timing = models.DateTimeField(default=now, editable=False)
    def __str__(self):
        return self.message