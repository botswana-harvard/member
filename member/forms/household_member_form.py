from django import forms
from django.forms.utils import ErrorList

from edc_base.modelform_mixins import CommonCleanModelFormMixin
from edc_constants.constants import DEAD, NO, YES, FEMALE, MALE

from ..choices import RELATIONS, FEMALE_RELATIONS, MALE_RELATIONS
from ..constants import HEAD_OF_HOUSEHOLD
from ..models import HouseholdMember, EnrollmentChecklist


class HouseholdMemberForm(CommonCleanModelFormMixin, forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        try:
            EnrollmentChecklist.objects.get(
                household_member_id=self.instance.id)
            raise forms.ValidationError(
                'Enrollment checklist exists. This member may not be changed.')
        except EnrollmentChecklist.DoesNotExist:
            pass

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

        if cleaned_data.get('survival_status') == DEAD:
            if not cleaned_data.get('present_today') == NO:
                raise forms.ValidationError({
                    'present_today':
                    'Based on the response to survival status, please select NO.'})
            if (cleaned_data.get('study_resident') == NO
                    or cleaned_data.get('study_resident') == YES):
                self._errors['study_resident'] = ErrorList(
                    ['Please, select don\'t want to answer'])

        if cleaned_data.get('personal_details_changed') == YES:
            if not cleaned_data.get('details_change_reason'):
                raise forms.ValidationError({
                    'details_change_reason':
                    'Provide why personal details have changed.'})
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

    class Meta:
        model = HouseholdMember
        fields = '__all__'
