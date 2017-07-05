# from faker import Faker
# from uuid import uuid4
# from django.test import TestCase, tag
# from model_mommy import mommy
#
# from edc_registration.models import RegisteredSubject
# from household.models import Household, HouseholdStructure
# from member_clone.clone import Clone
# from survey.site_surveys import site_surveys
# from survey.tests import SurveyTestHelper
# from survey.tests.surveys import survey_one
#
# from ..models import HouseholdMember
# from .member_test_helper import MemberTestHelper
#
# fake = Faker()
#
#
# @tag('clone')
# class TestCloneMembers(TestCase):
#
#     survey_helper = SurveyTestHelper()
#     member_helper = MemberTestHelper()
#
#     def setUp(self):
#         self.survey_helper.load_test_surveys(load_all=True)
#
#     
#     def test_household_member_clone(self):
#         survey_schedule = site_surveys.get_survey_schedules(current=True)[0]
#         household_structure = self.member_helper.make_household_ready_for_enumeration(
#             make_hoh=False, survey_schedule=survey_schedule)
#         self.member_helper.add_household_member(
#             household_structure=household_structure)
#         self.member_helper.add_household_member(
#             household_structure=household_structure)
#         self.member_helper.add_household_member(
#             household_structure=household_structure)
#         next_household_structure = self.member_helper.get_next_household_structure_ready(
#             household_structure, make_hoh=None)
#         previous_members = HouseholdMember.objects.filter(
#             household_structure=household_structure).order_by('report_datetime')
#         for obj in previous_members:
#             new_obj = obj.clone(
#                 household_structure=next_household_structure,
#                 report_datetime=next_household_structure.report_datetime,
#                 user_created='erikvw')
#             self.assertEqual(
#                 obj.internal_identifier, new_obj.internal_identifier)
#             self.assertEqual(
#                 obj.subject_identifier, new_obj.subject_identifier)
#             new_obj.save()
#             new_obj = HouseholdMember.objects.get(pk=new_obj.pk)
#             self.assertEqual(
#                 obj.internal_identifier, new_obj.internal_identifier)
#             self.assertEqual(
#                 obj.subject_identifier, new_obj.subject_identifier)
#
#     
#     def test_clone_members_none(self):
#         survey_schedule = site_surveys.get_survey_schedules(current=True)[0]
#         household_structure = self.member_helper.make_household_ready_for_enumeration(
#             make_hoh=False, survey_schedule=survey_schedule)
#         next_household_structure = self.member_helper.get_next_household_structure_ready(
#             household_structure, make_hoh=False)
#         clone = Clone(
#             household_structure=next_household_structure,
#             report_datetime=household_structure.report_datetime)
#         self.assertEqual(clone.members.all().count(), 0)
#
#     
#     def test_clone_members_no_previous(self):
#         survey_schedule = site_surveys.get_survey_schedules(current=True)[0]
#         household_structure = self.member_helper.make_household_ready_for_enumeration(
#             make_hoh=False, survey_schedule=survey_schedule)
#         next_household_structure = self.member_helper.get_next_household_structure_ready(
#             household_structure, make_hoh=False)
#         clone = Clone(
#             household_structure=next_household_structure,
#             report_datetime=household_structure.report_datetime)
#         self.assertEqual(clone.members.all().count(), 0)
