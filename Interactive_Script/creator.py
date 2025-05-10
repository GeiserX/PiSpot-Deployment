#!/usr/bin/python3
from __future__ import print_function, unicode_literals
from PyInquirer import prompt, style_from_dict, Token, Validator, ValidationError
from pprint import pprint
from pyfiglet import Figlet
from random import randint
import json
import re
import os
import hvac

style = style_from_dict({
    Token.Separator: '#cc5454',
    Token.QuestionMark: '#673ab7 bold',
    Token.Selected: '#cc5454',  # default
    Token.Pointer: '#673ab7 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#f44336 bold',
    Token.Question: '',
})

class VenueTownValidator(Validator):
    def validate(self, document):
        if(len(document.text) >= 10):
            raise ValidationError(message='Keep it shorter than 10 characters', cursor_position=len(document.text))
        if(len(document.text) <= 1):
            raise ValidationError(message='Keep it longer than 1 character', cursor_position=len(document.text))

class NumberValidator(Validator):
    def validate(self, document):
        try:
            number = int(document.text)
#            if(number >= 50):
#                raise ValidationError(message='Please, lower the value', cursor_position=len(document.text))
        except ValueError:
            raise ValidationError(message='Please, enter a number', cursor_position=len(document.text))

class SpotipoKeyValidator(Validator):
    def validate(self, document):
        if(len(document.text) != 36):
            raise ValidationError(message='Wrong key length', cursor_position=len(document.text))
        if not (document.text[8] == '-' and document.text[13] == '-' and document.text[18] == '-' and document.text[23] == '-'):
            raise ValidationError(message='Wrong key format', cursor_position=len(document.text))

class VaultAddressValidator(Validator):
    def validate(self, document):
        regex = re.compile(r'^(?:http|ftp)s?://' r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' r'localhost|' r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' r'(?::\d+)?' r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if not (re.match(regex, document.text) is not None or document.text == "$VAULT_ADDR"):
            raise ValidationError(message='Wrong URL format', cursor_position=len(document.text))

class VaultTokenValidator(Validator):
    def validate(self, document):
        if not (document.text == '$VAULT_TOKEN'):
            if(document.text[1] != "."):
                raise ValidationError(message='Wrong token format', cursor_position=len(document.text))
            if(len(document.text) != 26):
                raise ValidationError(message='Wrong token length', cursor_position=len(document.text))

f = Figlet(font='slant')
print(f.renderText('PiSpot Deployer'))

print("Checking if the Approle token needs to be renewed...")
try:
    client = hvac.Client(url = os.environ['VAULT_ADDR'], token = os.environ['VAULT_TOKEN'])
    ttl = client.lookup_token()['data']['ttl']
    if(ttl < 864000):
        renewed_data = client.renew_token()
        print("Token renewed")
    else:
        print("Token still has %1.1f hours to live" % (ttl/3600,))
except:
    raise RuntimeError("Can't reach the network")

questionsNames = [
    {
        'type': 'rawlist',
        'name': 'project',
        'message': 'For which project do you want to write secrets?',
        'choices': ['PiSpot_Voucher', 'PiSpot_HDMI', 'PiSpot_SMS'],
        'filter': lambda val: val.lower()
    },
    {
        'type': 'input',
        'name': 'venue_name',
        'message': 'What is the name of the venue?',
        'validate': VenueTownValidator,
        'filter': lambda val: val.lower()
    },
    {
        'type': 'input',
        'name': 'town_name',
        'message': 'What is the name of the town?',
        'validate': VenueTownValidator,
        'filter': lambda val: val.lower()
    },
    {
        'type': 'input',
        'name': 'id_pispot',
        'message': 'Which is the ID number for this PiSpot?',
        'default': '1',
        'validate': NumberValidator,
        'filter': lambda val: int(val)
    }
]
answersNames = prompt(questionsNames, style=style)

questions = [
    {
        'type': 'input',
        'name': 'spotipo_key',
        'message': "What is the Spotipo Server's API key?",
        'validate': SpotipoKeyValidator,
        'filter': lambda val: val.lower()
    },
    {
        'type': 'input',
        'name': 'site_number',
        'message': 'Which is the Site number for the Spotipo Server?', # f50ca06b-6853-4725-9e58-853a669cbe57
        'validate': NumberValidator,
        'filter': lambda val: int(val)
    },
    {
        'type': 'rawlist',
        'name': 'duration_type',
        'message': 'How long should every voucher last?',
        'choices': ['Minutes', 'Hours', 'Days']
    },
    {
        'type': 'input',
        'name': 'button_2',
        'message': 'What will be the duration value for the button 2?',
        'default': '1',
        'validate': NumberValidator,
        'filter': lambda val: int(val)
    },
    {
        'type': 'input',
        'name': 'button_3',
        'message': 'What will be the duration value for the button 3?',
        'default': '2',
        'validate': NumberValidator,
        'filter': lambda val: int(val)
    },
    {
        'type': 'input',
        'name': 'button_4',
        'message': 'What will be the duration value for the button 4?',
        'default': '3',
        'validate': NumberValidator,
        'filter': lambda val: int(val)
    },
    {
        'type': 'input',
        'name': 'speed_dl',
        'message': 'What will be the maximum download speed allowed? (KB/s)',
        'default': '1024',
        'validate': NumberValidator,
        'filter': lambda val: int(val)
    },
    {
        'type': 'input',
        'name': 'speed_ul',
        'message': 'What will be the maximum upload speed allowed? (KB/s)',
        'default': '256',
        'validate': NumberValidator,
        'filter': lambda val: int(val)
    },
]

answers = prompt(questions, style=style)

# Number of devices to allow are set to 1 by default for the pispot voucher !
# Number of voucher to create is set to 1 by default with all pispot !
# Total data allowed to download by voucher is set to 0 (unlimited) by default for all pispot !

questionCheck = [
    {
        'type': 'confirm',
        'name': 'checkName',
        'message': 'Is this name correct: %s_%s_%s' % (answersNames['venue_name'], answersNames['town_name'], answersNames['id_pispot']),
        'default': True
    }
]
answerCheck = prompt(questionCheck, style=style)

if(answerCheck['checkName'] == True):
    answers['duration_type'] = 1 if answers['duration_type'] == 'Minutes' else 2 if answers['duration_type'] == 'Hours' else 3
    answers['batchid'] = randint(1000, 9999)
    answers['num_devices'] = 1
    answers['number'] = 1
    answers['notes'] =  '%s_%s_%s' % (answersNames['venue_name'], answersNames['town_name'], answersNames['id_pispot'])
    answers['bytes_t'] = 0

    pprint(answers)
    fileName = '%s_%s_%s_%s.json' % (answersNames['project'], answersNames['venue_name'], answersNames['town_name'], answersNames['id_pispot'])
    with open(fileName, 'w') as json_file:
        json.dump(answers, json_file)
    print("Saved to ", fileName)

    print("Now let's upload it all to hashicorp Vault")
    questionsVault = [
        {
            'type': 'input',
            'name': 'vault_addr',
            'message': 'What is the Vault Address?',
            'default': 'https://secrets.YOUR-URL.us',
            'validate': VaultAddressValidator
        },
        {
            'type': 'input',
            'name': 'vault_token',
            'message': 'What is your Vault Token?',
            'default': '$VAULT_TOKEN',
            'validate': VaultTokenValidator
        }
    ]
    answersVault = prompt(questionsVault, style=style)

    if(answersVault['vault_addr'] == '$VAULT_ADDR'): answersVault['vault_addr'] = os.environ['VAULT_ADDR']
    if(answersVault['vault_token'] == '$VAULT_TOKEN'): answersVault['vault_token'] = os.environ['VAULT_TOKEN']

    questionCheckVault = [
        {
            'type': 'confirm',
            'name': 'check',
            'message': 'Is this data correct? VAULT_ADDR: %s VAULT_TOKEN: %s' % (answersVault['vault_addr'], answersVault['vault_token']),
            'default': True
        }
    ]
    answerCheckVault = prompt(questionCheckVault, style=style)

    if(answerCheckVault['check'] == True):
        print("Uploading...")
        try:
            client = hvac.Client(url = answersVault['vault_addr'], token = answersVault['vault_token'])
            client.secrets.kv.default_kv_version = '1'
            secret_path = '%s_%s_%s' % (answersNames['venue_name'], answersNames['town_name'], answersNames['id_pispot'])
            create_response = client.secrets.kv.create_or_update_secret(mount_point = answersNames['project'], path = secret_path, secret = answers)
            read_secret_result = client.secrets.kv.read_secret(mount_point = answersNames['project'], path = secret_path)
            pprint(read_secret_result['data'])
            print("Uploaded to ")
        except:
            raise RuntimeError("Can't reach the network")
else:
    print("Incorrect name")
