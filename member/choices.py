from edc_constants.constants import OTHER, DWTA, NOT_APPLICABLE, POS, NEG, IND

from .constants import (ABSENT, BHS, BHS_ELIGIBLE, BHS_SCREEN, HTC, HTC_ELIGIBLE, NOT_ELIGIBLE,
                        NOT_REPORTED, REFUSED, UNDECIDED, REFUSED_HTC, BHS_LOSS, ANNUAL, DECEASED,
                        HEAD_OF_HOUSEHOLD)

options = list(set([ABSENT, BHS, BHS_ELIGIBLE, BHS_SCREEN, HTC, HTC_ELIGIBLE, NOT_ELIGIBLE,
                    NOT_REPORTED, REFUSED, UNDECIDED, REFUSED_HTC, BHS_LOSS, ANNUAL, DECEASED]))

HOUSEHOLD_MEMBER_PARTICIPATION = [(item, item) for item in options]

FEMALE_RELATIONS = [
    ('wife', 'Wife'),
    ('daughter', 'Daughter'),
    ('mother', 'Mother'),
    ('sister', 'Sister'),
    ('grandmother', 'Grandmother'),
    ('granddaughter', 'Granddaughter'),
    ('great-Grandmother', 'Great-Grandmother'),
    ('great-Granddaughter', 'Great-Granddaughter'),
    ('aunt', 'Aunt'),
    ('niece', 'Niece'),
    ('mother-in-law', 'Mother-in-law'),
    ('daughter-in-law', 'Daughter-in-law'),
    ('sister-in-law', 'Sister-in-law'),
    ('housemaid', 'Housemaid'),
]

ANY_RELATIONS = [
    ('partner', 'Partner'),
    ('housemate', 'Housemate'),
    ('cousin', 'Cousin'),
    ('family_friend', 'Family friend'),
    ('friend', 'Friend'),
    ('helper', 'Helper'),
    ('employee', 'Employee'),
]
MALE_RELATIONS = [
    ('husband', 'Husband'),
    ('son', 'Son'),
    ('father', 'Father'),
    ('brother', 'Brother'),
    ('grandfather', 'Grandfather'),
    ('grandson', 'Grandson'),
    ('great-Grandfather', 'Great-Grandfather'),
    ('great-Grandson', 'Great-Grandson'),
    ('uncle', 'Uncle'),
    ('nephew', 'Nephew'),
    ('father-in-law', 'Father-in-law'),
    ('son-in-law', 'Son-in-law'),
    ('brother-in-law', 'Brother in-law'),
]


relations = FEMALE_RELATIONS + MALE_RELATIONS + ANY_RELATIONS
relations.sort()
RELATIONS = [(HEAD_OF_HOUSEHOLD, 'HEAD of HOUSEHOLD')] + relations + [('UNKNOWN', 'UNKNOWN')]

DETAILS_CHANGE_REASON = (
    ('married', 'Married'),
    ('parent_married', 'Parent Married'),
)

INABILITY_TO_PARTICIPATE_REASON = (
    (NOT_APPLICABLE, _('ABLE to participate')),
    ('Mental Incapacity', _('Mental Incapacity')),
    ('Deaf/Mute', _('Deaf/Mute')),
    ('Too sick', _('Too sick')),
    ('Incarcerated', _('Incarcerated')),
    (OTHER, _('Other, specify.')),
)

REASONS_UNDECIDED = (
    ('afraid_to_test', _('afraid_to_test')),
    ('not ready to test', _('not ready to test')),
    ('wishes to test with partner', _('wishes to test with partner')),
    ('OTHER', _('Other...')),
)

REASONS_REFUSED = (
    ('I don\'t have time', _('I don\'t have time')),
    ('I don\'t want to answer the questions', _('I don\'t want to answer the questions')),
    ('I don\'t want to have the blood drawn', _('I don\'t want to have the blood drawn')),
    ('I am afraid my information will not be private', _('I am afraid my information will not be private')),
    ('Fear of needles', _('Fear of needles')),
    ('Illiterate does not want a witness', _('Illiterate does not want a witness')),
    ('I already know I am HIV-positive', _('I already know I am HIV-positive')),
    ('I am afraid of testing', _('I am afraid of testing')),
    ('I don\'t want to take part', _('I don\'t want to take part')),
    ('I haven\'t had a chance to think about it', _('I haven\'t had a chance to think about it')),
    ('Have a newly born baby, not permitted', _('Have a newly born baby, not permitted')),
    ('I am not ready to test', _('I am not ready to test')),
    ('Already on HAART', _('Already on HAART')),
    ('I want to test where i always test', _('I want to test where i always test')),
    ('I already know my partner\'s status, no need to test', _('I already know my partner\'s status, no need to test')),
    ('The appointment was not honoured', _('The appointment was not honoured')),
    ('not_sure', _('I am not sure')),
    (OTHER, _('Other, specify:')),
    (DWTA, _('Don\'t want to answer')),
)

REASONS_ABSENT = (
    ('gone visiting (relatives,holidays,weddings,funerals)', _('Gone visiting')),
    ('stays at lands or cattlepost ', _('Stays at Lands/Cattlepost ')),
    ('stepped out(shops, errands etc) ', _('Stepped out (shops, errands, ) ')),
    ('works in village and comes home daily', _('Works in the village, home daily')),
    ('goes to school in village and comes home daily', _('Schools in this village, home daily')),
    ('works outside village and comes home daily', _('Works outside the village, home daily')),
    ('goes to school outside village and comes home daily', _('Schools outside village, home daily')),
    ('works outside village and comes home irregularly ', _('Works outside the village, home irregularly ')),
    ('goes to school outside village and comes home irregularly ', _('Schools outside village, home irregularly ')),
    ('works outside village and comes home monthly ', _('Works outside the village, home monthly ')),
    ('goes to school outside village and comes home monthly ', _('Schools outside village, home monthly ')),
    ('works outside village and comes home on weekends ', _('Works outside the village, home on weekends ')),
    ('goes to school outside village and comes home on weekends ', _('Schools outside village, home on weekends ')),
    ('OTHER', _('Other...')),
)

BLOCK_CONTINUE = (
    ('Block', 'Yes( Block from further participation)'),
    ('Continue', 'No (Can continue and participate)'),
    (NOT_APPLICABLE, 'Not applicable'),
)

HIV_RESULT = (
    (POS, 'HIV Positive (Reactive)'),
    (NEG, 'HIV Negative (Non-reactive)'),
    (IND, 'Indeterminate'),
    ('Declined', 'Participant declined testing'),
    ('Not performed', 'Test could not be performed (e.g. supply outage, technical problem)'),
)
