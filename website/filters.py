def status_abbreviate(status):
    abbreviations = {
        'ASSIGNED': 'A',
        'NEED SOME INFO': 'NSI',
        'IN PROGRESS': 'IP',
        'DEPLOYING(TEST)': 'DT',
        'TESTING': 'T',
        'TEST OK': 'TO',
        'TEST FAILED': 'TF',
        'DEPLOYING': 'D',
        'DEPLOY FAILED': 'DF',
        'DEPLOY OK': 'DO',
        'STABILITY': 'S',
        'REJECT': 'R',
        'CLOSED': 'CLD'
    }
    return abbreviations.get(status, status)
