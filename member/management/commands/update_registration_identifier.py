from django.conf import settings
from django.core.management.base import BaseCommand

from edc_map.models import InnerContainer
from edc_registration.models import RegisteredSubject

from ...models import HouseholdMember


def to_string(value):
    """Returns a string.

    Converts UUID to string using .hex.
    """
    try:
        value = str(value.hex)
    except AttributeError:
        pass
    return value


class Command(BaseCommand):

    help = 'Update registration identifiers.'

    def add_arguments(self, parser):
        parser.add_argument('map_area', type=str, help='map_area')

    def handle(self, *args, **options):
        count = 0
        map_area = options['map_area']
        try:
            inner_container = InnerContainer.objects.get(
                map_area=map_area, device_id=settings.DEVICE_ID)
        except InnerContainer.DoesNotExist:
            pass
        else:
            plot_identifiers = inner_container.identifier_labels
            household_members = HouseholdMember.objects.filter(
                household_structure__household__plot__map_area=map_area,
                household_structure__household__plot__plot_identifier__in=plot_identifiers)
            subject_identifier_internal_identifier = {}
            for household_member in household_members:
                subject_identifier_internal_identifier[
                    household_member.subject_identifier] = household_member.internal_identifier
            for subject_identifier, internal_identifier in subject_identifier_internal_identifier.items():
                try:
                    registered_subject = RegisteredSubject.objects.get(
                        subject_identifier=subject_identifier, registration_identifier__isnull=True)
                except RegisteredSubject.DoesNotExist:
                    pass
                else:
                    registration_value = to_string(internal_identifier)
                    registered_subject.registration_identifier = registration_value
                    registered_subject.save()
                    count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'{count} {registered_subject.first_name} registration identifier Updated machine {settings.DEVICE_ID}'))
            self.stdout.write(
                self.style.SUCCESS('Successfully update registration identifiers members.'))
