# creators/forms.py
from django import forms
from django.core.exceptions import ValidationError

from .models import CreatorProfile, CraftType
from accounts.data import DESTINATIONS_MAINLAND_CHINA

from django.utils.text import slugify

from taggit.models import Tag
from blog.models import Post
from django_ckeditor_5.widgets import CKEditor5Widget
from .utils import clean_blog_body
from core.widgets import CropTargetClearableFileInput


class CustomClearableFileInput(forms.ClearableFileInput):
    template_name = 'widgets/clearable_file_input.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        attrs_dict = context['widget'].get('attrs', {})  
        attrs_dict.pop('disabled', None)
        attrs_dict.pop('checked', None)
        return context

    def value_from_datadict(self, data, files, name):
        upload = files.get(name)
        if upload:
            # A new file was uploaded — prefer it, ignore the clear checkbox.
            # This bypasses ClearableFileInput's FILE_INPUT_CONTRADICTION detection.
            return upload
        # No new file — defer to super() so the clear checkbox is handled normally.
        return super().value_from_datadict(data, files, name)
    

class ArtisanApplicationForm(forms.Form):
    # ── Identity ─────────────────────────────────
    display_name = forms.CharField(
        max_length=100,
        label="Public Display Name｜公開展示名稱",
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'e.g., Li Huixian｜李慧嫻',
        })
    )
    full_name = forms.CharField(
        max_length=100,
        label="Full Name (private)｜真實姓名（僅供內部審核）",
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
        })
    )
    email = forms.EmailField(
        label="Email｜電郵",
        widget=forms.EmailInput(attrs={
            'class': 'input input-bordered w-full',
        })
    )
    phone = forms.CharField(
        max_length=30,
        required=False,
        label="Phone｜電話（可選）",
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
        })
    )
    wechat = forms.CharField(
        max_length=50,
        required=False,
        label="WeChat ID｜微信號（可選）",
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
        })
    )

    # ── Location ────────────────────────────────
    province = forms.ChoiceField(
        choices=[('', '—')] + list(DESTINATIONS_MAINLAND_CHINA),
        label="Province｜省份",
        widget=forms.Select(attrs={'class': 'select select-bordered w-full'})
    )
    city = forms.CharField(
        max_length=50,
        required=False,
        label="City｜城市",
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )

    # ── Craft ────────────────────────────────────
    craft_types = forms.ModelMultipleChoiceField(
        queryset=CraftType.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Your Craft(s)｜您的工藝",
        help_text="You may select more than one.",
    )

    # ── Portfolio & Bio ──────────────────────────
    portfolio_url = forms.URLField(
        required=False,
        label="Portfolio URL｜作品集連結（可選）",
        widget=forms.URLInput(attrs={'class': 'input input-bordered w-full'})
    )
    short_bio = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'textarea textarea-bordered w-full',
            'rows': 4,
            'placeholder': 'Tell us about your craft and your work...｜請簡單介紹您的工藝與作品...'
        }),
        max_length=500,
        label="Short Bio｜自我簡介",
    )
    reason_for_joining = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'textarea textarea-bordered w-full',
            'rows': 4,
            'placeholder': "Why would you like to join?｜為何希望加入我們？"
        }),
        max_length=500,
        label="Why do you want to join?｜加入原因",
    )

    # ── Anti-bot ─────────────────────────────────
    honeypot = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'autocomplete': 'off',
            'tabindex': '-1',
            'style': 'position:absolute; left:-9999px; width:1px; height:1px; opacity:0;',
            'aria-hidden': 'true',
        }),
        label="",
    )
    render_timestamp = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )
    math_answer = forms.IntegerField(
        label="Verification｜驗證",
        widget=forms.NumberInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Answer the question above｜請輸入答案',
        })
    )

    def clean_honeypot(self):
        """If honeypot is filled, it's a bot. Raise a silent error."""
        if self.cleaned_data.get('honeypot'):
            raise ValidationError("Invalid submission.")
        return ''


class CreatorProfileForm(forms.ModelForm):
    """
    Form for artisans to edit their own CreatorProfile.
    Excludes admin-only fields (is_verified, is_premium, premium_page_*).
    """
    craft_types = forms.ModelMultipleChoiceField(
        queryset=CraftType.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        help_text="選擇您所從事的工藝（可多選）。｜Select all craft disciplines that apply.",
    )

    tags_choices = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.none(),  # populated in __init__
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="從現有標籤中挑選（可多選）。｜Choose from existing tags.",
    )

    class Meta:
        model = CreatorProfile
        fields = [
            'display_name',
            'slug',
            'tagline',
            'bio',
            'province',
            'city',
            'avatar',
            'banner',
            'website',
            'instagram',
            'wechat_qr',
            'page_template',
        ]
        widgets = {
            'display_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'e.g., Li Huixian｜李慧嫻',
            }),
            'slug': forms.TextInput(attrs={
                'class': 'input input-bordered w-full font-mono text-sm',
                'placeholder': 'leave blank to auto-generate｜留空即自動生成',
            }),
            'tagline': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'A short poetic line｜一句短語',
                'maxlength': 200,
            }),
            'bio': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 8,
                'placeholder': 'Tell visitors about your craft, your workshop, your approach…\n請介紹您的工作坊、工藝與理念…',
            }),
            'province': forms.Select(attrs={
                'class': 'select select-bordered w-full',
            }),
            'city': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'e.g., Dali｜大理',
            }),
            'avatar': CustomClearableFileInput(attrs={
                'class': 'file-input file-input-bordered w-full',
                'accept': 'image/*',
            }),
            'banner': CustomClearableFileInput(attrs={
                'class': 'file-input file-input-bordered w-full',
                'accept': 'image/*',
            }),
            'website': forms.URLInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'https://example.com',
            }),
            'instagram': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'username, no @｜用戶名，不含 @',
            }),
            'wechat_qr': CustomClearableFileInput(attrs={
                'class': 'file-input file-input-bordered w-full',
                'accept': 'image/*',
            }),
            'page_template': forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate tag choices — only show used tags
        from taggit.models import TaggedItem
        used_tag_ids = TaggedItem.objects.values_list('tag_id', flat=True).distinct()
        self.fields['tags_choices'].queryset = Tag.objects.filter(name__contains='|').order_by('name')

        # ── Populate initial values for manually-declared fields ──
        if self.instance and self.instance.pk:
            self.fields['craft_types'].initial = self.instance.craft_types.all()
            self.fields['tags_choices'].initial = self.instance.tags.all()

        # ── page_template: set choices AND re-attach the widget ──
        page_template_choices = [
            ('A', 'Banner-Led｜橫幅主導'),
            ('B', 'Portrait-Led｜肖像主導'),
            ('C', 'Text-Led｜文字主導（預設）'),
        ]
        if self.instance and self.instance.is_premium:
            page_template_choices.append(
                ('D', 'Custom Premium｜客製精選（僅限管理員設定）')
            )

        self.fields['page_template'].choices = page_template_choices
        self.fields['page_template'].widget = forms.RadioSelect(choices=page_template_choices)

    def clean_slug(self):
        """Allow blank slug — auto-generate from display_name."""
        slug = self.cleaned_data.get('slug', '').strip()
        if slug:
            # Ensure uniqueness (exclude self)
            qs = CreatorProfile.objects.filter(slug=slug)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(
                    "此網址代稱已被使用。｜This slug is already taken."
                )
        return slug

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Auto-generate slug from display_name if left blank
        if not instance.slug:
            base_slug = slugify(instance.display_name)
            slug = base_slug
            counter = 2
            while CreatorProfile.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            instance.slug = slug

        if commit:
            instance.save()
            
            # Explicitly save craft_types (declared field, not auto-handled)
            if 'craft_types' in self.cleaned_data:
                instance.craft_types.set(self.cleaned_data['craft_types'])

            # Tags are M2M via taggit — set them
            if 'tags_choices' in self.cleaned_data:
                for tag in self.cleaned_data['tags_choices']:
                    instance.tags.add(tag)
                # 移除用户取消勾选的（这里需要知道"原先有、现在没勾"的集合）
                initial_tags = set(self.initial.get('tags_choices', []))
                selected_tags = set(self.cleaned_data['tags_choices'])
                for tag in initial_tags - selected_tags:
                    instance.tags.remove(tag)

        return instance

    def _check_file_clear_conflict(self, field_name):
        """
        Raise a bilingual ValidationError if the user submitted both a new file
        and the clear checkbox for the given field.
        """
        from django.core.exceptions import ValidationError

        # The clear checkbox is named '<field_name>-clear'
        clear_key = f'{field_name}-clear'

        # Files dict contains uploaded files keyed by field name
        file_uploaded = bool(self.files.get(field_name))

        # Data dict contains the checkbox value ('on' if checked)
        clear_checked = bool(self.data.get(clear_key))

        if file_uploaded and clear_checked:
            raise ValidationError(
                "請勿同時提交檔案並勾選「移除」，請二選一。"
                "｜Please submit either a new file OR check the clear checkbox, not both."
            )

    def clean_avatar(self):
        self._check_file_clear_conflict('avatar')
        return self.cleaned_data.get('avatar')

    def clean_banner(self):
        self._check_file_clear_conflict('banner')
        return self.cleaned_data.get('banner')

    def clean_wechat_qr(self):
        self._check_file_clear_conflict('wechat_qr')
        return self.cleaned_data.get('wechat_qr')


class BlogPostForm(forms.ModelForm):
    """
    Artisan-side form for creating/editing blog posts.
    Does NOT expose status, author, creator — those are set in the view.
    """
    tags_choices = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text=(
            "從現有標籤中挑選；如需新增請聯繫後台。"
            "｜Pick from existing tags. To request a new one, contact the platform."
        ),
    )

    class Meta:
        model = Post
        fields = [
            'title',
            'short_description',
            'post_category',
            'featured_image',
            'blog_body',
            'location',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Title｜標題',
            }),
            'short_description': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 3,
                'placeholder': 'A brief description shown in lists｜列表用簡介（最多 500 字）',
            }),
            'post_category': forms.Select(attrs={
                'class': 'select select-bordered w-full',
            }),
            'featured_image': CropTargetClearableFileInput(),
            'blog_body': CKEditor5Widget(
                config_name='extends',
                attrs={'class': 'django_ckeditor_5'},
            ),
            'location': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'e.g., Dali, Yunnan｜例如：雲南大理（可選）',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Tag choices: only used tags in the platform
        from taggit.models import TaggedItem
        used_tag_ids = (
            TaggedItem.objects
            .values_list('tag_id', flat=True)
            .distinct()
        )
        self.fields['tags_choices'].queryset = (
            Tag.objects
            .filter(id__in=used_tag_ids)
            .order_by('name')
        )

        # Pre-select existing tags if editing
        if self.instance and self.instance.pk:
            self.fields['tags_choices'].initial = self.instance.tags.all()

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Sanitize rich text before it ever touches the DB
        if 'blog_body' in self.cleaned_data:
            instance.blog_body = clean_blog_body(self.cleaned_data['blog_body'])

        if commit:
            instance.save()
            if 'tags_choices' in self.cleaned_data:
                instance.tags.set(self.cleaned_data['tags_choices'])

        return instance