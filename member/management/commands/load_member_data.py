from edc_base.utils import get_utcnow
from django.apps import apps as django_apps
from django.core.management.base import BaseCommand

from edc_constants.constants import YES
from household.constants import ELIGIBLE_REPRESENTATIVE_PRESENT
from household.models import HouseholdLogEntry, HouseholdStructure
from member.models import HouseholdMember, RepresentativeEligibility
from django.core.exceptions import ValidationError


def data_dict(file_path=None):
    data_list = []
    with open(file_path) as csvfile:
        lines = csvfile.readlines()
        fields = lines[0]
        fields = fields.strip()
        fields = fields.split(',')
        fields = fields[3:]
        lines.pop(0)
        for line in lines:
            line = line.strip()
            line = line.split(',')
            line = line[3:]
            data = dict(zip(fields, line))
            data_list.append(data)
    return data_list


class Command(BaseCommand):

    help = 'Create moved members or deceased member from a csv.'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='file_path')
        parser.add_argument(
            'model_label_lower', type=str, help='model_label_lower')

    def handle(self, *args, **options):
        file_path = options['file_path']
        model_label_lower = options['model_label_lower']
        data_list = data_dict(file_path=file_path)
        app_label, model_name = model_label_lower.split('.')
        model_cls = django_apps.get_model(app_label, model_name)
        created_members = 0
        survey_schedule = None
        total_to_create = len(data_list)
        self.stdout.write(
            self.style.WARNING(f'Total to create {total_to_create} for model {model_cls}.'))
        for data in data_list:
            if data.get('time_point') == 'T2':
                survey_schedule = 'bcpp-survey.bcpp-year-3'
            elif data.get('time_point') == 'T1':
                survey_schedule = 'bcpp-survey.bcpp-year-2'
            subject_identifier = data.get('subject_identifier')
            try:
                household_member = HouseholdMember.objects.get(
                    subject_identifier=subject_identifier,
                    survey_schedule__icontains=survey_schedule)
            except HouseholdMember.DoesNotExist:
                print(
                    'Household Member for the subject identifier '
                    f'{subject_identifier} may be missing. Check if the member is imported')
            else:
                try:
                    model_cls.objects.get(household_member=household_member)
                except model_cls.DoesNotExist:
                    data.update(
                        report_datetime=get_utcnow(),
                        household_member=household_member)
                    del data['subject_identifier']
                    del data['time_point']
                    del data['created']
                    del data['revision']
                    try:
                        household_structure = HouseholdStructure.objects.get(
                            id=household_member.household_structure.id)
                    except HouseholdStructure.DoesNotExist:
                        raise ValidationError(
                            f'Missing household structure for member {household_member}')
                    else:
                        try:
                            HouseholdLogEntry.objects.get(
                                report_datetime__date=get_utcnow().date(),
                                household_log=household_structure.householdlog,
                                household_status=ELIGIBLE_REPRESENTATIVE_PRESENT)
                        except:
                            HouseholdLogEntry.objects.create(
                                report_datetime=get_utcnow(),
                                household_log=household_structure.householdlog,
                                household_status=ELIGIBLE_REPRESENTATIVE_PRESENT)
                    try:
                        RepresentativeEligibility.objects.get(
                            household_structure=household_structure)
                    except RepresentativeEligibility.DoesNotExist:
                        RepresentativeEligibility.objects.create(
                            household_structure=household_structure,
                            report_datetime=get_utcnow(),
                            aged_over_18=YES,
                            household_residency=YES,
                            verbal_script=YES)
                    obj = model_cls.objects.create(**data)
                    obj.save_base(raw=True)
                    obj = model_cls.objects.get(id=obj.id)
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully created {obj} member data.'))
                    created_members += 1
                else:
                    self.stdout.write(self.style.WARNING(f'Already exists {household_member}.'))
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_members} member data.'))
