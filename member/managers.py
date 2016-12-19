from django.db import models

from bcpp.manager_mixins import BcppSubsetManagerMixin


class HouseholdMemberManager(BcppSubsetManagerMixin, models.Manager):

    to_reference_model = ['household_member', 'household_structure', 'household', 'plot']

    def get_by_natural_key(self, household_identifier, survey_name, subject_identifier_as_pk):
        return self.get(
            household_member__household_structure__household__household_identifier=household_identifier,
            household_member__subject_identifier_as_pk=subject_identifier_as_pk)


class RefusedMemberHistoryManager(BcppSubsetManagerMixin, models.Manager):

    def get_by_natural_key(self, transaction):
        return self.get(transaction=transaction)


class HtcMemberHistoryManager(HouseholdMemberManager, models.Manager):

    def get_by_natural_key(self, transaction):
        self.get(transaction=transaction)
