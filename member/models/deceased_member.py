from django.db import models

from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel
from edc_base.model_validators import date_not_future
from edc_constants.choices import DEATH_RELATIONSIP_TO_STUDY

from ..managers import MemberEntryManager
from .model_mixins import HouseholdMemberModelMixin


class DeceasedMember(HouseholdMemberModelMixin, BaseUuidModel):

    """A model completed by the user to report the death of a member.
    """

    # TODO: was this a subject form???

    death_date = models.DateField(
        verbose_name='Date of Death:',
        validators=[
            date_not_future],
        help_text='')

    site_aware_date = models.DateField(
        verbose_name='Date site aware of Death:',
        validators=[
            date_not_future],
        help_text='')

    death_cause = models.TextField(
        max_length=1000,
        blank=True,
        null=True,
        verbose_name=(
            'Describe the major cause of death(including pertinent autopsy '
            'information if available),starting with the first noticeable '
            'illness thought to be related to death,continuing to '
            'time of death. '),
        help_text=(
            'Note: Cardiac and pulmonary arrest are not major reasons and '
            'should not be used to describe major cause'))

    duration_of_illness = models.IntegerField(
        verbose_name=(
            'Duration of acute illness directly causing death '
            '(in days, or choose Unknown)?'),
        help_text='in days',
        default=0)

    relationship_death_study = models.CharField(
        verbose_name='What is the relationship of the death to study participation?',
        max_length=50,
        choices=DEATH_RELATIONSIP_TO_STUDY,
        help_text='')
    
    extra_death_info = models.TextField(
        max_length=1000,
        blank=True,
        null=True,
        verbose_name=(
            'Extra information collected from other sources, specifically the death registry.'))
    
    extra_death_info_date = models.DateField(
        verbose_name='Date extra information captured:',
        validators=[date_not_future],
        blank=True,
        null=True)

    objects = MemberEntryManager()

    history = HistoricalRecords()

    class Meta:
        app_label = 'member'
