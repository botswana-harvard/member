from edc_sync.site_sync_models import site_sync_models
from edc_sync.sync_model import SyncModel

sync_models = [
    'member.absentmember',
    'member.deceasedmember',
    'member.enrollmentchecklist',
    'member.enrollmentloss',
    'member.householdheadeligibility',
    'member.householdinfo',
    'member.householdmember',
    'member.householdworklist',
    'member.htcmemberhistory',
    'member.htcmember',
    'member.listmodels',
    'member.memberappointment',
    'member.movedmember',
    'member.refusedmemberhistory',
    'member.refusedmember',
    'member.representativeeligibility',
    'member.undecidedmemberhistory',
    'member.undecidedmember'
]


site_sync_models.register(sync_models, SyncModel)
