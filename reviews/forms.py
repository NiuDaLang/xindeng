from django import forms
from .models import Comment

class RangeInput(forms.widgets.NumberInput):
    input_type = "range"

class CommentForm(forms.Form):
    content_type = forms.CharField(widget=forms.HiddenInput(), required=False)
    object_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    rating = forms.DecimalField(
        label="評分|Rating",
        min_value=0.5,
        max_value=5.0,
        decimal_places=1,
        widget=RangeInput(
            attrs={
                "min": 0.5,
                "max": 5.0,
                "step": 0.5,
                "class": "star-rating-range",
                "value": 3.0
            }
        )
    )

    def __init__(self, *args, **kwargs):
        self.is_product_context = kwargs.pop('is_product_review', False)
        super().__init__(*args, **kwargs)

        if self.is_product_context:
            self.fields['rating'].required = True

    class Meta:
        model = Comment
        fields = ["text", "rating", "parent_comment", "content_type", "object_id"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 4, "placeholder": "請留言您的感想...|Your thoughts..."}),
            "parent_comment": forms.HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        rating=cleaned_data.get("rating")

        if self.is_product_context:
            if rating is None or rating == "":
                self.add_error("rating", "請提供評分|Please provide a rating.")

        return cleaned_data