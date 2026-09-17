# creators/forms.py
from django import forms
from django.core.exceptions import ValidationError

from .models import CraftType
from accounts.data import DESTINATIONS_MAINLAND_CHINA


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