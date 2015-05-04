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
        '8-10AM',
        '10-11AM',
        '11AM-12PM',
        '12-1PM',
        '1-2PM',
        '2-3PM',
        '3-4PM',
        '4-5PM',
        '5-6PM',
        '6-7PM',
        '7PM-Close',
        {'role': 'annotation'}
        ]
    ],

    'times' : [
        ["8-10AM", None, None, None, None, None, ''],
        ["10-11AM", None, None, None, None, None, ''],
        ["11AM-12PM", None, None, None, None, None, ''],
        ["12-1PM", None, None, None, None, None, ''],
        ["1-2PM", None, None, None, None, None, ''],
        ["2-3PM", None, None, None, None, None, ''],
        ["3-4PM", None, None, None, None, None, ''],
        ["4-5PM", None, None, None, None, None, ''],
        ["5-6PM", None, None, None, None, None, ''],
        ["6-7PM", None, None, None, None, None, ''],
        ["7-Close", None, None, None, None, None, '']
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

    'directional': [
        "Directional", None, None, None, None, None, None, None, None, None, None, None, ''
    ],
    
    'collect/serv' : [
        "Help with Collections/Services", None, None, None, None, None, None, None, None, None, None, None, ''
    ],

    'referral' : [
        "Referral to Librarian", None, None, None, None, None, None, None, None, None, None, None, ''
    ],

    'equip' : [
        "Equipment", None, None, None, None, None, None, None, None, None, None, None, ''
    ],

    'print/software' : [
        "Help with Printers/Software", None, None, None, None, None, None, None, None, None, None, None, ''
    ],

    #For DB Parsing
    'helpcodes' : {
        "dir": 1,
        "equipment": 2,
        "help": 3,
        "ithelp": 4,
        "referral": 5
    },

    'timecodes': {
        "8to10": 1,
        "10to11": 2,
        "11to12": 3,
        "12to1": 4,
        "1to2": 5,
        "2to3": 6,
        "3to4": 7,
        "4to5": 8,
        "5to6": 9,
        "6to7": 10,
        "7toclose": 11
    },
    'timelabels' : {
        "8to10": '8 - 10 AM',
        "10to11": '10 - 11 AM',
        "11to12": '11 AM - 12 PM',
        "12to1": '12 - 1 PM',
        "1to2": '1 - 2 PM',
        "2to3": '2 - 3 PM',
        "3to4": '3 - 4 PM',
        "4to5": '4 - 5 PM',
        "5to6": '5 - 6 PM',
        "6to7": '6 - 7 PM',
        "7toclose": '7 PM - Closing'
    }
}
