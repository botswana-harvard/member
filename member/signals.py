from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .constants import HEAD_OF_HOUSEHOLD

from .models import (
    AbsentMember, EnrollmentChecklist, EnrollmentLoss,
    HouseholdHeadEligibility, HouseholdMember,
    RefusedMember, UndecidedMember, DeceasedMember, MovedMember)


@receiver(post_save, weak=False, sender=HouseholdMember,
          dispatch_uid="household_member_on_post_save")
def household_member_on_post_save(sender, instance, raw, created, using, **kwargs):
    """Updates enumerated, eligible_members on household structure.
    """
    if not raw:
        if created:
            if not instance.household_structure.enumerated:
                instance.household_structure.enumerated = True
                instance.household_structure.enumerated_datetime = instance.report_datetime
                instance.household_structure.save()
        if not instance.eligible_member:
            EnrollmentChecklist.objects.filter(
                household_member=instance).delete()


@receiver(post_delete, weak=False, sender=HouseholdMember,
          dispatch_uid="household_member_on_post_delete")
def household_member_on_post_delete(sender, instance, using, **kwargs):
    if not instance.household_structure.householdmember_set.exclude(
            id=instance.id).exists():
        instance.household_structure.enumerated = False
        instance.household_structure.enumerated_datetime = None
        instance.household_structure.save()


@receiver(post_save, weak=False, sender=HouseholdHeadEligibility,
          dispatch_uid='household_head_eligibility_on_post_save')
def household_head_eligibility_on_post_save(
        sender, instance, raw, created, using, **kwargs):
    if not raw:
        if instance.household_member.relation == HEAD_OF_HOUSEHOLD:
            instance.household_member.eligible_hoh = True
            instance.household_member.save()


@receiver(post_save, weak=False, sender=EnrollmentLoss,
          dispatch_uid="enrollment_loss_on_post_save")
def enrollment_loss_on_post_save(sender, instance, raw, created, using, **kwargs):
    if not raw:
        instance.household_member.enrollment_loss_completed = True
        instance.household_member.save()


@receiver(post_delete, weak=False, sender=EnrollmentLoss,
          dispatch_uid="enrollment_loss_on_post_delete")
def enrollment_loss_on_post_delete(sender, instance, using, **kwargs):
    instance.household_member.enrollment_loss_completed = False
    instance.household_member.save()


@receiver(post_save, weak=False, sender=AbsentMember,
          dispatch_uid="absent_member_on_post_save")
def absent_member_on_post_save(sender, instance, raw, created, using, **kwargs):
    if not raw:
        if created:
            instance.household_member.visit_attempts += 1
        instance.household_member.absent = True
        instance.household_member.save()


@receiver(post_delete, weak=False, sender=AbsentMember,
          dispatch_uid="absent_member_on_post_delete")
def absent_member_on_post_delete(sender, instance, using, **kwargs):
    instance.household_member.visit_attempts -= 1
    if instance.household_member.visit_attempts < 0:
        instance.household_member.visit_attempts = 0
    if instance.household_member.absentmember_set.all().count() == 0:
        instance.household_member.absent = False
    instance.household_member.save()


@receiver(post_save, weak=False, sender=UndecidedMember,
          dispatch_uid="undecided_member_on_post_save")
def undecided_member_on_post_save(sender, instance, raw, created, using, **kwargs):
    if not raw:
        if created:
            instance.household_member.visit_attempts += 1
        instance.household_member.undecided = True
        instance.household_member.save()


@receiver(post_delete, weak=False, sender=AbsentMember,
          dispatch_uid="undecided_member_on_post_delete")
def undecided_member_on_post_delete(sender, instance, using, **kwargs):
    instance.household_member.visit_attempts -= 1
    if instance.household_member.visit_attempts < 0:
        instance.household_member.visit_attempts = 0
    if instance.household_member.undecidedmember_set.all().count() == 0:
        instance.household_member.undecided = False
    instance.household_member.save()


@receiver(post_delete, weak=False, sender=RefusedMember,
          dispatch_uid="refused_member_on_post_delete")
def refused_member_on_post_delete(sender, instance, using, **kwargs):
    instance.household_member.visit_attempts -= 1
    if instance.household_member.visit_attempts < 0:
        instance.household_member.visit_attempts = 0
    instance.household_member.refused = False
    instance.household_member.save()


@receiver(post_save, weak=False, sender=RefusedMember,
          dispatch_uid="refused_member_on_post_save")
def refused_member_on_post_save(sender, instance, raw, created, using, **kwargs):
    if not raw:
        if created:
            instance.household_member.visit_attempts += 1
        instance.household_member.refused = True
        instance.household_member.save()


@receiver(post_delete, weak=False, sender=DeceasedMember,
          dispatch_uid="deceased_member_on_post_delete")
def deceased_member_on_post_delete(sender, instance, using, **kwargs):
    instance.household_member.visit_attempts -= 1
    if instance.household_member.visit_attempts < 0:
        instance.household_member.visit_attempts = 0
    instance.household_member.deceased = False
    instance.household_member.save()


@receiver(post_save, weak=False, sender=DeceasedMember,
          dispatch_uid="deceased_member_on_post_save")
def deceased_member_on_post_save(sender, instance, raw, created, using, **kwargs):
    if not raw:
        if created:
            instance.household_member.visit_attempts += 1
        instance.household_member.deceased = True
        instance.household_member.save()


@receiver(post_save, weak=False, sender=MovedMember,
          dispatch_uid="moved_member_on_post_save")
def moved_member_on_post_save(sender, instance, raw, created, using, **kwargs):
    if not raw:
        if created:
            instance.household_member.visit_attempts += 1
        instance.household_member.moved = True
        instance.household_member.save()


@receiver(post_delete, weak=False, sender=MovedMember,
          dispatch_uid="moved_member_on_post_delete")
def moved_member_on_post_delete(sender, instance, using, **kwargs):
    instance.household_member.visit_attempts -= 1
    if instance.household_member.visit_attempts < 0:
        instance.household_member.visit_attempts = 0
    if instance.household_member.absentmember_set.all().count() == 0:
        instance.household_member.moved = False
    instance.household_member.save()
