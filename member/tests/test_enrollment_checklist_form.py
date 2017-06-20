from django.test import TestCase

from edc_constants.constants import MALE, ALIVE, YES, NO

from ..constants import ABLE_TO_PARTICIPATE
from ..forms import HouseholdMemberForm
from .member_test_helper import MemberTestHelper


class TestHouseholdMemberForm(TestCase):

    member_helper = MemberTestHelper()

    def setUp(self):
        self.subject_visit = self.make_subject_visit_for_consented_subject(
            'T0')
        self.options = {
            'internal_identifier': '343216789',
            'first_name': 'Neo',
            'initials': 'NJK',
            'gender': MALE,
            'age_in_years': 22,
            'survival_status': ALIVE,
            'present_today': YES,
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
            'subject_visit': self.subject_visit.id,
            'report_datetime': self.member_helper.get_utcnow(),
        }

    def test_valid_form(self):
        form = HouseholdMemberForm(data=self.options)
        self.assertTrue(form.is_valid())

    def test_valid_initials(self):
        """Assert participant provided correct initials"""
        self.options.update(initials='BHJ')
        form = HouseholdMemberForm(data=self.options)
        self.AssertFalse(form.is_valid)
