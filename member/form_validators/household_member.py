from django import forms

from edc_base.modelform_validators import FormValidator
from edc_base.utils import get_utcnow
from edc_constants.constants import YES, FEMALE, MALE, ALIVE, UNKNOWN

from household.constants import REFUSED_ENUMERATION
from household.exceptions import HouseholdLogRequired
from household.models import todays_log_entry_or_raise

from ..choices import RELATIONS, FEMALE_RELATIONS, MALE_RELATIONS
from ..constants import HEAD_OF_HOUSEHOLD
from ..models import HouseholdMember, DeceasedMember


class HouseholdMemberFormValidator(FormValidator):

    def __init__(self, today_datetime=None, **kwargs):
        super().__init__(**kwargs)
        self.household_structure = self.cleaned_data.get('household_structure')
        self.first_name = self.cleaned_data.get('first_name')
        self.initials = self.cleaned_data.get('initials')
        self.relation = self.cleaned_data.get('relation')
        self.age_in_years = self.cleaned_data.get('age_in_years', 0)
        if self.instance.id:
            self.eligible_hoh = self.instance.eligible_hoh
        else:
            self.eligible_hoh = False
        self.gender = self.cleaned_data.get('gender')
        self.survival_status = self.cleaned_data.get('survival_status')
        if not self.instance.id:
            self.report_datetime = self.cleaned_data.get(
                'report_datetime', today_datetime or get_utcnow())
        else:
            self.report_datetime = today_datetime or self.instance.report_datetime

    def clean(self):

        # validate cannot change if enrollment_checklist_completed
        if self.instance.id and self.instance.enrollment_checklist_completed:
            raise forms.ValidationError(
                'Enrollment checklist exists. This member may not be changed.',
                code='enrollment_checklist_completed')

        # require household log entry
        try:
            self.household_log_entry = todays_log_entry_or_raise(
                household_structure=self.household_structure,
                report_datetime=self.report_datetime)
        except HouseholdLogRequired as e:
            raise forms.ValidationError(e, code='household_log_entry')

        # validate_refused_enumeration
        if self.household_log_entry.household_status == REFUSED_ENUMERATION:
            raise forms.ValidationError(
                'Household log entry for today shows household status as refused '
                'therefore you cannot add a member', code='refused_enumeration')

        self.validate_member_integrity_with_previous()

        # validate age of HoH
        if self.relation == HEAD_OF_HOUSEHOLD and not self.age_in_years >= 18:
            raise forms.ValidationError({
                'age_in_years': 'Head of Household must be 18 years or older.'})
        elif self.eligible_hoh and self.age_in_years < 18:
            raise forms.ValidationError({
                'age_in_years': (
                    f'This household member completed the HoH questionnaire. '
                    f'You cannot change their age to less than 18. '
                    f'Got {self.age_in_years}.')})

        self.validate_relation_and_gender()

        # validate_initials_on_first_name
        try:
            assert self.first_name[0] == self.initials[0]
        except AssertionError:
            raise forms.ValidationError({
                'initials': 'Invalid initials. First name does not match first initial.'})
        except TypeError:
            pass

        if self.survival_status in [ALIVE, UNKNOWN]:
            try:
                obj = DeceasedMember.objects.get(
                    household_member=self.instance)
            except DeceasedMember.DoesNotExist:
                pass
            else:
                aware_date = obj.site_aware_date.strftime('%Y-%m-%d')
                raise forms.ValidationError({
                    'survival_status': f'Member was reported as deceased on {aware_date}'})

        self.applicable_if(
            ALIVE, field='survival_status', field_applicable='present_today')
        self.applicable_if(
            ALIVE, field='survival_status', field_applicable='inability_to_participate')
        self.applicable_if(
            ALIVE, field='survival_status', field_applicable='study_resident')
        self.applicable_if(
            ALIVE, field='survival_status', field_applicable='relation')

        if 'personal_details_changed' in self.cleaned_data:
            self.applicable_if(
                ALIVE, field='survival_status', field_applicable='personal_details_changed')
            self.required_if(
                YES, field='personal_details_changed', field_required='details_change_reason')
        return self.cleaned_data

    def validate_member_integrity_with_previous(self):
        """Validates that this is not an attempt to ADD a member that
        already exists in a previous survey.
        """
        if not self.instance.id:
            while self.household_structure.previous:
                household_structure = self.household_structure.previous
                try:
                    HouseholdMember.objects.get(
                        household_structure=household_structure,
                        first_name=self.first_name,
                        initials=self.initials)
                except HouseholdMember.DoesNotExist:
                    pass
                else:
                    raise forms.ValidationError(
                        f'{self.first_name} with initials {self.initials} was '
                        f'enumerated in {household_structure.survey_schedule_object.name}. '
                        'Please use the import tool to add this member to the current '
                        'survey.', code='use_import_tool')

    def validate_relation_and_gender(self):
        if self.relation:
            if self.gender == MALE:
                relations = [
                    item[0] for item in RELATIONS if item not in FEMALE_RELATIONS]
                if self.relation not in relations:
                    raise forms.ValidationError({
                        'relation': 'Invalid relation for male.'})
            elif self.gender == FEMALE:
                relations = [
                    item[0] for item in RELATIONS if item not in MALE_RELATIONS]
                if self.relation not in relations:
                    raise forms.ValidationError({
                        'relation': 'Invalid relation for female.'})

#     def validate_absent_during_enumeration(self):
#         if self.household_log_entry.household_status == ELIGIBLE_REPRESENTATIVE_ABSENT:
#             raise forms.ValidationError(
#                 'Household log entry for today shows household status as absent '
#                 'therefore you cannot add a representative eligibility')
#
#     def validate_no_household_informant_enumeration(self):
#         if self.household_log_entry.household_status == NO_HOUSEHOLD_INFORMANT:
#             raise forms.ValidationError(
#                 'Household log entry for today shows household status as no '
#                 'household informant therefore you cannot add a '
#                 'representative eligibility')
