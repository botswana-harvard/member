from django import forms

from edc_base.modelform_mixins import OtherSpecifyValidationMixin

from ..models import HouseholdInfo, RepresentativeEligibility


class HouseholdInfoForm (OtherSpecifyValidationMixin, forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        try:
            RepresentativeEligibility.objects.get(
                household_structure=cleaned_data.get('household_structure'))
        except RepresentativeEligibility.DoesNotExist:
            raise forms.ValidationError(
                'Please complete the {} form first.'.format(
                    RepresentativeEligibility._meta.verbose_name))
        self.validate_other_specify('flooring_type')
        self.validate_other_specify('water_source')
        self.validate_other_specify('energy_source')
        self.validate_other_specify('toilet_facility')
        cleaned_data = super(HouseholdInfoForm, self).clean()
        return cleaned_data

    class Meta:
        model = HouseholdInfo
        fields = '__all__'
