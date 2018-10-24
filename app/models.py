from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
# Create your models here.

categories = (('Fashion','Fashion'),
              ('Daily Essentials','Daily Essentials'),
              ('Electronics','Electronics'),
              ('Home and Furniture','Home and Furniture'),
              ('Books','Books'))

class Product(models.Model):
    title = models.CharField(max_length=50)
    category = models.CharField(max_length=100, choices=categories, default="Goods")
    description = models.CharField(max_length=1000, blank=False)
    price = models.IntegerField()
    quantity = models.IntegerField(null=True)
    image = models.FileField(upload_to="./static/images/",null=True, blank=True)

    def __str__(self):
        return self.title

class Review(models.Model):
    product = models.ForeignKey("app.Product", related_name="reviews", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=False)
    rating = models.IntegerField()
    review = models.CharField(max_length=250)
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.review

    class Meta():
        ordering = ['-date_created']

class Cart(models.Model):
    product = models.ForeignKey("app.Product", related_name="cart", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=False)

    def __str__(self):
        return self.user.username

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=250, null=True, blank=True)
    email = models.EmailField(null=True)
    fname = models.CharField(max_length=50)
    lname = models.CharField(max_length=50)

    def __str__(self):
        return self.fname + ' ' + self.lname
