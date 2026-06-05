from django.db import models
from category.models import Category
from taggit.managers import TaggableManager
from .managers import ProductManager
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
from django.contrib.contenttypes.fields import GenericRelation


# Create your models here.
# Model for global color options
class Color(models.Model):
    color_name      = models.CharField(max_length=50, unique=True, blank=True)

    def __str__(self):
        return self.color_name


# Model for global size options
class Size(models.Model):
    size_name       = models.CharField(max_length=50, unique=True, blank=True)
    dimensions      = models.CharField(max_length=100, blank=True)
    weight          = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.size_name
    

# Model for global type options
class Type(models.Model):
    type_name       = models.CharField(max_length=100, unique=True, blank=True)

    def __str__(self):
        return self.type_name


# Model for the main product details
ORIGIN = [
    ('DEFAULT', '地球|EARTH'),
    ('CHINA', '中國|CHINA'),
    ('AUSTRALIA', '澳大利亞|AUSTRALIA'),
    ('TYPE_OTHER', '其他|Other'),
]
GENDER = [
    ('DEFAULT', '通用|UNISEX'),
    ('MALE', '男款|MALE'),
    ('FEMALE', '女款|FEMALE'),
]
BLOOD = [
    ('DEFAULT', '未指定|UNSPECIFIED'),
    ('A', 'A型|TYPE_A'),
    ('B', 'B型|TYPE_B'),
    ('AB', 'AB型|TYPE_AB'),
    ('O', 'O型|TYPE_O'),
    ('OTHER', '其他|OTHER'),
]
COLOR = [
    ('DEFAULT', '未指定|UNSPECIFIED'),
    ('RED', 'Red｜紅色'),
    ('PINK', 'Pink｜粉紅色'),
    ('ORANGE', 'Orange｜橙色'),
    ('YELLOW', 'Yellow｜黃色'),
    ('PURPLE', 'Purple｜紫色'),
    ('VIOLET', 'Violet｜紫羅蘭色'),
    ('GREEN', 'Green｜綠色'),
    ('BLUE', 'Blue｜藍色'),
    ('BROWN', 'Brown｜褐色'),
    ('GRAY', 'White｜白色'),
    ('GREYBLACK', 'Grey/Black｜灰/黑色'),
]


class Product(models.Model):
    product_name    = models.CharField(max_length=255, unique=True)
    slug            = models.SlugField(unique=True)
    description     = models.TextField(max_length=500, blank=True)
    details         = CKEditor5Field(config_name='extends', blank=True, null=True)
    brand           = models.CharField(max_length=255, blank=True)
    images          = models.ImageField(upload_to='images/products', null=True, blank=True)
    category        = models.ForeignKey(Category, on_delete=models.CASCADE)
    origin          = models.CharField(blank=True, max_length=50, choices=ORIGIN, default='DEFAULT')
    gender          = models.CharField(blank=True, max_length=50, choices=GENDER, default='DEFAULT')
    blood           = models.CharField(blank=True, max_length=50, choices=BLOOD, default='DEFAULT')
    color           = models.CharField(blank=True, max_length=50, choices=COLOR, default='DEFAULT')
    hs_code         = models.CharField(max_length=20, blank=True, null=True, help_text="Harmonized System code for tax/duty (e.g., 9701.10 for paintings)")
    tax_category    = models.CharField(max_length=100, blank=True, null=True, help_text="Internal or third-party tax category (e.g., 'physical_art')")
    is_physical     = models.BooleanField(default=True)
    is_voucher      = models.BooleanField(default=False)

    is_active       = models.BooleanField(default=True)
    created_date    = models.DateTimeField(auto_now_add=True)
    modified_date   = models.DateTimeField(auto_now=True)

    tags = TaggableManager()

    products = ProductManager()
    objects = models.Manager()

    comments = GenericRelation('reviews.Comment', related_query_name='product')

    def __str__(self):
        return self.product_name
    
    def get_url(self):
        return reverse("product", args=[self.category.slug, self.slug])
    
    def lowest_price(self):
        variations = self.variations.filter(is_available=True)
        prices = []
        for variation in variations:
            prices.append(variation.price)       
        return min(prices)

    @property
    def effective_lowest_price(self):
        # If we annotated the queryset (fast), use that
        if hasattr(self, 'min_price'):
            return self.min_price
        # Otherwise, fallback to your existing method (slower, for detail pages)
        return self.lowest_price() 
        
    @property
    def reviews(self):
        return self.comments.exclude(rating__isnull=True) #get only reviews that have a rating
    

class ProductVariation(models.Model):
    product         = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    color           = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)
    size            = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True)
    type            = models.ForeignKey(Type, on_delete=models.SET_NULL, null=True)
    images          = models.ImageField(upload_to='images/products/variations', default="images/products/variations/pattern1.png")
    stock           = models.PositiveIntegerField(default=0)
    is_available    = models.BooleanField(default=True)
    price           = models.DecimalField(max_digits=10, decimal_places=2) # Use DecimalField for money
    original_price  = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True) # Use DecimalField for money

    with_shipping   = models.BooleanField(default=False)
    single_pack     = models.BooleanField(default=False)
    # weight          = models.DecimalField(max_digits=10, decimal_places=3, default=0.000, help_text="Weight in kg (e.g., 1.250)")
    weight          = models.PositiveIntegerField(default=0, help_text="Weight in g (e.g., 800)")
    created_date    = models.DateTimeField(auto_now_add=True)
    modified_date   = models.DateTimeField(auto_now=True)

    class Meta:
        # Enforce uniqueness for the combination of product, color, and size
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'color', 'size', 'type',],
                name='unique_product_variation_constraint'
            )
        ]

    def __str__(self):
        product_name = str(self.product.product_name) if self.product else ""
        color_name = str(self.color.color_name) if self.color else ""
        size_name = str(self.size.size_name) if self.size else ""
        type_name = str(self.type.type_name) if self.type else ""

        sku_parts = [product_name, size_name, color_name, type_name]
        filtered_sku = [part for part in sku_parts if part.strip()]
        return "-".join(filtered_sku) or f"Variation {self.pk}"
        
    def get_sku(self):
        color_name = str(self.color.color_name) if self.color else ""
        size_name = str(self.size.size_name) if self.size else ""
        type_name = str(self.type.type_name) if self.type else ""

        sku = [size_name, color_name, type_name]
        filtered_sku = [str(item) for item in sku if item is not None and str(item).strip() != ""]
        # sku = separator.join(filtered_sku)
        return "-".join(filtered_sku) or f"Variation {self.pk}"


class ProductGallery(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/products/gallery', max_length=255)
    title = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.product.product_name
    
    class Meta:
        verbose_name = 'ProductGallery'
        verbose_name_plural = 'Product Gallery'
    

class ProductVariationGallery(models.Model):
    product_variation = models.ForeignKey(ProductVariation, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/products/variations/gallery', max_length=255)
    title = models.CharField(max_length=255, blank=True)


    def __str__(self):
        return self.product_variation.get_sku()
    
    class Meta:
        verbose_name = 'ProductVariationGallery'
        verbose_name_plural = 'ProductVariation Gallery'
