from django import forms

from edc_base.modelform_mixins import (
    CommonCleanModelFormMixin, ApplicableValidationMixin,
    RequiredFieldValidationMixin)
from edc_base.utils import get_utcnow
from edc_constants.constants import YES, FEMALE, MALE, ALIVE, UNKNOWN
from household.constants import (
    REFUSED_ENUMERATION, ELIGIBLE_REPRESENTATIVE_ABSENT, NO_HOUSEHOLD_INFORMANT)

from ..choices import RELATIONS, FEMALE_RELATIONS, MALE_RELATIONS
from ..constants import HEAD_OF_HOUSEHOLD
from ..models import HouseholdMember, EnrollmentChecklist, DeceasedMember
from ..models.household_member.utils import todays_log_entry_or_raise


class HouseholdMemberForm(CommonCleanModelFormMixin, ApplicableValidationMixin,
                          RequiredFieldValidationMixin, forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        try:
            EnrollmentChecklist.objects.get(
                household_member_id=self.instance.id)
            raise forms.ValidationError(
                'Enrollment checklist exists. This member may not be changed.')
        except EnrollmentChecklist.DoesNotExist:
            pass

        self.validate_refused_enumeration()
        self.validate_integrity_with_previous()

        if (cleaned_data.get('relation') == HEAD_OF_HOUSEHOLD
                and not cleaned_data.get('age_in_years', 0) >= 18):
            raise forms.ValidationError(
                'Head of Household must be 18 years or older.')
        elif (cleaned_data.get('eligible_hoh')
                and cleaned_data.get('age_in_years', 0) < 18):
            raise forms.ValidationError({
                'age_in_years': (
                    'This household member completed the HoH questionnaire. '
                    'You cannot change their age to less than 18. '
                    'Got {0}.'.format(cleaned_data.get('age_in_years')))})

        self.validate_on_gender()
        self.validate_initials_on_first_name()

        if cleaned_data.get('survival_status') in [ALIVE, UNKNOWN]:
            try:
                obj = DeceasedMember.objects.get(
                    household_member=self.instance)
            except DeceasedMember.DoesNotExist:
                pass
            else:
                raise forms.ValidationError({
                    'survival_status': 'Member was reported as deceased '
                    'on {}'.format(obj.site_aware_date.strftime('%Y-%m-%d'))})
        self.applicable_if(
            ALIVE, field='survival_status', field_applicable='present_today')
        self.applicable_if(
            ALIVE, field='survival_status', field_applicable='inability_to_participate')
        self.applicable_if(
            ALIVE, field='survival_status', field_applicable='study_resident')
        self.applicable_if(
            ALIVE, field='survival_status', field_applicable='relation')

        if 'personal_details_changed' in cleaned_data:
            self.applicable_if(
                ALIVE, field='survival_status', field_applicable='personal_details_changed')

            self.required_if(
                YES, field='personal_details_changed', field_required='details_change_reason')
        return cleaned_data

    def validate_integrity_with_previous(self):
        """Validates that this is not an attempt to ADD a member that
        already exists in a previous survey.
        """
        cleaned_data = self.cleaned_data
        if not self.instance.id:
            household_structure = cleaned_data.get('household_structure')
            while household_structure.previous:
                household_structure = household_structure.previous
                try:
                    HouseholdMember.objects.get(
                        household_structure=household_structure,
                        first_name=cleaned_data.get('first_name'),
                        initials=cleaned_data.get('initials'))
                except HouseholdMember.DoesNotExist:
                    pass
                else:
                    raise forms.ValidationError(
                        '{} with initials {} was enumerated '
                        'in {}. Please use the import tool to add this member '
                        'to the current survey.'.format(
                            cleaned_data.get('first_name'),
                            cleaned_data.get('initials'),
                            household_structure.survey_schedule_object.name))

    def validate_on_gender(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('relation'):
            if cleaned_data.get('gender') == MALE:
                relations = [
                    item[0] for item in RELATIONS if item not in FEMALE_RELATIONS]
                if cleaned_data.get('relation') not in relations:
                    raise forms.ValidationError({
                        'relation': 'Invalid relation for male.'})
            if cleaned_data.get('gender') == FEMALE:
                relations = [item[0]
                             for item in RELATIONS if item not in MALE_RELATIONS]
                if cleaned_data.get('relation') not in relations:
                    raise forms.ValidationError({
                        'relation': 'Invalid relation for female.'})

    def validate_initials_on_first_name(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('initials') and cleaned_data.get('first_name'):
            name_first_char = cleaned_data.get('first_name')[0]
            initials_first_char = cleaned_data.get('initials')[0]
            if name_first_char != initials_first_char:
                raise forms.ValidationError({
                    'initials': 'Invalid initials, first letter of first '
                                'name should be first letter of initials'})

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

    def validate_absent_during_enumeration(self):
        cleaned_data = self.cleaned_data
        household_structure = cleaned_data.get('household_structure')
        household_log_entry = todays_log_entry_or_raise(
            household_structure=household_structure,
            report_datetime=get_utcnow())
        if household_log_entry.household_status == ELIGIBLE_REPRESENTATIVE_ABSENT:
            raise forms.ValidationError('Household log entry for today shows '
                                        'household status as absent '
                                        'therefore you cannot add a '
                                        'representative eligibility')

    def validate_no_household_informent_enumeration(self):
        cleaned_data = self.cleaned_data
        household_structure = cleaned_data.get('household_structure')
        household_log_entry = todays_log_entry_or_raise(
            household_structure=household_structure,
            report_datetime=get_utcnow())
        if household_log_entry.household_status == NO_HOUSEHOLD_INFORMANT:
            raise forms.ValidationError('Household log entry for today shows '
                                        'household status as no household informant '
                                        'therefore you cannot add a '
                                        'representative eligibility')

    class Meta:
        model = HouseholdMember
        fields = '__all__'
