from django.test import TestCase

from edc_constants.constants import MALE, ALIVE, YES, NO

from member.constants import ABLE_TO_PARTICIPATE
from member.forms.household_member_form import HouseholdMemberForm


class TestHouseholdMemberForm(TestCase):

    def setUp(self):
        super().setUp()
        self.consent_data = {
            'identity': '31721515',
            'confirm_identity': '31721515',
            'report_datetime': self.get_utcnow(),
        }
        self.bhs_subject_visit_male = self.make_subject_visit_for_consented_subject_male(
            'T0', **self.consent_data)
        self.options = {
            'internal_identifier': '343216789',
            'first_name': 'Neo',
            'initials': 'NJK',
            'gender': MALE,
            'age_in_years': 22,
            'survival_status': ALIVE,
            'present_today': NO,
            'inability_to_participate': ABLE_TO_PARTICIPATE,
            'inability_to_participate_other': None,
            'study_resident': NO,
            'personal_details_changed': NO,
            'details_change_reason': 'Married',
            'visit_attempts': 3,
            'eligible_htc': True,
            'refused_htc': False,
            'htc': True,
            'target': 2,
            'auto_filled': False,
            'updated_after_auto_filled': False,
            'additional_key': None,
            'subject_visit': self.bhs_subject_visit_male.id,
            'report_datetime': self.get_utcnow(),
        }

    def test_valid_form(self):
        form = HouseholdMemberForm(data=self.options)
        self.assertTrue(form.is_valid())

    def test_valid_initials(self):
        """Assert participant provided correct initials"""
        self.options.update(initials='BHJ')
        form = HouseholdMemberForm(data=self.options)
        self.AssertFalse(form.is_valid)

    def test_household_member_absence(self):
        """Assert if household member is present"""
        self.options.update(present_today=YES)
        form = HouseholdMemberForm(data=self.options)
        self.assertFalse(form.is_valid())
