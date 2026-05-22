from django import forms
from pharmacy.models import Coupons

class CheckoutForm(forms.Form):
    coupons = forms.ModelMultipleChoiceField(
        queryset=Coupons.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Купоны",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["coupons"].queryset = Coupons.objects.filter(is_active=True)