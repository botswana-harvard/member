from datetime import datetime

from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from edc_base.utils import get_utcnow
from edc_constants.constants import ALIVE, REFUSED

from household.models import HouseholdStructure

from ..constants import NOT_ELIGIBLE, HEAD_OF_HOUSEHOLD, UNDECIDED, ABSENT

from .absent_member import AbsentMember
from .absent_member_entry import AbsentMemberEntry
from .enrollment_checklist import EnrollmentChecklist
from .enrollment_loss import EnrollmentLoss
from .household_head_eligibility import HouseholdHeadEligibility
from .household_member import HouseholdMember
from .htc_member import HtcMember
from .htc_member_history import HtcMemberHistory
from .refused_member import RefusedMember
from .refused_member_history import RefusedMemberHistory
from .undecided_member import UndecidedMember
from .undecided_member_entry import UndecidedMemberEntry


@receiver(post_delete, weak=False, dispatch_uid="refused_member_on_post_delete")
def refused_member_on_post_delete(sender, instance, using, **kwargs):
    """Delete refusal but first puts a copy into the history model."""
    if isinstance(instance, RefusedMember):
        # update the history model
        household_member = HouseholdMember.objects.using(using).get(
            pk=instance.household_member.pk)
        options = {'household_member': household_member,
                   'report_datetime': instance.report_datetime,
                   'survey': instance.survey,
                   'refusal_date': instance.refusal_date,
                   'reason': instance.reason,
                   'reason_other': instance.reason_other}
        RefusedMemberHistory.objects.using(using).create(**options)


@receiver(post_delete, weak=False, dispatch_uid="htc_member_on_post_delete")
def htc_member_on_post_delete(sender, instance, using, **kwargs):
    """Delete HtcMember on change of member status from HTC but first puts a
       copy into the history model."""
    if isinstance(instance, HtcMember):
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
        HtcMemberHistory.objects.using(using).create(**options)


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


@receiver(post_save, weak=False, sender=HouseholdMember, dispatch_uid="household_member_on_post_save")
def household_member_on_post_save(sender, instance, raw, created, using, **kwargs):
    """Updates enumerated, eligible_members on household structure."""
    if not raw:
        instance.update_plot_on_post_save()
        instance.delete_deceased_member_on_post_save()
        # instance.update_or_create_member_status_model()
        model = None
        if instance.member_status == UNDECIDED:
            model = UndecidedMember
        elif instance.member_status == ABSENT:
            model = AbsentMember
        elif instance.member_status == REFUSED:
            model = RefusedMember
        if model:
            try:
                model.objects.get(household_member=instance)
            except model.DoesNotExist:
                model.objects.create(
                    report_datetime=get_utcnow(),
                    household_member=instance)
        try:
            # update household structure
            if not instance.household_structure.enumerated:
                instance.household_structure.enumerated = True
            eligible_members = False
            if HouseholdMember.objects.filter(
                    household_structure=instance.household_structure, eligible_member=True):
                eligible_members = True
            instance.household_structure.eligible_members = eligible_members
            instance.household_structure.save(update_fields=['enumerated', 'eligible_members'])
        except AttributeError as e:
            if 'household_structure' not in str(e):
                raise AttributeError(str(e))


@receiver(post_save, weak=False, dispatch_uid='subject_member_status_form_on_post_save')
def subject_member_status_form_on_post_save(sender, instance, raw, created, using, **kwargs):
    """Deletes the Enrollment checklist if it exists and sets the
    household member booleans accordingly."""
    if not raw:
        if isinstance(instance, (AbsentMember, UndecidedMember, RefusedMember)):
            # delete enrollment checklist
            EnrollmentChecklist.objects.using(using).filter(
                household_member=instance.household_member).delete()
            instance.household_member.enrollment_checklist_completed = False
            # update household member
            instance.household_member.reported = True  # because one of these forms is saved
            instance.household_member.enrollment_loss_completed = False
            instance.household_member.htc = False
            instance.household_member.refused_htc = False
            if isinstance(instance, AbsentMember):
                instance.household_member.undecided = False
                instance.household_member.refused = False
            elif isinstance(instance, UndecidedMember):
                instance.household_member.absent = False
                instance.household_member.refused = False
            elif isinstance(instance, RefusedMember):
                instance.household_member.refused = True
                instance.household_member.absent = False
                instance.household_member.undecided = False
            instance.household_member.save(using=using, update_fields=[
                'reported', 'undecided', 'absent', 'refused', 'enrollment_loss_completed',
                'enrollment_checklist_completed', 'htc', 'refused_htc', 'eligible_htc'
            ])


@receiver(post_save, weak=False, dispatch_uid='absent_member_entry_on_post_save')
def absent_member_entry_on_post_save(sender, instance, raw, created, using, **kwargs):
    """Increments visit attempts on the household member."""
    if not raw:
        if isinstance(instance, AbsentMemberEntry):
            if created:
                instance.absent_member.household_member.visit_attempts += 1
                instance.absent_member.household_member.save(
                    using=using, update_fields=['visit_attempts'])


@receiver(post_save, weak=False, dispatch_uid='undecided_member_entry_on_post_save')
def undecided_member_entry_on_post_save(sender, instance, raw, created, using, **kwargs):
    """Increments visit attempts on the household member."""
    if not raw:
        if isinstance(instance, UndecidedMemberEntry):
            if created:
                instance.undecided_member.household_member.visit_attempts += 1
                instance.undecided_member.household_member.save(
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


@receiver(post_save, weak=False, dispatch_uid='htc_member_on_post_save')
def htc_member_on_post_save(sender, instance, raw, created, using, **kwargs):
    """Updates household member to reflect the htc status."""
    if not raw:
        if isinstance(instance, HtcMember):
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
