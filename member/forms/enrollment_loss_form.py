from django import forms

from ..models import EnrollmentLoss


class EnrollmentLossForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('household_member').enrollment_checklist_completed:
            raise forms.ValidationError(
                'Enrollment Checklist has not been completed. Please correct.')
        return cleaned_data

    class Meta:
        model = EnrollmentLoss
        fields = '__all__'
