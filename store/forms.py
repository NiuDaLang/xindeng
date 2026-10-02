# store/forms.py

from django import forms
from django.utils.text import slugify
from django_ckeditor_5.widgets import CKEditor5Widget
from taggit.models import Tag
from .models import Product, ProductVariation, Color, Size, Type
from core.widgets import CropTargetFileInput


PRODUCT_KIND_CHOICES = [
    ('physical', 'Physical｜實物'),
    ('digital',  'Digital｜電子產品'),
]


class ArtisanProductForm(forms.ModelForm):
    """
    Metadata form for a product. Variations are handled separately via
    dedicated views (add/remove) — this form only edits the product shell.
    """

    product_kind = forms.ChoiceField(
        choices=PRODUCT_KIND_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'radio radio-primary radio-sm'}),
        label="Product Type｜產品類型",
        required=True,
    )

    tags_choices = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="從現有標籤中挑選；如需新增請聯繫後台。"
                  "｜Pick from existing tags. To request a new one, contact the platform.",
    )

    class Meta:
        model = Product
        fields = [
            'product_name',
            'description',
            'details',
            'category',
            'craft_types',
            # 'tags',
            'color',
            'gender',
            'blood',
            'images',
            'digital_fulfillment_type'
        ]
        widgets = {
            'product_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Product title｜作品名稱',
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 3,
                'placeholder': 'Short description shown in listings｜列表用簡介（最多 500 字）',
            }),
            'details': CKEditor5Widget(
                config_name='extends',
                attrs={'class': 'django_ckeditor_5'},
            ),
            'category': forms.Select(attrs={
                'class': 'select select-bordered w-full',
            }),
            'craft_types': forms.CheckboxSelectMultiple,
            'color': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'gender': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'blood': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'images': CropTargetFileInput(),
            'digital_fulfillment_type': forms.Select(attrs={
                'class': 'select select-bordered w-full',
            }),
        }

    def __init__(self, *args, artisan=None, require_image=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.artisan = artisan
        self._require_image = require_image        # ← NEW: set once, here

        # Tag choices: only used tags in the platform
        from taggit.models import TaggedItem
        used_tag_ids = (
            TaggedItem.objects
            .values_list('tag_id', flat=True)
            .distinct()
        )
        self.fields['tags_choices'].queryset = (
            Tag.objects.filter(id__in=used_tag_ids).order_by('name')
        )

        # Pre-select existing tags, Populate product_kind from the instance if editing
        if self.instance and self.instance.pk:
            self.fields['tags_choices'].initial = self.instance.tags.all()
            if self.instance.is_digital and not self.instance.is_physical:
                self.initial['product_kind'] = 'digital'
            else:
                self.initial['product_kind'] = 'physical'

        # Pre-check artisan's craft types on create
        if artisan and not (self.instance and self.instance.pk):
            self.initial.setdefault(
                'craft_types',
                list(artisan.craft_types.values_list('pk', flat=True)),
            )

    def clean(self):
        cleaned = super().clean()
        kind = cleaned.get('product_kind')

        if kind == 'physical':
            cleaned['is_physical'] = True
            cleaned['is_digital'] = False
            cleaned['digital_fulfillment_type'] = 'INSTANT'  # irrelevant; safe default
        elif kind == 'digital':
            cleaned['is_physical'] = False
            cleaned['is_digital'] = True
            # cleaned_data already validated against choices
            cleaned['digital_fulfillment_type'] = cleaned.get(
                'digital_fulfillment_type', 'INSTANT'
            )
        else:
            raise forms.ValidationError("請選擇產品類型｜Please select a product type.")

        return cleaned

    def clean_images(self):
        img = self.cleaned_data.get('images')
        has_existing = bool(self.instance and self.instance.pk and self.instance.images)

        # ── A2: submission-time image requirement ──
        if self._require_image and not img and not has_existing:
            raise forms.ValidationError(
                "提交審核前請先上傳作品主視覺。"
                "｜Featured image is required before submitting for review."
            )

        # ── Existing soft ratio hint (unchanged) ──
        if img:
            try:
                from PIL import Image
                with Image.open(img) as pil_img:
                    w, h = pil_img.size
                    ratio = w / h
                    if ratio < 0.8 or ratio > 2.0:
                        self.hero_ratio_hint = (
                            f"Tip: For best display, use images between "
                            f"4:5 and 16:9 aspect ratio. Yours is {w}×{h}. "
                            f"｜提示：建議使用 4:5 至 16:9 比例的圖片。"
                        )
            except Exception:
                pass
        return img

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.creator = self.artisan
        instance.is_voucher = False
        if not instance.pk:
            instance.status = 'Draft'

        # is_physical / is_digital / digital_fulfillment_type set via clean()
        instance.is_physical = self.cleaned_data.get('is_physical', True)
        instance.is_digital = self.cleaned_data.get('is_digital', False)
        instance.digital_fulfillment_type = self.cleaned_data.get(
            'digital_fulfillment_type', 'INSTANT'
        )

        if commit:
            instance.save()
            self.save_m2m()
            # Tags are set explicitly (not a model field)
            if 'tags_choices' in self.cleaned_data:
                instance.tags.set(self.cleaned_data['tags_choices'])
        return instance

    # def clean_product_name(self):
    #     """
    #     Enforce conditional uniqueness manually.

    #     Django's ModelForm validation doesn't reliably enforce
    #     UniqueConstraint with a `condition=` when the condition field
    #     isn't in Meta.fields. So we do it explicitly here.
    #     """
    #     name = self.cleaned_data.get('product_name', '').strip()
    #     if not name:
    #         return name

    #     qs = Product.objects.filter(product_name=name, is_deleted=False)
    #     if self.instance and self.instance.pk:
    #         qs = qs.exclude(pk=self.instance.pk)

    #     if qs.exists():
    #         raise forms.ValidationError(
    #             "此作品名稱已被使用。｜This product name is already in use."
    #         )
    #     return name


class ProductVariationForm(forms.ModelForm):
    """
    Modal form for adding/editing a single variation.
    Supports either FK-based lookup values (color/size/type dropdowns)
    OR free-text pending values (pending_color/pending_size/pending_type).
    """

    # Free-text fallback fields — if filled, they take precedence over the FK
    color_custom = forms.CharField(
        required=False, max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered input-sm w-full',
            'placeholder': '或新增｜Or add new',
        }),
    )
    size_custom = forms.CharField(
        required=False, max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered input-sm w-full',
            'placeholder': '或新增（含尺寸）｜Or add (with dimensions)',
        }),
    )
    type_custom = forms.CharField(
        required=False, max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered input-sm w-full',
            'placeholder': '或新增｜Or add new',
        }),
    )

    class Meta:
        model = ProductVariation
        fields = [
            'color', 'size', 'type',
            'price', 'original_price',
            'stock', 'weight',
            'with_shipping',
            'single_pack',
            'images',
        ]
        widgets = {
            'color': forms.Select(attrs={'class': 'select select-bordered select-sm w-full'}),
            'size': forms.Select(attrs={'class': 'select select-bordered select-sm w-full'}),
            'type': forms.Select(attrs={'class': 'select select-bordered select-sm w-full'}),
            'price': forms.NumberInput(attrs={
                'class': 'input input-bordered input-sm w-full',
                'step': '0.01', 'min': '0',
            }),
            'original_price': forms.NumberInput(attrs={
                'class': 'input input-bordered input-sm w-full',
                'step': '0.01', 'min': '0',
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'input input-bordered input-sm w-full', 'min': '0',
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'input input-bordered input-sm w-full', 'min': '0',
                'placeholder': 'grams',
            }),
            'single_pack': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-sm checkbox-primary',
            }),
            'images': CropTargetFileInput(),
            'with_shipping': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-sm checkbox-primary',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # FKs are optional — pending values cover the empty case
        self.fields['color'].required = False
        self.fields['size'].required = False
        self.fields['type'].required = False

        # 🆕 Image is required on NEW variations. On EDIT, if a
        # file already exists, keep it optional (user doesn't have to
        # re-upload to change other fields).
        if self.instance and self.instance.pk and self.instance.images:
            self.fields['images'].required = False
        else:
            self.fields['images'].required = True

        # Prefill custom fields from pending_* on edit
        if self.instance and self.instance.pk:
            self.initial.setdefault('color_custom', self.instance.pending_color or '')
            self.initial.setdefault('size_custom', self.instance.pending_size or '')
            self.initial.setdefault('type_custom', self.instance.pending_type or '')

    def clean_images(self):
        """
        Validate the image field.

        - On CREATE: image is required.
        - On EDIT with an existing image: image is optional (allows
          updates to other fields without re-upload).
        - On EDIT without an existing image: image is required.
        """
        img = self.cleaned_data.get('images')
        has_existing = bool(self.instance and self.instance.pk and self.instance.images)

        if not img and not has_existing:
            raise forms.ValidationError(
                "款式圖片為必填。｜Variation image is required."
            )

        if img:
            # Basic sanity checks
            try:
                from PIL import Image
                with Image.open(img) as pil_img:
                    w, h = pil_img.size
                    # Minimum dimension guard
                    if w < 200 or h < 200:
                        raise forms.ValidationError(
                            "圖片尺寸過小，建議至少 200×200 像素。"
                            "｜Image is too small; minimum 200×200 pixels recommended."
                        )
                    # Optional: ratio hint (soft — matches product hero hint)
                    ratio = w / h
                    if ratio < 0.4 or ratio > 2.5:
                        # Non-fatal; just attach a hint.
                        self.image_ratio_hint = (
                            f"Tip: Variation images display best between "
                            f"1:2 and 2:1. Yours is {w}×{h}. "
                            f"｜提示：款式圖片建議使用 1:2 至 2:1 之間的比例。"
                        )
            except forms.ValidationError:
                raise
            except Exception:
                # If Pillow can't read it, nh3 will still catch bad files
                # when the model saves. Don't hard-fail here.
                pass

        return img

    def clean(self):
        cleaned = super().clean()

        # Mutual exclusion: FK OR custom, not both
        pairs = [
            ('color', 'color_custom', '顏色｜Color'),
            ('size', 'size_custom', '尺寸｜Size'),
            ('type', 'type_custom', '款式｜Type'),
        ]
        for fk, custom, label in pairs:
            if cleaned.get(fk) and cleaned.get(custom, '').strip():
                self.add_error(
                    custom,
                    f"請擇一：下拉選擇或新增 {label}｜Choose either the dropdown or add a new value.",
                )

        if not cleaned.get('price'):
            self.add_error('price', "售價為必填。｜Price is required.")

        if not cleaned.get('stock') and cleaned.get('stock') != 0:
            self.add_error('stock', "庫存為必填。｜Stock is required.")

        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Apply pending values (whichever are used)
        instance.pending_color = self.cleaned_data.get('color_custom', '').strip()
        instance.pending_size = self.cleaned_data.get('size_custom', '').strip()
        instance.pending_type = self.cleaned_data.get('type_custom', '').strip()

        # Clear FK if a pending value is used (avoid confusion later)
        if instance.pending_color:
            instance.color = None
        if instance.pending_size:
            instance.size = None
        if instance.pending_type:
            instance.type = None

        if commit:
            instance.save()
        return instance