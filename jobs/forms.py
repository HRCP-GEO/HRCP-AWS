from django import forms
from .models import Job # <-- Import the Job model
import re

class JobAdForm(forms.Form):

    PAYMENT_METHODS = [
        ('გადარიცხვა', 'ონლაინ გადახდა'),
        ('ინვოისი', 'ინვოისი'),
    ]

    # Product options with prices
    PRODUCT_CHOICES = [
        ("standard", "სტანდარტული განცხადება - 30 ლარი"),
        ("standard_logo", "სტანდარტული განცხადება + ლოგო - 50 ლარი"),
        ("vip_ad", "VIP განცხადება - 100 ლარი"),  # Changed key from 'vip' to 'vip_ad' for clarity
        ("vip_logo", "VIP განცხადება + ლოგო - 120 ლარი"),
        ("training", "ტრენინგი/განათლება - 30 ლარი"),
        ("training_logo", "ტრენინგი/განათლება + ლოგო - 50 ლარი"),
        ("tender", "ტენდერი - 30 ლარი"),
        ("tender_logo", "ტენდერი + ლოგო - 50 ლარი"),
    ]

    identification_code = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}),required=True)
    company_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}),required=True)
    company_email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}),required=True)
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control','type': 'tel', 'placeholder': '+995 XXX XXX XXX'}),required=True)
    additional_email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), required=False)

    # --- MODIFIED FIELD ---
    advertisement_type = forms.ChoiceField(
        choices=Job.JOB_TYPES, # <-- Use choices from the Job model
        widget=forms.Select(attrs={'class': 'form-control'}), # <-- Use Select widget
        required=True # <-- Make it required
    )
    # --- END MODIFIED FIELD ---

    advertisement_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    comment = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), required=False)
    vacancy_description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}), required=False)

    # Keep the product selection as ChoiceField (or adjust if you implement multi-select)
    # Note: The HTML allows adding multiple products, but the form currently only defines one ChoiceField.
    # You might need to use a different field type (like MultipleChoiceField or Formsets)
    # if you want users to select multiple products simultaneously via the form submission itself.
    # The current setup suggests JS handles the multi-product logic primarily for price calculation.
    products = forms.MultipleChoiceField(
        choices=PRODUCT_CHOICES,
        # widget=forms.SelectMultiple(attrs={"class": "form-control"}), # Use default or this
        required=True
    )

    document = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    company_logo = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))


    def clean_advertisement_name(self):
        data = self.cleaned_data['advertisement_name']
        if not data:
             raise forms.ValidationError("This field is required.") # Or Georgian translation
        return data

    def clean_phone(self):
        phone_number = self.cleaned_data.get('phone')
        if phone_number:  # Only validate if something was entered
            # Example: Simple regex for digits, spaces, +, - (adjust as needed)
            # This is a VERY basic example, doesn't validate actual number structure
            if not re.match(r'^[\d\s\+\-\(\)]+$', phone_number):
                raise forms.ValidationError("არასწორი ტელეფონის ნომრის ფორმატი.")  # "Invalid phone number format."
            # You could add more sophisticated regex or checks here
        return phone_number
