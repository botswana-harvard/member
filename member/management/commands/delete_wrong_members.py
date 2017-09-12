from django.core.management.base import BaseCommand

from ...models import (
    HouseholdMember, HouseholdHeadEligibility, EnrollmentChecklist,
    AbsentMember, DeceasedMember, HtcMember, RefusedMember, UndecidedMember)
from bcpp_subject.models import Appointment, SubjectVisit, SubjectConsent
from household.exceptions import HouseholdLogRequired


def delete_household_members(map_area=None, survey_schedule=None, consent_version=None):
    household_members = HouseholdMember.objects.filter(
        household_structure__household__plot__map_area=map_area,
        survey_schedule=survey_schedule, cloned=True)
    count = 0
    not_household_members = []
    consented = 0
    for household_member in household_members:
        try:
            SubjectConsent.objects.get(
                version=consent_version, household_member=household_member)
            consented += 1
        except SubjectConsent.DoesNotExist:
            not_household_members.append(household_member)
    print(
        '••••••••••••••••••CONSENTED MEMBERS ARE•••••••••••••••••••••••••••• ')
    print(f'consented: {consented}')
    print(
        '••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••• ')
    members_to_delete = len(not_household_members)
    for household_member in not_household_members:
        HouseholdHeadEligibility.objects.filter(
            household_member=household_member).delete()
        try:
            AbsentMember.objects.filter(
                household_member=household_member).delete()
        except HouseholdLogRequired:
            print(
                '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print(
                f'Failed because of HouseholdLogRequired for {household_member}, {household_member.subject_identifier}')
            print(
                '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        DeceasedMember.objects.filter(
            household_member=household_member).delete()
        HtcMember.objects.filter(
            household_member=household_member).delete()
        RefusedMember.objects.filter(
            household_member=household_member).delete()
        UndecidedMember.objects.filter(
            household_member=household_member).delete()
        try:
            EnrollmentChecklist.objects.filter(
                household_member=household_member).delete()
        except TypeError:
            print(
                '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print(
                f'Failed to delete enrollment checklist for {household_member}, {household_member.subject_identifier}')
            print(
                '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        else:
            if not AbsentMember.objects.filter(
                    household_member=household_member):
                Appointment.objects.filter(
                    household_member=household_member).delete()
                SubjectVisit.objects.filter(
                    household_member=household_member).delete()
                household_member.delete()
        count += 1
        print(f'Succefully deleted {household_member}. {count} out of {members_to_delete}')


class Command(BaseCommand):

    help = 'Delete year 3 system cloned members'

    def add_arguments(self, parser):
        parser.add_argument('map_area', type=str, help='map_area')
        parser.add_argument(
            'survey_schedule', type=str, help='survey_schedule')
        parser.add_argument(
            'consent_version', type=str, help='consent_version')

    def handle(self, *args, **options):
        map_area = options['map_area']
        survey_schedule = options['survey_schedule']
        consent_version = options['consent_version']

        delete_household_members(
            map_area=map_area, survey_schedule=survey_schedule,
            consent_version=consent_version)
        self.stdout.write(self.style.SUCCESS('Succefully deleted members.'))
