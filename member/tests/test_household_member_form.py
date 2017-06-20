from django import forms
from django.apps import apps as django_apps
from django.test import TestCase, tag
from uuid import uuid4

from edc_base.utils import get_utcnow
from edc_constants.constants import MALE, ALIVE, YES, NO, FEMALE, NOT_APPLICABLE
from edc_map.site_mappers import site_mappers
from household.constants import REFUSED_ENUMERATION
from survey.tests import SurveyTestHelper

from ..constants import ABLE_TO_PARTICIPATE, HEAD_OF_HOUSEHOLD
from ..form_validators import HouseholdMemberFormValidator
from ..forms import HouseholdMemberForm
from ..models import HouseholdMember
from .mappers import TestMapper
from .member_test_helper import MemberTestHelper


@tag('form')
class TestHouseholdMemberFormValidator(TestCase):

    member_helper = MemberTestHelper()
    survey_helper = SurveyTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys()
        django_apps.app_configs['edc_device'].device_id = '99'
        site_mappers.registry = {}
        site_mappers.loaded = False
        site_mappers.register(TestMapper)
        self.household_structure = self.member_helper.make_household_ready_for_enumeration(
            make_hoh=False)
        self.today_datetime = self.household_structure.report_datetime

    def test_form(self):
        form = HouseholdMemberForm()
        self.assertFalse(form.is_valid())

    def test_form_validator_log_entry(self):
        """Asserts raises on missing log entry for now.

        Note, for tests today is set in the past, see member_helper.get_utcnow.
        """
        cleaned_data = dict(household_structure=self.household_structure)
        form_validator = HouseholdMemberFormValidator(
            today_datetime=get_utcnow(),  # set to actual today, e.g future
            cleaned_data=cleaned_data,
            instance=HouseholdMember())
        self.assertRaises(forms.ValidationError, form_validator.validate)
        self.assertIn('household_log_entry', form_validator._error_codes)

    def test_form_validator_refused_enumeration(self):
        """Asserts raises if current household log entry log status
        is refused enumeration.
        """
        obj = self.household_structure.householdlog.householdlogentry_set.all().last()
        obj.household_status = REFUSED_ENUMERATION
        obj.save()
        cleaned_data = dict(
            household_structure=self.household_structure)
        form_validator = HouseholdMemberFormValidator(
            today_datetime=self.today_datetime,
            cleaned_data=cleaned_data,
            instance=HouseholdMember())
        self.assertRaises(forms.ValidationError, form_validator.validate)
        self.assertIn('refused_enumeration', form_validator._error_codes)

    def test_form_validator_relation_female(self):
        defaults = dict(household_structure=self.household_structure)
        cleaned_data = dict(
            relation='husband',
            gender=FEMALE, **defaults)
        form_validator = HouseholdMemberFormValidator(
            today_datetime=self.today_datetime,
            cleaned_data=cleaned_data,
            instance=HouseholdMember())
        self.assertRaises(forms.ValidationError, form_validator.validate)
        self.assertIn('relation', form_validator._errors)

    def test_form_validator_relation_male(self):
        defaults = dict(household_structure=self.household_structure)
        cleaned_data = dict(
            relation='wife',
            gender=MALE, **defaults)
        form_validator = HouseholdMemberFormValidator(
            today_datetime=self.today_datetime,
            cleaned_data=cleaned_data,
            instance=HouseholdMember())
        self.assertRaises(forms.ValidationError, form_validator.validate)
        self.assertIn('relation', form_validator._errors)

    def test_form_validator_initials(self):
        defaults = dict(
            household_structure=self.household_structure,
            relation='husband',
            gender=MALE,)
        cleaned_data = dict(
            first_name='ERIK',
            initials='XX', **defaults)
        form_validator = HouseholdMemberFormValidator(
            today_datetime=self.today_datetime,
            cleaned_data=cleaned_data,
            instance=HouseholdMember())
        self.assertRaises(forms.ValidationError, form_validator.validate)
        self.assertIn('initials', form_validator._errors)

    def test_form_validator_enrollment_checklist_complete_raises(self):
        cleaned_data = dict(household_structure=self.household_structure)
        form_validator = HouseholdMemberFormValidator(
            today_datetime=self.today_datetime,
            cleaned_data=cleaned_data,
            instance=HouseholdMember(id=uuid4(), enrollment_checklist_completed=True))
        self.assertRaises(forms.ValidationError, form_validator.validate)
        self.assertIn('enrollment_checklist_completed',
                      form_validator._error_codes)

    def test_household_member_alive1(self):
        defaults = dict(
            household_structure=self.household_structure,
            first_name='ERIK',
            initials='EX',
            relation='husband',
            gender=MALE)
        cleaned_data = dict(
            survival_status=ALIVE,
            present_today=NOT_APPLICABLE, **defaults)
        form_validator = HouseholdMemberFormValidator(
            today_datetime=self.today_datetime,
            cleaned_data=cleaned_data,
            instance=HouseholdMember())
        self.assertRaises(forms.ValidationError, form_validator.validate)
        self.assertIn('present_today', form_validator._errors)

    def test_household_member_alive2(self):
        defaults = dict(
            household_structure=self.household_structure,
            first_name='ERIK',
            initials='EX',
            relation='husband',
            gender=MALE)
        cleaned_data = dict(
            survival_status=ALIVE,
            present_today=YES,
            inability_to_participate=NOT_APPLICABLE,
            **defaults)
        form_validator = HouseholdMemberFormValidator(
            today_datetime=self.today_datetime,
            cleaned_data=cleaned_data,
            instance=HouseholdMember())
        self.assertRaises(forms.ValidationError, form_validator.validate)
        self.assertIn('inability_to_participate', form_validator._errors)

    def test_household_member_alive3(self):
        defaults = dict(
            household_structure=self.household_structure,
            first_name='ERIK',
            initials='EX',
            relation='husband',
            gender=MALE)
        cleaned_data = dict(
            survival_status=ALIVE,
            present_today=YES,
            inability_to_participate=ABLE_TO_PARTICIPATE,
            study_resident=NOT_APPLICABLE,
            **defaults)
        form_validator = HouseholdMemberFormValidator(
            today_datetime=self.today_datetime,
            cleaned_data=cleaned_data,
            instance=HouseholdMember())
        self.assertRaises(forms.ValidationError, form_validator.validate)
        self.assertIn('study_resident', form_validator._errors)

    def test_household_member_alive4(self):
        defaults = dict(
            household_structure=self.household_structure,
            first_name='ERIK',
            initials='EX',
            gender=MALE)
        cleaned_data = dict(
            survival_status=ALIVE,
            present_today=YES,
            inability_to_participate=ABLE_TO_PARTICIPATE,
            study_resident=YES,
            relation=NOT_APPLICABLE,
            **defaults)
        form_validator = HouseholdMemberFormValidator(
            today_datetime=self.today_datetime,
            cleaned_data=cleaned_data,
            instance=HouseholdMember())
        self.assertRaises(forms.ValidationError, form_validator.validate)
        self.assertIn('relation', form_validator._errors)

    def test_household_member_alive5(self):
        defaults = dict(
            household_structure=self.household_structure,
            first_name='ERIK',
            initials='EX',
            gender=MALE)
        cleaned_data = dict(
            survival_status=ALIVE,
            present_today=YES,
            inability_to_participate=ABLE_TO_PARTICIPATE,
            study_resident=YES,
            relation='husband',
            personal_details_changed=NOT_APPLICABLE,
            **defaults)
        form_validator = HouseholdMemberFormValidator(
            today_datetime=self.today_datetime,
            cleaned_data=cleaned_data,
            instance=HouseholdMember())
        self.assertRaises(forms.ValidationError, form_validator.validate)
        self.assertIn('personal_details_changed', form_validator._errors)

    def test_household_member_alive6(self):
        defaults = dict(
            household_structure=self.household_structure,
            first_name='ERIK',
            initials='EX',
            gender=MALE)
        cleaned_data = dict(
            survival_status=ALIVE,
            present_today=YES,
            inability_to_participate=ABLE_TO_PARTICIPATE,
            study_resident=YES,
            relation='husband',
            personal_details_changed=YES,
            details_change_reason=None,
            ** defaults)
        form_validator = HouseholdMemberFormValidator(
            today_datetime=self.today_datetime,
            cleaned_data=cleaned_data,
            instance=HouseholdMember())
        self.assertRaises(forms.ValidationError, form_validator.validate)
        self.assertIn('details_change_reason', form_validator._errors)

    def test_household_member_age_in_years_and_hoh(self):
        defaults = dict(
            household_structure=self.household_structure,
            first_name='ERIK',
            initials='EX',
            gender=MALE,
            survival_status=ALIVE,
            present_today=YES,
            inability_to_participate=ABLE_TO_PARTICIPATE,
            study_resident=YES,
            personal_details_changed=NO,
            details_change_reason=None,
        )
        cleaned_data = dict(
            age_in_years=15,
            relation=HEAD_OF_HOUSEHOLD,
            ** defaults)
        form_validator = HouseholdMemberFormValidator(
            today_datetime=self.today_datetime,
            cleaned_data=cleaned_data,
            instance=HouseholdMember())
        self.assertRaises(forms.ValidationError, form_validator.validate)
        self.assertIn('age_in_years', form_validator._errors)

    def test_household_member_age_in_years_and_hoh2(self):
        defaults = dict(
            household_structure=self.household_structure,
            first_name='ERIK',
            initials='EX',
            gender=MALE,
            survival_status=ALIVE,
            present_today=YES,
            inability_to_participate=ABLE_TO_PARTICIPATE,
            study_resident=YES,
            personal_details_changed=NO,
            details_change_reason=None,
        )
        cleaned_data = dict(
            age_in_years=15,
            relation='husband',
            ** defaults)
        form_validator = HouseholdMemberFormValidator(
            today_datetime=self.today_datetime,
            cleaned_data=cleaned_data,
            instance=HouseholdMember(id=uuid4(), eligible_hoh=True))
        self.assertRaises(forms.ValidationError, form_validator.validate)
        self.assertIn('age_in_years', form_validator._errors)

#
#     def test_household_member_add_previous_member(self):
#         household_member = self.member_helper.add_household_member(
#             household_structure=self.household_structure)
#         household_structure = self.member_helper.make_household_ready_for_last(
#             household_structure=self.household_structure)
#         defaults = dict(
#             household_structure=household_structure,
#             gender=MALE,
#             survival_status=ALIVE,
#             present_today=YES,
#             inability_to_participate=ABLE_TO_PARTICIPATE,
#             study_resident=YES,
#             personal_details_changed=NO,
#             details_change_reason=None,
#             age_in_years=18,
#             relation='husband',
#         )
#         cleaned_data = dict(
#             first_name=household_member.first_name,
#             initials=household_member.initials,
#             ** defaults)
#         form_validator = HouseholdMemberFormValidator(
#             today_datetime=self.today_datetime,
#             cleaned_data=cleaned_data,
#             instance=HouseholdMember())
#         self.assertRaises(forms.ValidationError, form_validator.validate)
#         self.assertIn('use_import_tool', form_validator._error_codes)
