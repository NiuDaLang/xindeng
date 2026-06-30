from django import forms
from .models import Comment


class CommentForm(forms.Form):
    class Meta:
        model = Comment
        fields = ["text", "rating", "parent_comment"]
        widgets = {
            "text": forms.Textarea(attrs={
                "rows": 4, 
                "class": "textarea textarea-bordered w-full text-xs font-sans bg-white",
                "placeholder": "Detailed Feedback Content｜在此留下您寶貴的心得感受..."
            }),
            "parent_comment": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        self.is_product_context = kwargs.pop('is_product_review', False)
        super().__init__(*args, **kwargs)
        
        # Make the field optional if we are handling a standard blog comment context
        if self.is_product_context:
            self.fields['rating'].required = True
        else:
            self.fields['rating'].required = False

    def clean(self):
        cleaned_data = super().clean()
        rating = cleaned_data.get("rating")

        if self.is_product_context:
            if rating is None or rating == "":
                self.add_error("rating", "Please provide a rating｜請提供評分")

        return cleaned_data    