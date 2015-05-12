#Refdesk.py configurations.

config = {
    #Basic Settings
    'URL_BASE': '/refdesk-stats/',
    'DB_NAME': 'refstats',
    'DB_USER': 'victoria',
    'HOST': '0.0.0.0',
    'PORT': 6666,

    #Blank Lists to copy from.
    'stack' : [
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

    # A preallocated array for data display.
    'array': { 
        'dir_en': ['Directional (EN)',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        'dir_fr': ['Directional (FR)',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        'help_en': ['Help with Collections/Services (EN)',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        'help_fr': ['Help with Collections/Services (FR)',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        'referral_en': ['Referral to Librarian (EN)',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        'referral_fr': ['Referral to Librarian (FR)',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        'equipment_en': ['Equipment (EN)',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        'equipment_fr': ['Equipment (FR)',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        'ithelp_en': ['Help With Printers/Software (EN)',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''],
        'ithelp_fr': ['Help With Printers/Software (FR)',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,'']
    },
    
    'times' : [
        ["8-9AM", None, None, None, None, None, None, None, None, None, None, ''],
        ["9-10AM", None, None, None, None, None, None, None, None, None, None,  ''],
        ["10-11AM", None, None, None, None, None, None, None, None, None, None, ''],
        ["11AM-12PM", None, None, None, None, None, None, None, None, None, None, ''],
        ["12-1PM", None, None, None, None, None, None, None, None, None, None, ''],
        ["1-2PM", None, None, None, None, None, None, None, None, None, None, ''],
        ["2-3PM", None, None, None, None, None, None, None, None, None, None, ''],
        ["3-4PM", None, None, None, None, None, None, None, None, None, None, ''],
        ["4-5PM", None, None, None, None, None, None, None, None, None, None, ''],
        ["5-6PM", None, None, None, None, None, None, None, None, None, None, ''],
        ["6-7PM", None, None, None, None, None, None, None, None, None, None, ''],
        ["7-8PM", None, None, None, None, None, None, None, None, None, None, ''],
        ["8-9PM", None, None, None, None, None, None, None, None, None, None, ''],
        ["9-10PM", None, None, None, None, None, None, None, None, None, None, ''],
        ["10-11PM", None, None, None, None, None, None, None, None, None, None, ''],
        ["11PM-11AM", None, None, None, None, None, None, None, None, None, None, ''],
        ["12-1AM", None, None, None, None, None, None, None, None, None, None, ''],
        ["1-2AM", None, None, None, None, None, None, None, None, None, None, '']
    ],

    'days' : [
        ["Sunday", 0, 0, 0, 0, 0, ''],
        ["Monday", 0, 0, 0, 0, 0, ''],
        ["Tuesday", 0, 0, 0, 0, 0, ''],
        ["Wednesday", 0, 0, 0, 0, 0, ''],
        ["Thursday", 0, 0, 0, 0, 0, ''],
        ["Friday", 0, 0, 0, 0, 0, ''],
        ["Saturday", 0, 0, 0, 0, 0, '']
    ],

    #For DB Parsing
    'helpcodes' : {
        "dir_en": 1,
        "dir_fr": 2,
        "equipment_en": 3,
        "equipment_fr": 4,
        "help_en": 5,
        "help_en": 6,
        "ithelp_en": 7,
        "ithelp_en": 8,
        "referral_fr": 9,
        "referral_fr": 10
    },

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
