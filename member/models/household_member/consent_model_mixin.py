from django.apps import apps as django_apps
from django.db import models

from edc_consent.site_consents import site_consents

from edc_consent.exceptions import ConsentDoesNotExist


class ConsentModelMixin(models.Model):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._consent = None
        self._consent_object = None

    @property
    def is_consented(self):
        return True if self.consent and self.eligible_subject else False

    @property
    def consent_object(self):
        if not self._consent_object:
            if self.anonymous:
                anonymous_consent_group = django_apps.get_app_config(
                    'edc_consent').anonymous_consent_group
                try:
                    self._consent_object = site_consents.get_consent(
                        report_datetime=self.report_datetime,
                        consent_group=anonymous_consent_group)
                except ConsentDoesNotExist:
                    self._consent_object = None
            else:
                default_consent_group = django_apps.get_app_config(
                    'edc_consent').default_consent_group
                try:
                    self._consent_object = site_consents.get_consent(
                        report_datetime=self.report_datetime,
                        consent_group=default_consent_group)
                except ConsentDoesNotExist:
                    self._consent_object = None
        return self._consent_object

    @property
    def consent(self):
        """Returns a consent model instance, or None, that is
        valid for the current period (report_datetime).
        """
        if not self._consent:
            if self.consent_object and self.eligible_subject:
                try:
                    self._consent = self.consent_object.model.objects.get(
                        version=self.consent_object.version,
                        subject_identifier=self.subject_identifier)
                except self.consent_object.model.DoesNotExist:
                    self._consent = None
        return self._consent

    class Meta:
        abstract = True
