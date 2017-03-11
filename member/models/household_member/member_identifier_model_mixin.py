from django.db import models

from edc_identifier.model_mixins import NonUniqueSubjectIdentifierModelMixin


class MemberIdentifierModelMixin(NonUniqueSubjectIdentifierModelMixin, models.Model):

    def make_new_identifier(self):
        return self.subject_identifier_as_pk

    @property
    def registered_subject(self):
        return self.registered_subject_model_class.objects.get(
            registration_identifier=self.internal_identifier)

    class Meta:
        abstract = True
