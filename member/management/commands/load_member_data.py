from dateutil import parser

from django.apps import apps as django_apps
from django.core.management.base import BaseCommand

from edc_constants.constants import YES
from household.constants import ELIGIBLE_REPRESENTATIVE_PRESENT
from household.models import HouseholdLogEntry, HouseholdStructure
from member.models import HouseholdMember, RepresentativeEligibility


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
        model_cls = django_apps.get_model(model_label_lower)
        created_members = 0
        survey_schedule = None

        for data in data_list:
            if data.get('time_point') == 'T2':
                survey_schedule = 'bcpp-survey.bcpp-year-3'
            elif data.get('time_point') == 'T1':
                survey_schedule = 'bcpp-survey.bcpp-year-2'
            try:
                household_member = HouseholdMember.objects.get(
                    subject_identifier=data.get('subject_identifier'),
                    survey_schedule__icontains=survey_schedule)
            except:
                pass
            else:
                try:
                    model_cls.objects.get(household_member=household_member)
                except model_cls.DoesNotExist:
                    created = parser.parse(data.get('created'))
                    modified = parser.parse(data.get('modified'))
                    report_datetime = parser.parse(data.get('report_datetime'))
                    data.update(
                        created=created,
                        modified=modified,
                        report_datetime=report_datetime,
                        household_member=household_member)
                    del data['subject_identifier']
                    del data['time_point']
                    try:
                        household_structure = HouseholdStructure.objects.get(
                            id=household_member.household_structure.id)
                    except HouseholdStructure.DoesNotExist:
                        pass
                    else:
                        HouseholdLogEntry.objects.create(
                            report_datetime=report_datetime,
                            household_log=household_structure.householdlog,
                            household_status=ELIGIBLE_REPRESENTATIVE_PRESENT)
                    try:
                        RepresentativeEligibility.objects.get(
                            household_structure=household_structure)
                    except RepresentativeEligibility.DoesNotExist:
                        RepresentativeEligibility.objects.create(
                            household_structure=household_structure,
                            report_datetime=report_datetime,
                            aged_over_18=YES,
                            household_residency=YES,
                            verbal_script=YES)
                    print('&&&&&&&& about to create &&&&&&&&&&&&')
                    obj = model_cls.objects.created(**data)
                    print("*************************** Created", obj)
                    created_members += 1
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_members} moved members.'))
