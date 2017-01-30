from django.db import models
from django_crypto_fields.fields import EncryptedTextField

from edc_base.model.models import HistoricalRecords, BaseUuidModel
from edc_constants.choices import YES_NO_UNKNOWN

from ..managers import MemberEntryManager

from .model_mixins import HouseholdMemberModelMixin


class MovedMember(HouseholdMemberModelMixin, BaseUuidModel):

    """A model completed by the user to indicate a subject has
    moved from the household and or community.
    """

    moved_household = models.CharField(
        max_length=7,
        verbose_name='Has the participant moved out of the household where last seen',
        choices=YES_NO_UNKNOWN,
        null=True,
        blank=False,
        help_text=""
    )

    moved_community = models.CharField(
        max_length=7,
        verbose_name='Has the participant moved out of the community',
        choices=YES_NO_UNKNOWN,
        null=True,
        blank=False,
        help_text=""
    )

    new_community = models.CharField(
        max_length=50,
        verbose_name='If the participant has moved, provide the name of the new community',
        null=True,
        blank=True,
        help_text="If moved out of the community, provide a new community name or \'UNKNOWN\'"
    )

    update_locator = models.CharField(
        max_length=7,
        verbose_name='Has the locator information changed',
        choices=YES_NO_UNKNOWN,
        null=True,
        blank=False,
        help_text=('If YES, please enter the changed information '
                   'the locator form')
    )

    comment = EncryptedTextField(
        verbose_name="Comment",
        max_length=250,
        blank=True,
        help_text=('')
    )

    objects = MemberEntryManager()

    history = HistoricalRecords()

    class Meta(HouseholdMemberModelMixin.Meta):
        app_label = 'member'
