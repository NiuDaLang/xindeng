from django.db import models
from django.urls import reverse


PRODUCT_FORMAT = [
    ("physical", "實物 | physical"),
    ("e-product", "電子產品 | product"),
    ("donation", "捐款 | donation"),
]

# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)
    product_format = models.CharField(blank=True, max_length=20, choices=PRODUCT_FORMAT)
    cat_image = models.ImageField(upload_to='images/categories', blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.category_name
    
    def get_url(self):
        return reverse("products", args=[self.slug])