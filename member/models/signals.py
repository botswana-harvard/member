from datetime import datetime

from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from edc_constants.constants import ALIVE

from bcpp_household.models import HouseholdStructure

from ..constants import NOT_ELIGIBLE, HEAD_OF_HOUSEHOLD

from .enrollment_checklist import EnrollmentChecklist
from .enrollment_loss import EnrollmentLoss
from .household_head_eligibility import HouseholdHeadEligibility
from .household_member import HouseholdMember
from .subject_absentee import SubjectAbsentee, SubjectAbsenteeEntry
from .subject_htc import SubjectHtc, SubjectHtcHistory
from .subject_refusal import SubjectRefusal, SubjectRefusalHistory
from .subject_undecided import SubjectUndecided, SubjectUndecidedEntry


@receiver(post_delete, weak=False, dispatch_uid="subject_refusal_on_post_delete")
def subject_refusal_on_post_delete(sender, instance, using, **kwargs):
    """Delete refusal but first puts a copy into the history model."""
    if isinstance(instance, SubjectRefusal):
        # update the history model
        household_member = HouseholdMember.objects.using(using).get(
            pk=instance.household_member.pk)
        options = {'household_member': household_member,
                   'report_datetime': instance.report_datetime,
                   'survey': instance.survey,
                   'refusal_date': instance.refusal_date,
                   'reason': instance.reason,
                   'reason_other': instance.reason_other}
        SubjectRefusalHistory.objects.using(using).create(**options)


@receiver(post_delete, weak=False, dispatch_uid="subject_htc_on_post_delete")
def subject_htc_on_post_delete(sender, instance, using, **kwargs):
    """Delete SubjectHtc on change of member status from HTC but first puts a
       copy into the history model."""
    if isinstance(instance, SubjectHtc):
        # update the history model
        household_member = HouseholdMember.objects.using(using).get(
            pk=instance.household_member.pk)
        options = {'household_member': household_member,
                   'survey': instance.survey,
                   'report_datetime': instance.report_datetime,
                   'tracking_identifier': instance.tracking_identifier,
                   'offered': instance.offered,
                   'accepted': instance.accepted,
                   'refusal_reason': instance.refusal_reason,
                   'referred': instance.referred,
                   'referral_clinic': instance.referral_clinic,
                   'comment': instance.comment}
        SubjectHtcHistory.objects.using(using).create(**options)


@receiver(post_delete, weak=False, dispatch_uid="enrollment_checklist_on_post_delete")
def enrollment_checklist_on_post_delete(sender, instance, using, **kwargs):
    """Resets household member values to before the enrollment checklist was entered.

    A number of places check for these values including URLs in templates."""
    if isinstance(instance, EnrollmentChecklist):
        # re-save the member to recalc the member_status
        # If this gets deleted, then the process must be started again from BHS_SCREEN
        # household_member = HouseholdMember.objects.using(using).get(pk=instance.household_member.pk)
        try:
            EnrollmentLoss.objects.using(using).get(
                household_member=instance.household_member).delete(using=using)
        except EnrollmentLoss.DoesNotExist:
            pass


@receiver(post_save, weak=False, dispatch_uid="enrollment_checklist_on_post_save")
def enrollment_checklist_on_post_save(sender, instance, raw, created, using, **kwargs):
    """Updates household_member and removes the Loss form if it exists."""
    if not raw:
        if isinstance(instance, EnrollmentChecklist):
            instance.household_member.eligible_subject = False
            instance.household_member.enrollment_checklist_completed = True
            instance.household_member.enrollment_loss_completed = False
            if instance.is_eligible:
                instance.household_member.eligible_subject = True
                try:
                    EnrollmentLoss.objects.using(using).get(
                        household_member=instance.household_member).delete(using=using)
                except EnrollmentLoss.DoesNotExist:
                    pass
                instance.household_member.enrollment_loss_completed = False
            else:
                if instance.loss_reason:
                    instance.household_member.member_status = NOT_ELIGIBLE  # to allow edit of enrollment loss only
                    instance.household_member.enrollment_loss_completed = True
                    try:
                        enrollment_loss = EnrollmentLoss.objects.using(using).get(
                            household_member=instance.household_member)
                        enrollment_loss.report_datetime = instance.report_datetime
                        enrollment_loss.reason = ';'.join(instance.loss_reason)
                        enrollment_loss.save(using=using, update_fields=['report_datetime', 'reason'])
                    except EnrollmentLoss.DoesNotExist:
                        EnrollmentLoss.objects.using(using).create(
                            household_member=instance.household_member,
                            report_datetime=instance.report_datetime,
                            reason=';'.join(instance.loss_reason))
            instance.household_member.save(using=using, update_fields=['eligible_subject',
                                                                       'enrollment_checklist_completed',
                                                                       'enrollment_loss_completed',
                                                                       'member_status',
                                                                       'eligible_htc'])


@receiver(pre_save, weak=False, dispatch_uid="household_member_on_pre_save")
def household_member_on_pre_save(sender, instance, raw, using, **kwargs):
    """"Updates the hiv history flag for the dashboard."""
    if not raw:
        if isinstance(instance, HouseholdMember):
            instance.update_hiv_history_on_pre_save(using, **kwargs)


def create_subject_undecided(using, instance=None, household_structure=None):
    if instance.absent or (instance.present_today == 'No' and instance.survival_status == ALIVE):
        try:
            SubjectAbsentee.objects.using(using).get(household_member=instance)
        except SubjectAbsentee.DoesNotExist:
            SubjectAbsentee.objects.using(using).create(
                report_datetime=datetime.today(),
                registered_subject=instance.registered_subject,
                household_member=instance,
                survey=household_structure.survey,
            )


@receiver(post_save, weak=False, dispatch_uid="household_member_on_post_save")
def household_member_on_post_save(sender, instance, raw, created, using, **kwargs):
    """Updates enumerated, eligible_members on household structure."""
    if not raw:
        if isinstance(instance, HouseholdMember):
            # update registered subject
            instance.update_registered_subject_on_post_save(using, **kwargs)
            members = HouseholdMember.objects.filter(
                household_structure__household__plot=instance.household_structure.household.plot).count()
            instance.update_plot_on_post_save(instance, members)

            try:
                household_structure = HouseholdStructure.objects.using(using).get(
                    pk=instance.household_structure.pk)
                # create subject absentee if member_status == ABSENT otherwise delete the entries
                create_subject_undecided(using, instance, household_structure)
                # create subject undecided if member_status == UNDECIDED otherwise delete the entries
                if instance.undecided:
                    try:
                        SubjectUndecided.objects.using(using).get(household_member=instance)
                    except SubjectUndecided.DoesNotExist:
                        SubjectUndecided.objects.using(using).create(
                            report_datetime=datetime.today(),
                            registered_subject=instance.registered_subject,
                            household_member=instance,
                            survey=household_structure.survey,
                        )
                # update household structure
                if not household_structure.enumerated:
                    household_structure.enumerated = True
                household_structure.eligible_members = False
                if HouseholdMember.objects.using(using).filter(
                        household_structure=household_structure, eligible_member=True):
                    household_structure.eligible_members = True
                household_structure.save(using=using, update_fields=['enumerated', 'eligible_members'])
            except AttributeError:
                # expect a household_structure pk exception if coming from bcpp_clinic
                pass

            """1. Delete death form if exists when survival status changes from Dead to Alive """
            instance.delete_subject_death_on_post_save()


@receiver(post_save, weak=False, dispatch_uid='subject_member_status_form_on_post_save')
def subject_member_status_form_on_post_save(sender, instance, raw, created, using, **kwargs):
    """Deletes the Enrollment checklist if it exists and sets the
    household member booleans accordingly."""
    if not raw:
        if isinstance(instance, (SubjectAbsentee, SubjectUndecided, SubjectRefusal)):
            # delete enrollment checklist
            EnrollmentChecklist.objects.using(using).filter(
                household_member=instance.household_member).delete()
            instance.household_member.enrollment_checklist_completed = False
            # update household member
            instance.household_member.reported = True  # because one of these forms is saved
            instance.household_member.enrollment_loss_completed = False
            instance.household_member.htc = False
            instance.household_member.refused_htc = False
            if isinstance(instance, SubjectAbsentee):
                instance.household_member.undecided = False
                instance.household_member.refused = False
            elif isinstance(instance, SubjectUndecided):
                instance.household_member.absent = False
                instance.household_member.refused = False
            elif isinstance(instance, SubjectRefusal):
                instance.household_member.refused = True
                instance.household_member.absent = False
                instance.household_member.undecided = False
            instance.household_member.save(using=using, update_fields=[
                'reported', 'undecided', 'absent', 'refused', 'enrollment_loss_completed',
                'enrollment_checklist_completed', 'htc', 'refused_htc', 'eligible_htc'
            ])


@receiver(post_save, weak=False, dispatch_uid='subject_absentee_entry_on_post_save')
def subject_absentee_entry_on_post_save(sender, instance, raw, created, using, **kwargs):
    """Increments visit attempts on the household member."""
    if not raw:
        if isinstance(instance, SubjectAbsenteeEntry):
            if created:
                instance.subject_absentee.household_member.visit_attempts += 1
                instance.subject_absentee.household_member.save(
                    using=using, update_fields=['visit_attempts'])


@receiver(post_save, weak=False, dispatch_uid='subject_undecided_entry_on_post_save')
def subject_undecided_entry_on_post_save(sender, instance, raw, created, using, **kwargs):
    """Increments visit attempts on the household member."""
    if not raw:
        if isinstance(instance, SubjectUndecidedEntry):
            if created:
                instance.subject_undecided.household_member.visit_attempts += 1
                instance.subject_undecided.household_member.save(
                    using=using, update_fields=['visit_attempts'])


@receiver(post_save, weak=False, dispatch_uid='base_household_member_consent_on_post_save')
def base_household_member_consent_on_post_save(sender, instance, raw, created, using, **kwargs):
    """Confirms registered subject info for all child models
    of this base class."""
    if not raw:
        try:
            instance.confirm_registered_subject_pk_on_post_save(using)
        except AttributeError:
            pass


@receiver(post_save, weak=False, dispatch_uid='subject_htc_on_post_save')
def subject_htc_on_post_save(sender, instance, raw, created, using, **kwargs):
    """Updates household member to reflect the htc status."""
    if not raw:
        if isinstance(instance, SubjectHtc):
            if instance.accepted == 'No':
                instance.household_member.htc = False
                instance.household_member.refused_htc = True
            else:
                instance.household_member.htc = True
                instance.household_member.refused_htc = False
            instance.household_member.save(
                using=using,
                update_fields=['htc', 'refused_htc'])


@receiver(pre_save, weak=False, dispatch_uid='household_head_eligibility_on_pre_save')
def household_head_eligibility_on_pre_save(sender, instance, raw, using, **kwargs):
    if not raw:
        if isinstance(instance, HouseholdHeadEligibility):
            previous_head = HouseholdMember.objects.filter(
                household_structure=instance.household_member.household_structure,
                relation=HEAD_OF_HOUSEHOLD).exclude(id=instance.household_member.id)
            if previous_head.exists():
                previous_head = previous_head[0]
                previous_head.eligible_hoh = False
                previous_head.relation = 'UNKNOWN'
                previous_head.save(using=using, update_fields=['relation', 'eligible_hoh'])


@receiver(post_save, weak=False, dispatch_uid='household_head_eligibility_on_post_save')
def household_head_eligibility_on_post_save(sender, instance, raw, created, using, **kwargs):
    if not raw:
        if isinstance(instance, HouseholdHeadEligibility):
            instance.household_member.eligible_hoh = True
            instance.household_member.save(using=using, update_fields=['relation', 'eligible_hoh'])
