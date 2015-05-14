#Refdesk.py configurations.

config = {
    #Basic Settings
    'URL_BASE': '/refdesk-stats/',
    'DB_NAME': 'refstats',
    'DB_USER': 'victoria',
    'HOST': '0.0.0.0',
    'PORT': 6666,

    #Blank Lists to copy from.
    'stack_a' : [
        [
        'Timeslot',
        '8-9AM',
        '9-10AM',
        '10-11AM',
        '11AM-12PM',
        '12-1PM',
        '1-2PM',
        '2-3PM',
        '3-4PM',
        '4-5PM',
        '5-6PM',
        '6-7PM',
        '7-8PM',
        '8-9PM',
        '9-10PM',
        '10-11PM',
        '11PM-12AM',
        '12-1AM',
        '1-2AM',
        {'role': 'annotation'}
        ]
    ],
    
    'stack_b' : [
        [
        'Refstat',
        'Internal (EN)',
        'Internal (FR)',
        'Referral (Found, EN)',
        'Referral (Found, FR)',
        'Referral (N/A, EN)',
        'Referral (N/A, FR)',
        'Equipment (EN)',
        'Equipment (FR)',
        'OneCard/IT (EN)',
        'OneCard/IT (FR)',
        'External (EN)',
        'External (FR)',
        'Other (EN)',
        'Other (FR)',
        'Phone (EN)',
        'Phone (FR)',
        {'role': 'annotation'}
        ]
    ],

    # Preallocated arrays for data display.
    'array': [
        ['Internal (EN)',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ['Internal (FR)',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ['Referral (Found, EN)',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ['Referral (Found, FR)',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ['Referral (N/A, EN)',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ['Referral (N/A, FR)',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ['Equipment (EN)',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ['Equipment (FR)',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ['OneCard/IT (EN)',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ['OneCard/IT (FR)',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ['External (EN)',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ['External (FR)',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ['Other (EN)',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ['Other (FR)',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ['Phone (EN)',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ['Phone (FR)',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,'']
    ],
    
    'times' : [
        ["8-9AM",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ["9-10AM",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ["10-11AM",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ["11AM-12PM",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ["12-1PM",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ["1-2PM",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ["2-3PM",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ["3-4PM",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ["4-5PM",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ["5-6PM",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ["6-7PM",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ["7-8PM",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ["8-9PM",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ["9-10PM",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ["10-11PM",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ["11PM-12AM",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ["12-1AM",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ["1-2AM",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,'']
    ],

    'days' : [
        ["Sunday",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ["Monday",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ["Tuesday",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ["Wednesday",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ["Thursday",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ["Friday",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        ["Saturday",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,'']
    ],

    #For DB Parsing
    'helpcodes': {
        'internal_en': 1,
        'internal_fr': 2,
        'refer_yes_en': 3,
        'refer_yes_fr': 4,
        'refer_no_en': 5,
        'refer_no_fr': 6,
        'equipment_en': 7,
        'equipment_fr': 8,
        'ithelp_en': 9,
        'ithelp_fr': 10,
        'external_en': 11,
        'external_fr': 12,
        'other_en': 13,
        'other_fr': 14,
        'phone_en': 15,
        'phone_fr': 16
    },

    'helplist': [
        'internal', 'refer_yes', 'refer_no', 'equipment',
        'ithelp', 'external', 'other', 'phone'
    ],
    
    'timelist': [
        '8', '9', '10', '11',
        '12', '13', '14', '15',
        '16', '17', '18', '19',
        '20', '21', '22', '23',
        '0', '1'
    ],

    'timecodes': {
        "8": 1,
        "9": 2,
        "10": 3,
        "11": 4,
        "12": 5,
        "13": 6,
        "14": 7,
        "15": 8,
        "16": 9,
        "17": 10,
        "18": 11,
        "19": 12,
        "20": 13,
        "21": 14,
        "22": 15,
        "23": 16,
        "0": 17,
        "1": 18
    },

    'timelabels' : {
        "8": '8 - 9 AM',
        "9": '9 - 10 AM',
        "10": '10 - 11 AM',
        "11": '11 AM - 12 PM',
        "12": '12 - 1 PM',
        "13": '1 - 2 PM',
        "14": '2 - 3 PM',
        "15": '3 - 4 PM',
        "16": '4 - 5 PM',
        "17": '5 - 6 PM',
        "18": '6 - 7 PM',
        "19": '7 - 8 PM',
        "20": '8 - 9 PM',
        "21": '9 - 10 PM',
        "22": '10 - 11 PM',
        "23": '11 PM - 12 AM',
        "0": '12 - 1 AM',
        "1": '1 - 2 AM'
    }
}