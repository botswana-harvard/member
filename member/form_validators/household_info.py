from django import forms
from edc_base.modelform_validators import FormValidator

from ..models import RepresentativeEligibility


class HouseholdInfoFormValidator(FormValidator):

    def clean(self):

        try:
            RepresentativeEligibility.objects.get(
                household_structure=self.cleaned_data.get('household_structure'))
        except RepresentativeEligibility.DoesNotExist:
            raise forms.ValidationError(
                'Please complete the {} form first.'.format(
                    RepresentativeEligibility._meta.verbose_name))

        self.validate_other_specify('flooring_type')
        self.validate_other_specify('water_source')
        self.validate_other_specify('energy_source')
        self.validate_other_specify('toilet_facility')
        return self.cleaned_data
