from edc_constants.constants import OTHER, DWTA, NOT_APPLICABLE, POS, NEG, IND

from .constants import (ABSENT, BHS, BHS_ELIGIBLE, BHS_SCREEN, HTC, HTC_ELIGIBLE, NOT_ELIGIBLE,
                        NOT_REPORTED, REFUSED, UNDECIDED, REFUSED_HTC, BHS_LOSS, ANNUAL, DECEASED,
                        HEAD_OF_HOUSEHOLD)
from member.constants import MENTAL_INCAPACITY, BLOCK_PARTICIPATION

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
    (NOT_APPLICABLE, ('ABLE to participate')),
    (MENTAL_INCAPACITY, ('Mental Incapacity')),
    ('Deaf/Mute', ('Deaf/Mute')),
    ('Too sick', ('Too sick')),
    ('Incarcerated', ('Incarcerated')),
    (OTHER, ('Other, specify.')),
)

REASONS_UNDECIDED = (
    ('afraid_to_test', ('afraid_to_test')),
    ('not ready to test', ('not ready to test')),
    ('wishes to test with partner', ('wishes to test with partner')),
    ('OTHER', ('Other...')),
)

REASONS_REFUSED = (
    ('I don\'t have time', ('I don\'t have time')),
    ('I don\'t want to answer the questions', ('I don\'t want to answer the questions')),
    ('I don\'t want to have the blood drawn', ('I don\'t want to have the blood drawn')),
    ('I am afraid my information will not be private', ('I am afraid my information will not be private')),
    ('Fear of needles', ('Fear of needles')),
    ('Illiterate does not want a witness', ('Illiterate does not want a witness')),
    ('I already know I am HIV-positive', ('I already know I am HIV-positive')),
    ('I am afraid of testing', ('I am afraid of testing')),
    ('I don\'t want to take part', ('I don\'t want to take part')),
    ('I haven\'t had a chance to think about it', ('I haven\'t had a chance to think about it')),
    ('Have a newly born baby, not permitted', ('Have a newly born baby, not permitted')),
    ('I am not ready to test', ('I am not ready to test')),
    ('Already on HAART', ('Already on HAART')),
    ('I want to test where i always test', ('I want to test where i always test')),
    ('I already know my partner\'s status, no need to test', ('I already know my partner\'s status, no need to test')),
    ('The appointment was not honoured', ('The appointment was not honoured')),
    ('not_sure', ('I am not sure')),
    (OTHER, ('Other, specify:')),
    (DWTA, ('Don\'t want to answer')),
)

REASONS_ABSENT = (
    ('gone visiting (relatives,holidays,weddings,funerals)', ('Gone visiting')),
    ('stays at lands or cattlepost ', ('Stays at Lands/Cattlepost ')),
    ('stepped out(shops, errands etc) ', ('Stepped out (shops, errands, ) ')),
    ('works in village and comes home daily', ('Works in the village, home daily')),
    ('goes to school in village and comes home daily', ('Schools in this village, home daily')),
    ('works outside village and comes home daily', ('Works outside the village, home daily')),
    ('goes to school outside village and comes home daily', ('Schools outside village, home daily')),
    ('works outside village and comes home irregularly ', ('Works outside the village, home irregularly ')),
    ('goes to school outside village and comes home irregularly ', ('Schools outside village, home irregularly ')),
    ('works outside village and comes home monthly ', ('Works outside the village, home monthly ')),
    ('goes to school outside village and comes home monthly ', ('Schools outside village, home monthly ')),
    ('works outside village and comes home on weekends ', ('Works outside the village, home on weekends ')),
    ('goes to school outside village and comes home on weekends ', ('Schools outside village, home on weekends ')),
    ('OTHER', ('Other...')),
)

BLOCK_CONTINUE = (
    (BLOCK_PARTICIPATION, 'Yes( Block from further participation)'),
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

FLOORING_TYPE = (
    ('Dirt/earth', ('Dirt/earth ')),
    ('Wood, plank', ('Wood, plank')),
    ('Parquet/lino', ('Parquet/lino')),
    ('Cement', ('Cement')),
    ('Tile flooring', ('Tile flooring')),
    (OTHER, ('Other, specify:')),
    (DWTA, ('Don\'t want to answer')),
)

WATER_SOURCE = (
    ('Communal tap', ('Communal tap')),
    ('Standpipe/tap within plot', ('Standpipe/tap within plot')),
    ('Piped indoors', ('Piped indoors')),
    ('Borehore', ('Borehole')),
    ('Protected well', ('Protected well')),
    ('Unprotected/shallow well', ('Unprotected/shallow well')),
    ('River /dam/lake/pan', ('River /dam/lake/pan')),
    ('Bowser/tanker', ('Bowser/tanker')),
    (OTHER, ('Other, specify (including unknown):')),
    (DWTA, ('Don\'t want to answer')),
)


ENERGY_SOURCE = (
    ('Charcoal/wood', ('Charcoal/wood')),
    ('Paraffin', ('Paraffin')),
    ('Gas', ('Gas')),
    ('Electricity (mains)', ('Electricity (mains)')),
    ('Electricity (solar)', ('Electricity (solar)')),
    ('No cooking done', ('No cooking done')),
    (OTHER, ('Other, specify:')),
    (DWTA, ('Don\'t want to answer')),
)


TOILET_FACILITY = (
    ('Pit latrine within plot', ('Pit latrine within plot')),
    ('Flush toilet within plot', ('Flush toilet within plot')),
    ('Neighbour\'s flush toilet', ('Neighbour\'s flush toilet')),
    ('Neighbour\'s pit latrine', ('Neighbour''s pit latrine')),
    ('Communal flush toilet', ('Communal flush toilet')),
    ('Communal pit latrine', ('Communal pit latrine')),
    ('Pail bucket latrine', ('Pail bucket latrine')),
    ('Bush', ('Bush')),
    ('River or other body of water', ('River or other body of water')),
    (OTHER, ('Other, specify:')),
    (DWTA, ('Don\'t want to answer')),
)


SMALLER_MEALS = (
    ('Never', ('Never')),
    ('Rarely', ('Rarely')),
    ('Sometimes', ('Sometimes')),
    ('Often', ('Often')),
    (DWTA, ('Don\'t want to answer')),
)
