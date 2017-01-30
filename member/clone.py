from django.core.exceptions import ObjectDoesNotExist

from edc_base.utils import get_utcnow

from .exceptions import CloneError
from member.models.household_member.household_member import HouseholdMember


class Clone:

    def __init__(self, household=None, survey_schedule=None, report_datetime=None,
                 household_structure=None, create=None, now=None):
        """Clone household members for a new survey_schedule.

            * survey_schedule: adds new members for this survey_schedule.
        """
        create = True if create is None else create
        if household and household_structure:
            raise CloneError(
                'Ambiguous. Either specify household or household_structure, not both')
        if survey_schedule and household_structure:
            raise CloneError(
                'Ambiguous. Either specify survey_schedule or household_structure, not both')
        try:
            self.household = household_structure.household
            self.survey_schedule = household_structure.survey_schedule_object
        except AttributeError:
            self.household = household
            self.survey_schedule = survey_schedule
        self.report_datetime = report_datetime or get_utcnow()
        self.members = self.clone(create=create)

    def clone(self, create=None):
        """Returns a queryset or list of household_members, depending on `create`.

            * create: Default: True

        If created=True, returns a QuerySet, else a list of non-persisted
        model instances.
        """
        household_members = []
        self.safe_to_clone_or_raise()
        household_structure = self.household.householdstructure_set.get(
            survey_schedule=self.survey_schedule.field_value)

        survey_schedule = self.survey_schedule.previous
        while survey_schedule:
            try:
                previous_household_structure = self.household.householdstructure_set.get(
                    survey_schedule=survey_schedule.field_value)
            except ObjectDoesNotExist:
                survey_schedule = survey_schedule.previous
            except AttributeError:
                break
            else:
                previous_members = previous_household_structure.householdmember_set.all()
                for obj in previous_members:
                    new_obj = obj.clone(
                        household_structure=household_structure,
                        report_datetime=self.report_datetime,
                        user_created=household_structure.user_created)
                    if create:
                        new_obj.save()
                    else:
                        household_members.append(new_obj)
                if previous_members.count() > 0:
                    break
                else:
                    survey_schedule = survey_schedule.previous
        if create:
            return HouseholdMember.objects.filter(
                household_structure__household=self.household,
                survey_schedule=self.survey_schedule.field_value)
        return household_members

    def safe_to_clone_or_raise(self):
        current = self.household.householdstructure_set.get(
            survey_schedule=self.survey_schedule.field_value)
        if current.householdmember_set.all().count() > 0:
            raise CloneError(
                'Cannot clone household. Members already exist in '
                'household for {}.'.format(self.survey_schedule))
