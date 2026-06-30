from django.db import models
from category.models import Category
from taggit.managers import TaggableManager
from .managers import ProductManager
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
from django.contrib.contenttypes.fields import GenericRelation
from django.conf import settings
import uuid
from django.utils import timezone


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

    is_digital = models.BooleanField(default=False)
    digital_fulfillment_type = models.CharField(
        max_length=15,
        choices=[
            ('INSTANT', 'Instant Auto-Fulfillment ｜ 隨選即發'),
            ('CUSTOM', 'Custom / Manual Processing ｜ 人工交付'),
        ],
        default='INSTANT'
    )

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

    # 🌟 NEW: Private path pointer inside your secure local filesystem storage root
    # Target location example: settings.BASE_DIR / 'private_digital_vault' / 'ebook1.pdf'
    digital_file_path = models.CharField(max_length=255, blank=True, null=True)
    
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
        # 1. Cleanly extract and fallback text strings from parent relation rows safely
        product_name = str(self.product.product_name).strip() if self.product else ""
        
        # 🌟 THE NET FIX: Pull the inner string property (.color_name) BEFORE evaluating the string exclusions!
        color_val = str(self.color.color_name).strip() if self.color else ""
        size_val = str(self.size.size_name).strip() if self.size else ""
        type_val = str(self.type.type_name).strip() if self.type else ""

        # 2. Establish a strict exclusion blacklist matrix map array
        exclusion_blacklist = ["", "NONE", "N/A", "N/A｜不適用", "N/A ｜ 不適用"]

        # 3. Surgically apply condition filters to wipe out matching string artifacts
        color_name = color_val if color_val not in exclusion_blacklist else ""
        size_name = size_val if size_val not in exclusion_blacklist else ""
        type_name = type_val if type_val not in exclusion_blacklist else ""

        # 4. Pack, clean, and join your structured string attributes
        sku_parts = [product_name, size_name, color_name, type_name]
        filtered_sku = [part for part in sku_parts if part.strip()]
        
        return " - ".join(filtered_sku) or f"Variation #{self.pk}"
        
    def get_sku(self):
        """
        Generates a clean, compact SKU identification string by filtering out
        empty values, placeholder objects, and 'N/A' language tags.
        """
        # 1. Safely extract the inner string values from the foreign relations
        color_val = str(self.color.color_name).strip() if self.color else ""
        size_val = str(self.size.size_name).strip() if self.size else ""
        type_val = str(self.type.type_name).strip() if self.type else ""

        # 2. Establish our comprehensive exclusion blacklist matrix
        exclusion_blacklist = ["", "NONE", "N/A", "N/A｜不適用", "N/A ｜ 不適用"]

        # 3. Filter the values against the blacklist
        color_name = color_val if color_val not in exclusion_blacklist else ""
        size_name = size_val if size_val not in exclusion_blacklist else ""
        type_name = type_val if type_val not in exclusion_blacklist else ""

        # 4. Gather, clean, and join your structured parameters
        sku_parts = [size_name, color_name, type_name]
        filtered_sku = [part for part in sku_parts if part.strip()]
        
        return "-".join(filtered_sku) or f"SKU-VAR-{self.pk}"


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


class DigitalDownloadToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="digital_tokens")
    order_product = models.ForeignKey('orders.OrderProduct', on_delete=models.CASCADE, related_name="download_tokens")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at or not self.is_active

    def __str__(self):
        # By referencing the properties natively, Python maps them lazily 
        # at runtime without causing any top-level module load clashes!
        return f"Token for Order {self.order_product.order.order_number} - Exp: {self.expires_at}"
        