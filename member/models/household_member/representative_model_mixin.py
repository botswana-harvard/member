from django.apps import apps as django_apps
from django.core.exceptions import MultipleObjectsReturned
from django.db import models

from plot.utils import get_clinic_n_anonymous_plot

from ...choices import RELATIONS
from ...constants import HEAD_OF_HOUSEHOLD
from ...exceptions import EnumerationRepresentativeError


class RepresentativeModelMixin(models.Model):
    """Mixin that ensures enumeration cannot begin until a
    representative and HoH is identified.
    """

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
        # confirm RepresentativeEligibility exists ...
        plot_identifier = django_apps.get_app_config(
            'plot').anonymous_plot_identifier
        plot_type = 'anonymous'
        plot = get_clinic_n_anonymous_plot(
            plot_identifier=plot_identifier, plot_type=plot_type)
        if self.household_structure.household.plot != plot:
            try:
                RepresentativeEligibility = django_apps.get_model(
                    *'member.representativeeligibility'.split('.'))
                RepresentativeEligibility.objects.get(
                    household_structure=self.household_structure)
            except RepresentativeEligibility.DoesNotExist:
                if not self.cloned:
                    raise EnumerationRepresentativeError(
                        'Enumeration blocked. Please complete \'{}\' form first.'.format(
                            RepresentativeEligibility._meta.verbose_name))
            try:
                household_member = self.__class__.objects.get(
                    household_structure=self.household_structure,
                    relation=HEAD_OF_HOUSEHOLD)
                if (self.relation == HEAD_OF_HOUSEHOLD
                        and self.id != household_member.id):
                    raise EnumerationRepresentativeError(
                        '{} is already head of household.'.format(
                            household_member.first_name), 'relation')
            except self.__class__.DoesNotExist:
                household_member = None
            except MultipleObjectsReturned:
                # this condition should not occur!
                household_member = None
            # then expect HouseholdHeadEligibility to be added against
            # the member who has relation=HEAD_OF_HOUSEHOLD...
            # for all new instances
            if household_member and not self.id:
                try:
                    HouseholdHeadEligibility = django_apps.get_model(
                        *'member.householdheadeligibility'.split('.'))
                    HouseholdHeadEligibility.objects.get(
                        household_member=household_member)
                except HouseholdHeadEligibility.DoesNotExist:
                    raise EnumerationRepresentativeError(
                        'Further enumeration blocked. Please complete '
                        '\'{}\' form first.'.format(
                            HouseholdHeadEligibility._meta.verbose_name))
        # if all OK, add members as you like ...
        super().common_clean()

    @property
    def common_clean_exceptions(self):
        return super().common_clean_exceptions + [EnumerationRepresentativeError]

    class Meta:
        abstract = True
