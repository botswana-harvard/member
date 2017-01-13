from django.test import TestCase, tag

from .test_mixins import MemberMixin
from survey.site_surveys import site_surveys


class TestSurvey(MemberMixin, TestCase):

    """Tests to assert survey attrs."""

    def test_household_member(self):
        self.survey_schedule = self.get_survey_schedule(0)

        household_structure = self.make_household_ready_for_enumeration(
            survey_schedule=self.survey_schedule)

        household_member = self.add_household_member(household_structure)

        self.assertIsNotNone(household_member.survey_schedule)
        self.assertIsNotNone(household_member.survey_schedule_object)
        self.assertRaises(
            AttributeError, getattr, household_member, 'survey')
        self.assertRaises(
            AttributeError, getattr, household_member, 'survey_object')

    def test_household_member_survey_schedule_set_correctly(self):

        survey_schedules = site_surveys.get_survey_schedules(group_name='example-survey')

        if not survey_schedules:
            raise AssertionError('survey_schedules is unexpectedly None')

        for index, survey_schedule in enumerate(
                site_surveys.get_survey_schedules(group_name='example-survey')):
            household_structure = self.make_household_ready_for_enumeration(
                survey_schedule=survey_schedule)
            household_member = self.add_household_member(household_structure)
            self.assertEqual(
                household_member.survey_schedule,
                'example-survey.example-survey-{}.test_community'.format(index + 1))
            self.assertEqual(
                household_member.survey_schedule_object.field_value,
                'example-survey.example-survey-{}.test_community'.format(index + 1))
            self.assertEqual(
                household_member.survey_schedule_object.name,
                'example-survey-{}'.format(index + 1))
            self.assertEqual(
                household_member.survey_schedule_object.group_name,
                'example-survey')
            self.assertEqual(
                household_member.survey_schedule_object.short_name,
                'example-survey.example-survey-{}'.format(index + 1))
