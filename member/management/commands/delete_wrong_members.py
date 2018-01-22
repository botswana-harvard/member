from datetime import datetime
from django.core.management.base import BaseCommand

from edc_map.models import InnerContainer
from edc_sync.models import OutgoingTransaction
from ...models import (
    HouseholdMember, HouseholdHeadEligibility, EnrollmentChecklist,
    AbsentMember, DeceasedMember, HtcMember, MovedMember, RefusedMember, UndecidedMember)
from bcpp_subject.models import Appointment, SubjectVisit, SubjectConsent
from household.exceptions import HouseholdLogRequired
from django.core.exceptions import ValidationError
from django.conf import settings


def delete_household_members(
        map_area=None, survey_schedule=None, consent_version=None):
    plot_identifiers = None
    try:
        inner_container = InnerContainer.objects.get(
            device_id=settings.DEVICE_ID, map_area=map_area)
    except InnerContainer.DoesNotExist:
        raise ValidationError("There are no plots sectioned for this machine.")
    else:
        plot_identifiers = inner_container.identifier_labels

    household_members = HouseholdMember.objects.filter(
        household_structure__household__plot__map_area=map_area,
        household_structure__household__plot__plot_identifier__in=plot_identifiers,
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
            try:
                SubjectConsent.objects.get(
                    version=consent_version, subject_identifier=household_member.subject_identifier)
                consented += 1
            except SubjectConsent.DoesNotExist:
                not_household_members.append(household_member)
    print(f'consented: {consented}')
    members_to_delete = len(not_household_members)
    for household_member in not_household_members:
        HouseholdHeadEligibility.objects.filter(
            household_member=household_member).delete()
        try:
            AbsentMember.objects.filter(
                household_member=household_member).delete()
        except HouseholdLogRequired:
            print(
                f'Failed because of HouseholdLogRequired for {household_member}, {household_member.subject_identifier}')
        DeceasedMember.objects.filter(
            household_member=household_member).delete()
        MovedMember.objects.filter(
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
                f'Failed to delete enrollment checklist for {household_member}, {household_member.subject_identifier}')
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


def ignore_delete_transactions():
    OutgoingTransaction.objects.filter(
        action='D', created__date=datetime.today().date()).update(
            is_ignored=True, is_consumed_server=True)


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
        ignore_delete_transactions()
        self.stdout.write(self.style.SUCCESS('Succefully deleted members.'))
