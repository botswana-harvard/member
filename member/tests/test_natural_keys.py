from django.test import TestCase

from edc_sync.test_mixins import SyncTestSerializerMixin

from .mixins import MemberMixin


class TestNaturalKey(SyncTestSerializerMixin, MemberMixin, TestCase):

    def test_natural_key_attrs(self):
        self.sync_test_natural_key_attr('member')
