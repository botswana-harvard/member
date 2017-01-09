from django.apps import apps as django_apps
from django.db import models

from ...choices import RELATIONS
from ...constants import HEAD_OF_HOUSEHOLD
from ...exceptions import EnumerationRepresentativeError


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
                    '{} is already head of household.'.format(household_member.first_name), 'relation')
        except self.__class__.DoesNotExist:
            household_member = None
#             if self.relation != HEAD_OF_HOUSEHOLD and not self.age_in_years >= 18:
#                 raise EnumerationRepresentativeError(
#                     'Enumeration blocked. Please first add one '
#                     'member over 18 who is the head of household.')
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

    @property
    def common_clean_exceptions(self):
        common_clean_exceptions = super().common_clean_exceptions
        common_clean_exceptions.extend([EnumerationRepresentativeError])
        return common_clean_exceptions

    class Meta:
        abstract = True
