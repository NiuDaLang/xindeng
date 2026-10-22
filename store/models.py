# sotre.models.py
from django.db import models
from django.db.models import Q
from category.models import Category
from taggit_selectize.managers import TaggableManager
from .managers import ProductManager
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
from django.contrib.contenttypes.fields import GenericRelation
from django.conf import settings
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
import uuid
import decimal
from django.core.exceptions import ValidationError
from accounts.utils import get_real_admin_url
from django.utils.text import slugify


# Create your models here.
# Model for global color options
class Color(models.Model):
    color_name      = models.CharField(max_length=50, unique=True, blank=True)

    def __str__(self):
        return self.color_name

    @property
    def clean_color(self):
        if not self.color_name or self.color_name in ["N/A", "不適用", "N/A｜不適用"]:
            return "--"
        return self.color_name
    

# Model for global size options
class Size(models.Model):
    size_name       = models.CharField(max_length=50, unique=True, blank=True)
    dimensions      = models.CharField(max_length=100, blank=True)
    weight          = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.size_name

    @property
    def clean_size(self):
        if not self.size_name or self.size_name in ["N/A", "不適用", "N/A｜不適用"]:
            return "--"
        return self.size_name
    

# Model for global type options
class Type(models.Model):
    type_name       = models.CharField(max_length=100, unique=True, blank=True)

    def __str__(self):
        return self.type_name

    @property
    def clean_type(self):
        if not self.type_name or self.type_name in ["N/A", "不適用", "N/A｜不適用"]:
            return "--"
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
PRODUCT_STATUS_CHOICES = (
    ("Draft",       "Draft｜草稿"),
    ("Pending",     "Pending Review｜待審核"),
    ("Published",   "Published｜已發布"),
    ("Rejected",    "Rejected｜未通過"),
    ("Unpublished", "Unpublished｜已下架"),
)
ACTION_CHOICES = (
    ("submitted", "Submitted for Review｜提交審核"),
    ("approved",  "Approved｜審核通過"),
    ("rejected",  "Rejected｜審核未通過"),
    ("withdrawn", "Withdrawn｜作者撤回"),
    ("published", "Published Directly｜直接發布"),
    ("unpublished", "Unpublished｜下架"),
    ("deactivation_requested", "Deactivation Requested｜申請下架"),
    ("deletion_approved", "Deletion Approved｜已核准下架"),
    ("deletion_rejected", "Deletion Declined｜下架請求被拒"),
    ("deleted_by_author", "Deleted by Author｜作者刪除"),
)


class Product(models.Model):
    # Note: uniqueness for product_name and slug is enforced conditionally
    # via Meta.constraints (only among is_deleted=False rows). This lets
    # artisans re-use the name/slug of a soft-deleted product.
    product_name    = models.CharField(max_length=255)
    slug            = models.SlugField(allow_unicode=True, blank=True)
    # product_name    = models.CharField(max_length=255, unique=True)
    # slug            = models.SlugField(unique=True, allow_unicode=True)
    description     = models.TextField(max_length=500, blank=True)
    details         = CKEditor5Field(config_name='extends', blank=True, null=True)
    brand           = models.CharField(max_length=255, blank=True)
    creator         = models.ForeignKey(
                        'creators.CreatorProfile',
                        on_delete=models.SET_NULL,       # If artisan leaves, product survives
                        null=True,
                        blank=True,                       # Platform-owned products allowed
                        related_name='products',
                        help_text="The artisan responsible for this piece. Leave blank for platform-owned items."
                      )
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

    is_digital      = models.BooleanField(default=False)
    digital_fulfillment_type = models.CharField(
        max_length=15,
        choices=[
            ('INSTANT', 'Instant Auto-Fulfillment｜隨選即發'),
            ('CUSTOM', 'Custom / Manual Processing｜人工交付'),
        ],
        default='INSTANT'
    )

    craft_types     = models.ManyToManyField('creators.CraftType', blank=True, related_name='products', help_text="Craft disciplines this specific object belongs to.",)
    is_active       = models.BooleanField(default=True)
    created_date    = models.DateTimeField(auto_now_add=True)
    modified_date   = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True, help_text="Last time this product was submitted for review.")

    tags            = TaggableManager(blank=True)

    products        = ProductManager()
    objects         = models.Manager()

    comments        = GenericRelation('reviews.Comment', related_query_name='product')
    status          = models.CharField(max_length=20, choices=PRODUCT_STATUS_CHOICES, default="Draft")
    is_deleted      = models.BooleanField(default=False, help_text="Soft delete flag. Deleted products are hidden from artisan and storefront views but preserved for audit.")

    class Meta:
        indexes = [
            models.Index(fields=['creator', 'status', 'is_deleted']),
            models.Index(fields=['status', 'submitted_at']),
        ]
        constraints = [
            # Only enforce name/slug uniqueness among ACTIVE (non-deleted) products.
            # Soft-deleted products may share a name/slug with a live product,
            # which lets artisans re-use a name they've previously soft-deleted.
            models.UniqueConstraint(
                fields=['product_name'],
                condition=Q(is_deleted=False),
                name='unique_active_product_name',
            ),
            models.UniqueConstraint(
                fields=['slug'],
                condition=Q(is_deleted=False),
                name='unique_active_product_slug',
            ),
        ]

    def __str__(self):
        return self.product_name
    
    def get_url(self):
        return reverse("product", args=[self.category.slug, self.slug])
    
    def lowest_price(self):
        variations = self.variations.filter(is_available=True)
        prices = [v.price for v in variations]
        if not prices:
            return None
        return min(prices)

    def get_admin_url(self):
        """
        Return the admin-facing detail URL for this product.
        Centralised so we can repoint to a custom review-detail view later
        without touching templates.
        """
        return f"{get_real_admin_url()}store/product/{self.pk}/change/"

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

    @property
    def is_editable_by_artisan(self):
        return self.status in ("Draft", "Rejected", "Unpublished")

    @property
    def is_under_review(self):
        return self.status == "Pending"

    @property
    def latest_review_log(self):
        return self.review_logs.order_by('-created_at').first()

    @property
    def has_pending_deactivation_request(self):
        latest = self.review_logs.order_by('-created_at').first()
        return latest is not None and latest.action == 'deactivation_requested'

    @property
    def pending_vault_upload_count(self):
        """
        Number of ArtisanVaultUpload rows for this product's variations
        that are currently PENDING review.

        This is an AGGREGATE across variations, not a per-variation
        lookup. It is the product-level badge on the products-list page
        and the edit-page header. ProductVariation.pending_vault_upload_count
        is the per-variation sibling, used on the variation cards.

        The two properties serve different audiences and must not be
        collapsed into one: the list page wants "how much work is
        waiting on this product," the variation card wants "which
        specific variation is blocked." Do not "simplify" this into a
        `.first()` or `.exists()` — the aggregate must return the sum
        across variations, and supersession (one PENDING replaced by a
        newer PENDING on the same variation) must not inflate it.
        """
        return self.vault_uploads.filter(status="PENDING").count()
    
    @property
    def image_dimensions(self):
        """Return (width, height) of the hero image, or None."""
        if not self.images:
            return None
        from core.image_utils import get_image_dimensions
        return get_image_dimensions(self.images.name)

    @property
    def is_portrait(self):
        dims = self.image_dimensions
        if not dims:
            return False
        w, h = dims
        return h > w

    @property
    def is_landscape(self):
        dims = self.image_dimensions
        if not dims:
            return False
        w, h = dims
        return w > h

    @property
    def is_square(self):
        dims = self.image_dimensions
        if not dims:
            return False
        w, h = dims
        return w == h

    @property
    def hero_container_style(self):
        """
        Inline style for the hero container.
        
        Returns something like 'aspect-ratio: 1600 / 900;' — matching the
        source image's natural ratio, but clamped to [4/5, 16/9] so no
        single image can distort the layout.
        """
        dims = self.image_dimensions
        if not dims:
            return "aspect-ratio: 4 / 3;"
        
        w, h = dims
        ratio = w / h
        
        # Clamp
        if ratio > 16 / 9:
            return "aspect-ratio: 16 / 9;"
        if ratio < 1 / 2:                   # was 4/5
            return "aspect-ratio: 1 / 2;"
        
        return f"aspect-ratio: {w} / {h};"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.product_name, allow_unicode=True) or "product"
            base = base[:250]
            slug = base
            n = 1
            while Product.objects.filter(slug=slug, is_deleted=False).exclude(pk=self.pk).exists():
                suffix = f"-{n}"
                slug = f"{base[:250 - len(suffix)]}{suffix}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.creator_id and self.is_voucher:
            raise ValidationError({
                "is_voucher": "Artisans cannot create voucher products. Vouchers are platform-level."
            })

        # Conditional uniqueness for product_name (mirrors the DB constraint).
        if self.product_name:
            qs = Product.objects.filter(product_name=self.product_name, is_deleted=False)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError({
                    "product_name": "此作品名稱已被使用。｜This product name is already in use."
                })

        # Conditional uniqueness for slug (mirrors the DB constraint).
        if self.slug:
            qs = Product.objects.filter(slug=self.slug, is_deleted=False)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError({
                    "slug": "此網址代稱已被使用。｜This URL slug is already in use."
                })


class ProductVariation(models.Model):
    product         = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    color           = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)
    size            = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True)
    type            = models.ForeignKey(Type, on_delete=models.SET_NULL, null=True)
    pending_color   = models.CharField(max_length=50, blank=True, default="")
    pending_size    = models.CharField(max_length=100, blank=True, default="")
    pending_type    = models.CharField(max_length=100, blank=True, default="")
    images          = models.ImageField(upload_to='images/products/variations', null=True, blank=True)
    stock           = models.PositiveIntegerField(default=0)
    is_available    = models.BooleanField(default=True)
    price           = models.DecimalField(max_digits=10, decimal_places=2) # Use DecimalField for money
    original_price  = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True) # Use DecimalField for money

    cancellation_fee_pct = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=decimal.Decimal('0.00'),
        validators=[MinValueValidator(0), MaxValueValidator(90)]
    )

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

    @property
    def image_dimensions(self):
        if not self.images:
            return None
        from core.image_utils import get_image_dimensions
        return get_image_dimensions(self.images.name)

    @property
    def is_portrait(self):
        dims = self.image_dimensions
        return bool(dims and dims[1] > dims[0])

    @property
    def is_landscape(self):
        dims = self.image_dimensions
        return bool(dims and dims[0] > dims[1])

    @property
    def hero_container_style(self):
        """
        Inline style for the hero container.
        
        Returns something like 'aspect-ratio: 1600 / 900;' — matching the
        source image's natural ratio, but clamped to [4/5, 16/9] so no
        single image can distort the layout.
        """
        dims = self.image_dimensions
        if not dims:
            return "aspect-ratio: 4 / 3;"
        
        w, h = dims
        ratio = w / h
        
        # Clamp
        if ratio > 16 / 9:
            return "aspect-ratio: 16 / 9;"
        if ratio < 1 / 2:                   # was 4/5
            return "aspect-ratio: 1 / 2;"
        
        return f"aspect-ratio: {w} / {h};"

    @property
    def pending_vault_upload_count(self):
        """
        Number of ArtisanVaultUpload rows for this variation that are
        currently PENDING review.

        The partial unique constraint (unique_pending_upload_per_variation)
        caps this at 1, but it is exposed as a count rather than a bool
        so the template can render it as a counter badge directly, and
        so relaxing the constraint later does not silently change the
        UI contract.
        """
        return self.vault_uploads.filter(status="PENDING").count()

    def latest_terminal_vault_upload(self):
        """
        The most recent terminal (APPROVED or REJECTED) upload for this
        variation.

        Sort key is (-reviewed_at, -submitted_at).

        reviewed_at is the primary sort because it is the wall-clock
        time of the admin's decision — the semantically correct answer
        to "which terminal state is current". submitted_at is the
        secondary sort for the pathological case where two decisions
        share a reviewed_at (essentially impossible for human-admin
        actions, but cheap as a tiebreaker).

        Why not -pk: ArtisanVaultUpload.pk is a UUIDField, not an
        auto-increment integer. UUID4 ordering is random, so -pk would
        not order by insertion. See the test class
        TestLatestTerminalVaultUpload for the collision test that
        caught this.

        Legacy rows with null reviewed_at sort last under -reviewed_at
        in SQLite (NULL < any value, so DESC places NULL last), which
        is the desired behaviour: a reviewed decision beats an
        unreviewed terminal row.

        Returns None when this variation has never had a terminal upload
        (e.g. still PENDING, or superseded before review).
        """
        return (
            self.vault_uploads
            .filter(status__in=["APPROVED", "REJECTED"])
            .order_by("-reviewed_at", "-submitted_at")
            .first()
        )

    @property
    def is_instant_eproduct(self):
        """
        True for instant-fulfilment digital products that are not
        vouchers. These behave as effectively infinite stock: save()
        forces stock=1, every customer sees the same figure, and
        purchasing never decrements the column.

        Centralised here so the four call sites that need the same
        three-condition check — save(), the storefront availability
        loop, and the two cart views — can't drift.
        """
        return (
            self.product.is_digital
            and self.product.digital_fulfillment_type == "INSTANT"
            and not self.product.is_voucher
        )

    def compute_available_stock(self, quantity_in_cart=0):
        """
        Cart-aware availability figure for the storefront display.

        For most lines this is stock minus the user's own cart
        quantity — a partial reservation, so a visitor can't
        double-buy the last unit. For instant-digital products,
        subtraction would make the variation appear out of stock the
        moment it's added to the cart, which is wrong: stock is a
        storefront-wide availability figure and every purchase is
        fulfilled independently. Skip the subtraction there.
        """
        if self.is_instant_eproduct:
            return self.stock
        return max(0, self.stock - quantity_in_cart)
    

    def __str__(self):
        # 1. Cleanly extract and fallback text strings from parent relation rows safely
        product_name = str(self.product.product_name).strip() if self.product else ""
        
        # 🌟 THE NET FIX: Pull the inner string property (.color_name) BEFORE evaluating the string exclusions!
        color_val = str(self.color.color_name).strip() if self.color else ""
        size_val = str(self.size.size_name).strip() if self.size else ""
        type_val = str(self.type.type_name).strip() if self.type else ""

        # 2. Establish a strict exclusion blacklist matrix map array
        exclusion_blacklist = ["", "NONE", "N/A", "N/A｜不適用", "N/A｜不適用"]

        # 3. Surgically apply condition filters to wipe out matching string artifacts
        color_name = color_val if color_val not in exclusion_blacklist else ""
        size_name = size_val if size_val not in exclusion_blacklist else ""
        type_name = type_val if type_val not in exclusion_blacklist else ""

        # 4. Pack, clean, and join your structured string attributes
        sku_parts = [product_name, size_name, color_name, type_name]
        filtered_sku = [part for part in sku_parts if part.strip()]
        
        return " - ".join(filtered_sku) or f"Variation #{self.pk}"
        
    def get_sku(self):
        # Prefer FK value; fall back to pending; else empty
        color_val = str(self.color.color_name).strip() if self.color else self.pending_color.strip()
        size_val = str(self.size.size_name).strip() if self.size else self.pending_size.strip()
        type_val = str(self.type.type_name).strip() if self.type else self.pending_type.strip()

        exclusion_blacklist = ["", "NONE", "N/A", "N/A｜不適用"]

        color_name = color_val if color_val not in exclusion_blacklist else ""
        size_name = size_val if size_val not in exclusion_blacklist else ""
        type_name = type_val if type_val not in exclusion_blacklist else ""

        sku_parts = [size_name, color_name, type_name]
        filtered = [p for p in sku_parts if p.strip()]

        return "-".join(filtered) or f"SKU-VAR-{self.pk}"

    def save(self, *args, **kwargs):
        """
        Database-Level Infinite Asset Enforcement.
        Forces instant e-products to maintain a static inventory balance of 1,
        making them immune to accidental human edits or workflow deductions.
        """
        # 🌟 Check your explicit business rule condition safely at runtime
        if self.is_instant_eproduct:
            self.stock = 1
            self.is_available = True
           
            # If your save call specifies 'update_fields', make sure 'stock' and 'is_available' are included
            if 'update_fields' in kwargs and kwargs['update_fields'] is not None:
                # Convert tuple to list to allow modifications safely
                fields = list(kwargs['update_fields'])
                if 'stock' not in fields:
                    fields.append('stock')
                if 'is_available' not in fields:
                    fields.append('is_available')
                kwargs['update_fields'] = fields

        # Execute standard parent class save routing to write down to SQL engines cleanly
        super().save(*args, **kwargs)


class ProductGallery(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/products/gallery', max_length=255)
    title = models.CharField(max_length=255, blank=True)

    # 🌟 NEW: Gallery curation (for the 匠作 gallery page)
    is_featured_in_gallery = models.BooleanField(
        default=False,
        help_text="Show this image in the 匠作 Artisans Gallery page."
    )
    gallery_caption = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional poetic caption shown in the gallery lightbox."
    )
    gallery_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first. 0 = random order."
    )

    def __str__(self):
        return self.product.product_name
    
    class Meta:
        verbose_name = 'ProductGallery'
        verbose_name_plural = 'Product Gallery'

    @property
    def image_dimensions(self):
        if not self.image:
            return None
        from core.image_utils import get_image_dimensions
        return get_image_dimensions(self.image.name)

    @property
    def is_portrait(self):
        dims = self.image_dimensions
        return bool(dims and dims[1] > dims[0])

    @property
    def is_landscape(self):
        dims = self.image_dimensions
        return bool(dims and dims[0] > dims[1])

    @property
    def hero_container_style(self):
        """
        Inline style for the hero container.
        
        Returns something like 'aspect-ratio: 1600 / 900;' — matching the
        source image's natural ratio, but clamped to [4/5, 16/9] so no
        single image can distort the layout.
        """
        dims = self.image_dimensions
        if not dims:
            return "aspect-ratio: 4 / 3;"
        
        w, h = dims
        ratio = w / h
        
        # Clamp
        if ratio > 16 / 9:
            return "aspect-ratio: 16 / 9;"
        if ratio < 1 / 2:                   # was 4/5
            return "aspect-ratio: 1 / 2;"
        
        return f"aspect-ratio: {w} / {h};"
    

class ProductVariationGallery(models.Model):
    product_variation = models.ForeignKey(ProductVariation, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/products/variations/gallery', max_length=255)
    title = models.CharField(max_length=255, blank=True)


    def __str__(self):
        return self.product_variation.get_sku()
    
    class Meta:
        verbose_name = 'ProductVariationGallery'
        verbose_name_plural = 'ProductVariation Gallery'

    @property
    def image_dimensions(self):
        if not self.image:
            return None
        from core.image_utils import get_image_dimensions
        return get_image_dimensions(self.image.name)

    @property
    def is_portrait(self):
        dims = self.image_dimensions
        return bool(dims and dims[1] > dims[0])

    @property
    def is_landscape(self):
        dims = self.image_dimensions
        return bool(dims and dims[0] > dims[1])

    @property
    def hero_container_style(self):
        """
        Inline style for the hero container.
        
        Returns something like 'aspect-ratio: 1600 / 900;' — matching the
        source image's natural ratio, but clamped to [4/5, 16/9] so no
        single image can distort the layout.
        """
        dims = self.image_dimensions
        if not dims:
            return "aspect-ratio: 4 / 3;"
        
        w, h = dims
        ratio = w / h
        
        # Clamp
        if ratio > 16 / 9:
            return "aspect-ratio: 16 / 9;"
        if ratio < 1 / 2:                   # was 4/5
            return "aspect-ratio: 1 / 2;"
        
        return f"aspect-ratio: {w} / {h};"


class DigitalDownloadToken(models.Model):
    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="digital_tokens",
    )

    # Email snapshot, populated at token creation from order.email.
    # This is the identity anchor for the guest fallback: it survives
    # any later edit to the parent order, so a change to order.email
    # after the token was issued cannot widen or narrow access.
    # Empty string only when the parent order had no email recorded —
    # checkout requires one, but the field is defensive.
    email           = models.EmailField(blank=True, default="")

    order_product   = models.ForeignKey(
                        'orders.OrderProduct',
                        on_delete=models.CASCADE,
                        related_name="download_tokens",
                    )
    created_at      = models.DateTimeField(auto_now_add=True)
    expires_at      = models.DateTimeField()
    is_active       = models.BooleanField(default=True)

    @property
    def is_revoked(self):
        return not self.is_active

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_revoked_or_expired(self):
        return self.is_revoked or self.is_expired

    def __str__(self):
        # By referencing the properties natively, Python maps them lazily 
        # at runtime without causing any top-level module load clashes!
        return f"Token for Order {self.order_product.order.order_number} - Exp: {self.expires_at}"


class ProductReviewLog(models.Model):
    product         = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='review_logs')
    action          = models.CharField(max_length=30, choices=ACTION_CHOICES)
    actor           = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,related_name='product_review_actions')
    note            = models.TextField(blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Product Review Log'
        verbose_name_plural = 'Product Review Logs'

    def __str__(self):
        return f"{self.product.product_name} — {self.get_action_display()} @ {self.created_at:%Y-%m-%d %H:%M}"


class ArtisanVaultUpload(models.Model):
    """
    A staged digital file awaiting admin review before it becomes the
    authoritative asset for a ProductVariation.

    Lifecycle:
      1. Artisan uploads via the creators dashboard. Row created with
         storage_kind=LOCAL and staged_filename pointing at a file in
         private_digital_vault/_pending/. Server computes sha256.
         OR
         Artisan pastes a cloud-drive URL. Row created with
         storage_kind=EXTERNAL_PENDING, external_url set, checksum
         optionally filled from the artisan's paste.
      2. For EXTERNAL_PENDING, an admin downloads the file manually
         and stages it into _pending/, flipping storage_kind to
         LOCAL_PENDING and computing the checksum locally. If the
         artisan supplied a checksum and it disagrees with the
         server-computed one, the staging view refuses to proceed.
      3. Admin approves or rejects.
         Approve: file moves out of _pending/ into the vault root and
         ProductVariation.digital_file_path is updated. Status set to
         APPROVED.
         Reject: staged file (if any) is deleted. Status set to
         REJECTED with review_note explaining why.
         Approve (order-product-scoped): file moves out of _pending/ into
         the vault root, OrderProduct.digital_file_path is updated, and
         issue_download_token is called on the order-product. Status set to
         APPROVED. This is the CUSTOM delivery path; see the CUSTOM pipeline
         v2 handoff.

    Uniqueness invariant: at most one PENDING upload may exist per
    target, where "target" is the variation for variation-scoped rows
    and the order_product for order-product-scoped rows. Enforced by
    two partial unique constraints whose conditions partition the
    PENDING-row space:

      * unique_pending_upload_per_variation
        Fields: variation
        Condition: order_product__isnull=True, status='PENDING'
        Applies to: the INSTANT path and legacy variation-scoped
          uploads (rows whose order_product is NULL).
        The order_product__isnull=True condition is load-bearing.
        Without it, the constraint would also cover order-product-
        scoped rows and cap PENDING uploads at one per variation —
        which breaks the CUSTOM pipeline, because a single variation
        legitimately hosts many CUSTOM order lines, each with its own
        PENDING upload.

      * unique_pending_upload_per_order_product
        Fields: order_product
        Condition: order_product__isnull=False, status='PENDING'
        Applies to: the CUSTOM path (rows whose order_product is set).
        The order_product__isnull=False condition is the mirror guard.
        Without it, the constraint would attempt uniqueness enforcement
        on the NULL values that variation-scoped rows carry, which is
        not the intent.

    The two conditions are complementary, not redundant. Do not remove
    either "for simplicity" — doing so either breaks CUSTOM delivery
    (removing the isnull=True guard) or adds unintended uniqueness
    pressure on the INSTANT path (removing the isnull=False guard).

    Supersession — an artisan uploading again while a previous upload
    for the same target is still PENDING — is handled at the view
    layer: the previous row is flipped to SUPERSEDED and the new row
    is created. The supersession query branches on the same target-
    scoping the constraints use; see
    creators.views.self_supersede_and_create.
    """

    STORAGE_KIND_CHOICES = [
        ("LOCAL", "Direct upload to vault staging"),
        ("EXTERNAL_PENDING", "Cloud drive link awaiting admin copy"),
        ("LOCAL_PENDING", "Cloud drive file staged locally"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending review"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected by admin"),
        ("SUPERSEDED", "Superseded by newer upload"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # ── Ownership and target ──────────────────────────────────────
    artisan = models.ForeignKey(
        'creators.CreatorProfile',
        on_delete=models.CASCADE,
        related_name='vault_uploads',
    )
    product = models.ForeignKey(
        'store.Product',
        on_delete=models.CASCADE,
        related_name='vault_uploads',
    )
    variation = models.ForeignKey(
        'store.ProductVariation',
        on_delete=models.CASCADE,
        related_name='vault_uploads',
    )
    order_product = models.ForeignKey(
        'orders.OrderProduct',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vault_uploads',
        help_text=(
            "Set for CUSTOM order-product-scoped uploads. The approve view "
            "writes OrderProduct.digital_file_path when this is set, and "
            "ProductVariation.digital_file_path otherwise. SET_NULL, not "
            "CASCADE — a staged file is the artisan's submitted work, not "
            "the parent's property, so it must survive an OrderProduct "
            "deletion (order cancelled, line replaced). See the sweeper "
            "backlog item for eventual cleanup."
        ),
    )
    # ── File metadata ─────────────────────────────────────────────
    # staged_filename is a path relative to XINDENG_VAULT_ROOT/_pending/,
    # e.g. "4b1d3c2a-....pdf". Blank when storage_kind=EXTERNAL_PENDING
    # and the admin has not yet copied the file in.
    staged_filename = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text=(
            "Path relative to XINDENG_VAULT_ROOT/_pending/ for LOCAL "
            "and LOCAL_PENDING uploads."
        ),
    )
    original_filename = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text=(
            "The filename the artisan submitted. Preserved for display "
            "in the review queue and in download headers."
        ),
    )
    file_size = models.PositiveBigIntegerField(
        default=0,
        help_text="Bytes. Zero means unknown (EXTERNAL_PENDING pre-copy).",
    )
    checksum = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text=(
            "Hex checksum of the file bytes. For LOCAL and LOCAL_PENDING, "
            "server-computed SHA-256. For EXTERNAL_PENDING, the artisan-"
            "supplied value (may be blank)."
        ),
    )

    # ── External transit ──────────────────────────────────────────
    external_url = models.URLField(
        max_length=500,
        blank=True,
        default="",
        help_text=(
            "Cloud drive URL provided by the artisan. Only populated for "
            "EXTERNAL_PENDING rows; kept after staging for audit."
        ),
    )

    # ── State ─────────────────────────────────────────────────────
    storage_kind = models.CharField(
        max_length=20,
        choices=STORAGE_KIND_CHOICES,
        default="LOCAL",
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING",
    )

    # ── Review metadata ───────────────────────────────────────────
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vault_uploads_reviewed',
    )
    review_note = models.TextField(
        blank=True,
        default="",
        help_text="Set on rejection; also set on supersession for audit.",
    )

    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['status', 'submitted_at']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['variation'],
                condition=Q(order_product__isnull=True, status='PENDING'),
                name='unique_pending_upload_per_variation',
            ),
            models.UniqueConstraint(
                fields=['order_product'],
                condition=Q(order_product__isnull=False, status='PENDING'),
                name='unique_pending_upload_per_order_product',
            ),
        ]

    def __str__(self):
        label = (
            self.original_filename
            or self.staged_filename
            or f"upload {str(self.id)[:8]}"
        )
        return f"{label} for {self.product.product_name} — {self.status}"


class VaultUploadReviewLog(models.Model):
    """
    Audit trail for reviewer actions on ArtisanVaultUpload rows.

    Only reviewer actions are logged here (approve, reject, supersede).
    Submission is recorded by the ArtisanVaultUpload row itself
    (submitted_at, status='PENDING'), so we do not duplicate it.

    Kept separate from ProductReviewLog because the two logs have
    different audiences and different lifecycle semantics: product
    reviews belong to the product, vault reviews belong to a specific
    staged file that may be superseded many times over the life of a
    single variation.
    """

    ACTION_CHOICES = [
        ("approved", "Approved｜審核通過"),
        ("rejected", "Rejected｜審核未通過"),
        ("superseded", "Superseded by newer upload｜已被新上傳取代"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    upload = models.ForeignKey(
        'store.ArtisanVaultUpload',
        on_delete=models.CASCADE,
        related_name='review_logs',
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='vault_upload_reviews',
    )
    note = models.TextField(
        blank=True,
        default="",
        help_text="Reason for rejection, or context for supersession.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Vault upload review log'
        verbose_name_plural = 'Vault upload review logs'

    def __str__(self):
        who = self.actor.username if self.actor else "system"
        return f"{self.action} by {who} on {str(self.upload.id)[:8]}"