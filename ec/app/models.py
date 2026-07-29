from django.db import models
from django.contrib.auth.models import User


# Create your models here.
CATEGORY_CHOICES=(
    ('Bd', 'Bed'),
    ('Sf', 'Sofa'),
    ('Dt', 'Dinning table'),
    ('Bs','Bookshelf'),
    ('Ct', 'Coffee table'),
    ('Dk', 'Desk'),
    ('Mr', 'Mirrors'),
    ('Vs', 'Vases'),
    ('fl', 'floor lamps'),
    
)
    
class Product(models.Model):
    title = models.CharField(max_length=100)
    selling_price= models.FloatField()
    discounted_price = models.FloatField()
    description = models.TextField()
    composition = models.TextField(default='')
    prodapp= models.TextField(default='')
    category = models. CharField (choices=CATEGORY_CHOICES,max_length=2)
    product_image = models. ImageField(upload_to= 'product')
    def __str__(self):
        return self.title

class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    locality = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    mobile = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.locality} - {self.city}"
    
class Cart(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_cost(self):
         return self.quantity * self.product.discounted_price 
          

class OrderPlaced(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    ordered_date = models.DateTimeField()

    def __str__(self):
        return str(self.id)          
    

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"    
    




     

     





