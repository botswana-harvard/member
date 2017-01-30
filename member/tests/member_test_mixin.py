from dateutil.relativedelta import relativedelta
from faker import Faker
from model_mommy import mommy
from random import choice

from edc_base_test.exceptions import TestMixinError
from edc_constants.constants import MALE, FEMALE, NOT_APPLICABLE, YES, NO
from edc_registration.models import RegisteredSubject

from household.models import HouseholdStructure
from survey.site_surveys import site_surveys

from ..constants import HEAD_OF_HOUSEHOLD
from ..models import HouseholdMember, EnrollmentChecklist


fake = Faker()


class MemberTestMixin:

    def setUp(self):
        super().setUp()
        self.study_site = '40'

    def _make_ready(self, household_structure, make_hoh=None, **options):
        """Returns household_structure after adding representative
        eligibility.

        For internal use.
        """
        make_hoh = True if make_hoh is None else make_hoh

        household_log_entry = (
            household_structure.householdlog.
            householdlogentry_set.all().order_by('report_datetime').last())
        # add representative eligibility
        mommy.make_recipe(
            'member.representativeeligibility',
            report_datetime=household_log_entry.report_datetime,
            household_structure=household_structure)
        if make_hoh:
            first_name = fake.first_name()
            last_name = fake.last_name()
            gender = options.get('gender', choice([MALE, FEMALE]))
            household_member = mommy.make_recipe(
                'member.householdmember',
                household_structure=household_structure,
                report_datetime=household_log_entry.report_datetime,
                first_name=first_name,
                initials=first_name[0] + last_name[0],
                gender=gender,
                relation=HEAD_OF_HOUSEHOLD)
            mommy.make_recipe(
                'member.householdheadeligibility',
                report_datetime=household_log_entry.report_datetime,
                household_member=household_member)
        household_structure = HouseholdStructure.objects.get(
            pk=household_structure.pk)
        return household_structure

    def make_household_ready_for_enumeration(self, make_hoh=None,
                                             survey_schedule=None, **options):
        """Returns household_structure after adding representative
        eligibility.

        By default returns the household_structure of the first
        survey_schedule.

        * survey_schedule: a survey schedule object. Default: first
          survey_schedule from `site_surveys.get_survey_schedules`.
        """

        options.update(attempts=options.get('attempts', 1))
        if 'report_datetime' not in options:
            options['report_datetime'] = (
                site_surveys.get_survey_schedules()[0].start)
        household_structure = self.make_household_structure(
            survey_schedule=survey_schedule,
            **options)
        return self._make_ready(
            household_structure, make_hoh=make_hoh, **options)

    def get_next_household_structure_ready(self, household_structure,
                                           make_hoh=None, **options):
        """Returns the next `household_structure` or None relative to
        given household_structure.

            * household_structure: uses this instance to find the
              `next` household_structure.
            Adds logs and returns the the `next`  household_structure
            or None.

        Same as `make_household_ready_for_enumeration` except uses the
        given `household_structure`.
        """
        options.update(attempts=options.get('attempts', 1))
        if household_structure.next:
            survey_schedule = household_structure.next.survey_schedule_object
            if household_structure.next.householdlog.householdlogentry_set.all().count() > 0:
                raise TestMixinError(
                    'Household structure already "ready" for '
                    'enumeration. Got {}'.format(
                        household_structure.next))
            self._add_attempts(
                household_structure.next,
                survey_schedule=survey_schedule,
                **options)
            return self._make_ready(
                household_structure.next, make_hoh=make_hoh, **options)
        return None

    def make_household_ready_for_last(
            self, household_structure, make_hoh=None, **options):
        """Returns the `household_structure` for the next survey.

        Same as `make_household_ready_for_enumeration` except uses the given
        `household_structure`.
        """
        options.update(attempts=options.get('attempts', 1))
        survey_schedule = household_structure.survey_schedule_object.last
        return self._make_ready(
            household_structure, survey_schedule=survey_schedule,
            make_hoh=make_hoh, **options)

    def make_enumerated_household_with_male_member(self, survey_schedule=None):
        household_structure = self.make_household_ready_for_enumeration(
            make_hoh=True, survey_schedule=survey_schedule, gender=MALE)
        return household_structure

    def add_household_member(self, household_structure, **options):
        """Returns a household member that is by default is
        an eligible household member.

        Survey schedule is always that of the household structure.
        """

        first_name = fake.first_name()
        last_name = fake.last_name()
        options.update(first_name=options.get('first_name', first_name))
        options.update(
            initials=options.get('initials', first_name[0] + last_name[0]))

        if not options.get('report_datetime'):
            last = (household_structure.householdlog.
                    householdlogentry_set.all().order_by(
                        'report_datetime').last())
            try:
                options.update(report_datetime=last.report_datetime)
            except AttributeError:
                options.update(
                    report_datetime=household_structure.report_datetime)

        household_member = mommy.make_recipe(
            'member.householdmember',
            household_structure=household_structure,
            **options)

        if not options and not household_member.eligible_member:
            raise TestMixinError(
                'Default values expected to create an eligible '
                'household member. Got eligible_member=False. Did '
                'someone mess with the mommy recipe?')
        return household_member

    def update_household_member_clone(self, household_member):
        """Returns a household_member after updating values not
        carried forward when cloned.

        household_member.eligible_member is True after save().
        """
        household_member.present_today = YES
        household_member.inability_to_participate = NOT_APPLICABLE
        household_member.study_resident = YES
        household_member.personal_details_changed = NO
        household_member.user_created = 'erikvw'
        household_member.save()
        return HouseholdMember.objects.get(pk=household_member.pk)

    def add_enrollment_checklist(self, household_member, **options):
        """Returns a household_member after adding an
        enrollment_checklist.
        """
#         report_datetime = options.get(
#             'report_datetime',
#             household_member.survey_schedule_object.start)
        report_datetime = options.get(
            'report_datetime',
            household_member.report_datetime)
        if 'age_in_years' in options:
            raise TestMixinError('Invalid option. Got \'age_in_years\'')

        try:
            registered_subject = RegisteredSubject.objects.get(
                registration_identifier=household_member.internal_identifier)
        except RegisteredSubject.DoesNotExist:
            options.update(
                dob=options.get('dob', (report_datetime - relativedelta(
                    years=household_member.age_in_years)).date()))
        else:
            options.update(
                dob=options.get('dob', registered_subject.dob))
        options.update(
            report_datetime=report_datetime,
            initials=options.get('initials', household_member.initials),
            gender=options.get('gender', household_member.gender))

        mommy_options = {k: v for k, v in options.items() if k in [
            f.name for f in EnrollmentChecklist._meta.get_fields()]}

        mommy.make_recipe(
            'member.enrollmentchecklist',
            household_member=household_member,
            **mommy_options)
        return HouseholdMember.objects.get(pk=household_member.pk)

    def make_absent_member(self, household_member, **options):
        """Returns a household member after adding a absent member
        report.
        """
        options.update(report_datetime=options.get(
            'report_datetime',
            household_member.report_datetime))
        mommy.make_recipe(
            'member.absentmember',
            household_member=household_member, **options)
        return HouseholdMember.objects.get(pk=household_member.pk)

    def make_refused_member(self, household_member, **options):
        """Returns a household member after adding a refused member
        report.
        """
        options.update(report_datetime=options.get(
            'report_datetime',
            household_member.report_datetime))
        mommy.make_recipe(
            'member.refusedmember',
            household_member=household_member, **options)
        return HouseholdMember.objects.get(pk=household_member.pk)

    def make_undecided_member(self, household_member, **options):
        """Returns a household member after adding a undecided
        member report.
        """
        options.update(report_datetime=options.get(
            'report_datetime',
            household_member.report_datetime))
        mommy.make_recipe(
            'member.undecidedmember',
            household_member=household_member, **options)
        return HouseholdMember.objects.get(pk=household_member.pk)

    def make_moved_member(self, household_member, **options):
        """Returns a household member after adding a undecided
        member report.
        """
        options.update(report_datetime=options.get(
            'report_datetime',
            household_member.report_datetime))
        mommy.make_recipe(
            'member.movedmember',
            household_member=household_member, **options)
        return HouseholdMember.objects.get(pk=household_member.pk)

    def make_deceased_member(self, household_member, **options):
        """Returns a household member after adding a deceased member
        report.
        """
        options.update(report_datetime=options.get(
            'report_datetime',
            household_member.report_datetime))
        mommy.make_recipe(
            'member.deceasedmember',
            household_member=household_member, **options)
        return HouseholdMember.objects.get(pk=household_member.pk)

    def make_htc_member(self, household_member, **options):
        """Returns a household member after adding a HTC member
        report.
        """
        options.update(report_datetime=options.get(
            'report_datetime',
            household_member.report_datetime))
        mommy.make_recipe(
            'member.htcmember',
            household_member=household_member, **options)
        return HouseholdMember.objects.get(pk=household_member.pk)
