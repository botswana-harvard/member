from django import forms
from django.db.models import Max
from django.forms import ValidationError

from edc_base.utils import get_utcnow

from household.models import HouseholdLogEntry
from household.constants import REFUSED_ENUMERATION, ELIGIBLE_REPRESENTATIVE_ABSENT
from household.constants import NO_HOUSEHOLD_INFORMANT
from household.utils import todays_log_entry_or_raise

from ..exceptions import EnumerationRepresentativeError
from ..models import RepresentativeEligibility


class RepresentativeEligibilityForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        household_structure = cleaned_data.get('household_structure')

        self.validate_refused_enumeration()
        self.validate_eligible_participant_absent()
        self.validate_eligible_if_no_household_participant()

        try:
            report_datetime = HouseholdLogEntry.objects.filter(
                household_log__household_structure=household_structure).aggregate(
                    Max('report_datetime')).get('report_datetime__max')
            if HouseholdLogEntry.objects.get(
                    household_log__household_structure=household_structure,
                    household_status='no_household_informant',
                    report_datetime=report_datetime):
                raise ValidationError(
                    'You cannot save representative eligibility, '
                    'no household informant.')

            HouseholdLogEntry.objects.get(
                household_log__household_structure=household_structure,
                report_datetime=report_datetime,
                household_status=ELIGIBLE_REPRESENTATIVE_ABSENT)
            raise ValidationError(
                'The eligible household representative is absent. '
                'See Household Log.')
        except HouseholdLogEntry.DoesNotExist:
            pass
        try:
            instance = self._meta.model(id=self.instance.id, **cleaned_data)
            instance.common_clean()
        except EnumerationRepresentativeError as e:
            raise forms.ValidationError(str(e))
        return cleaned_data

    def validate_eligible_participant_absent(self):
        cleaned_data = self.cleaned_data
        household_structure = cleaned_data.get('household_structure')
        household_log_entry = todays_log_entry_or_raise(
            household_structure=household_structure,
            report_datetime=get_utcnow())
        if household_log_entry.household_status == ELIGIBLE_REPRESENTATIVE_ABSENT:
            raise forms.ValidationError('Household log entry for today shows '
                                        'household status as absent '
                                        'therefore you cannot add '
                                        'representative eligibility')
        return cleaned_data

    def validate_eligible_if_no_household_participant(self):
        cleaned_data = self.cleaned_data
        household_structure = cleaned_data.get('household_structure')
        household_log_entry = todays_log_entry_or_raise(
            household_structure=household_structure,
            report_datetime=get_utcnow())
        if household_log_entry.household_status == NO_HOUSEHOLD_INFORMANT:
            raise forms.ValidationError('Household log entry for today shows '
                                        'household status as no household informant '
                                        'therefore you cannot add '
                                        'representative eligibility')
        return cleaned_data

    def validate_refused_enumeration(self):
        cleaned_data = self.cleaned_data
        household_structure = cleaned_data.get('household_structure')
        household_log_entry = todays_log_entry_or_raise(
            household_structure=household_structure,
            report_datetime=get_utcnow())
        if household_log_entry.household_status == REFUSED_ENUMERATION:
            raise forms.ValidationError('Household log entry for today shows '
                                        'household status as refused '
                                        'therefore you cannot add a member')
        return cleaned_data

    class Meta:
        model = RepresentativeEligibility
        fields = '__all__'
