from django.db import models


class HouseholdMemberManager(models.Manager):

    to_reference_model = ['household_member', 'household_structure', 'household', 'plot']

    def get_by_natural_key(self, subject_identifier_as_pk, survey, household_identifier, plot_identifier):
        return self.get(
            subject_identifier_as_pk=subject_identifier_as_pk,
            household_structure__survey=survey,
            household_structure__household__household_identifier=household_identifier,
            household_structure__household__plot__plot_identifier=household_identifier
        )


class RefusedMemberHistoryManager(models.Manager):

    def get_by_natural_key(self, transaction):
        return self.get(transaction=transaction)


class HtcMemberHistoryManager(models.Manager):

    def get_by_natural_key(self, transaction):
        self.get(transaction=transaction)
