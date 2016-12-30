import arrow

from django.apps import apps as django_apps
from django.db.models import Max
from django.db import models

from household.models import HouseholdLogEntry

from ...choices import RELATIONS
from ...constants import HEAD_OF_HOUSEHOLD
from ...exceptions import EnumerationRepresentativeError

from .utils import is_eligible_member


class RepresentativeModelMixin(models.Model):
    """Mixin that ensures enumeration cannot begin until a representative and HoH is identified."""

    relation = models.CharField(
        verbose_name="Relation to head of household",
        max_length=35,
        choices=RELATIONS,
        null=True,
        help_text="Relation to head of household")

    eligible_hoh = models.BooleanField(
        default=False,
        editable=False,
        help_text="updated by the head of household.")

    def common_clean(self):
        # TODO: the validations here may cause problems if importing the previous surveys members

        # confirm there is todays household log before editing household information.
        try:
            report_datetime = HouseholdLogEntry.objects.filter(
                household_log__household_structure=self.household_structure).aggregate(
                    Max('report_datetime')).get('report_datetime__max')
            HouseholdLogEntry.objects.get(
                household_log__household_structure=self.household_structure,
                report_datetime=report_datetime)
            r = arrow.Arrow.fromdatetime(report_datetime, report_datetime.tzinfo).to('utc')
            if not r.date() == arrow.utcnow().date():
                raise EnumerationRepresentativeError(
                    'Enumeration blocked. Please complete today\'s \'{}\' form first.'.format(
                        HouseholdLogEntry._meta.verbose_name))
        except HouseholdLogEntry.DoesNotExist:
            raise EnumerationRepresentativeError(
                'Enumeration blocked. Please complete today\'s \'{}\' form first.'.format(
                    HouseholdLogEntry._meta.verbose_name))

        # confirm RepresentativeEligibility exists ...
        try:
            RepresentativeEligibility = django_apps.get_model(
                *'member.representativeeligibility'.split('.'))
            RepresentativeEligibility.objects.get(
                household_structure=self.household_structure)
        except RepresentativeEligibility.DoesNotExist:
            raise EnumerationRepresentativeError(
                'Enumeration blocked. Please complete \'{}\' form first.'.format(
                    RepresentativeEligibility._meta.verbose_name))
        # then expect the first added member to be the HEAD_OF_HOUSEHOLD ...
        try:
            household_member = self.__class__.objects.get(
                household_structure=self.household_structure,
                relation=HEAD_OF_HOUSEHOLD, eligible_member=True)
            if self.relation == HEAD_OF_HOUSEHOLD and self.id != household_member.id:
                raise EnumerationRepresentativeError(
                    'Only one member may be the head of household. {} is already '
                    'head of household. Got {}'.format(household_member, self))
        except self.__class__.DoesNotExist:
            household_member = None
            if self.relation != HEAD_OF_HOUSEHOLD or not is_eligible_member(self):
                raise EnumerationRepresentativeError(
                    'Enumeration blocked. Please first add one eligible '
                    'member who is the head of household.')
        # then expect HouseholdHeadEligibility to be added against the member who has relation=HEAD_OF_HOUSEHOLD...
        # for all new instances
        if household_member and not self.id:
            try:
                HouseholdHeadEligibility = django_apps.get_model(
                    *'member.householdheadeligibility'.split('.'))
                HouseholdHeadEligibility.objects.get(household_member=household_member)
            except HouseholdHeadEligibility.DoesNotExist:
                raise EnumerationRepresentativeError(
                    'Further enumeration blocked. Please complete \'{}\' form first.'.format(
                        HouseholdHeadEligibility._meta.verbose_name))
        # if all OK, add members as you like ...
        super().common_clean()

    class Meta:
        abstract = True
