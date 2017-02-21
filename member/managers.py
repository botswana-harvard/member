from django.db import models


class HouseholdMemberManager(models.Manager):

    def get_by_natural_key(self,
                           internal_identifier,
                           survey_schedule,
                           household_identifier,
                           plot_identifier):
        return self.get(
            internal_identifier=internal_identifier,
            household_structure__survey_schedule=survey_schedule,
            household_identifier=household_identifier,
            household_structure__household__plot__plot_identifier=plot_identifier
        )


class MemberEntryManager(models.Manager):

    def get_by_natural_key(self, report_datetime,
                           internal_identifier,
                           survey_schedule,
                           household_identifier,
                           plot_identifier):

        options = {
            'report_datetime': report_datetime,
            'household_member__internal_identifier':
            internal_identifier,
            'household_member__household_structure__survey_schedule':
            survey_schedule,
            'household_member__household_structure__household__household_identifier':
            household_identifier,
            'household_member__household_structure__household__plot__plot_identifier':
            plot_identifier
        }
        return self.get(**options)
