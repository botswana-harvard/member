from django.db import models


class HouseholdMemberManager(models.Manager):

    def get_by_natural_key(self, subject_identifier_as_pk, survey, household_identifier, plot_identifier):
        return self.get(
            subject_identifier_as_pk=subject_identifier_as_pk,
            household_structure__survey=survey,
            household_structure__household__household_identifier=household_identifier,
            household_structure__household__plot__plot_identifier=household_identifier
        )


class MemberEntryManager(models.Manager):

    def get_by_natural_key(self, report_datetime, subject_identifier_as_pk, survey,
                           household_identifier, plot_identifier):
        return self.get(
            report_datetime=report_datetime,
            household_member__household_structure__survey=survey,
            household_member__household_structure__household__household_identifier=household_identifier,
            household_member__household_structure__household__plot__plot_identifier=plot_identifier,
        )
