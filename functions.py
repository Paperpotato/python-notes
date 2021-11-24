import command_dict as cd
import datetime
import pyperclip
import re
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import os.path

today = datetime.date.today().strftime("%d-%m-%Y")
command_dict = cd.command_dict

def print_line():
    print('#################################################################')
    
def command_prompt(patient_name):
    full_date = datetime.date.today().strftime('%d %b %y')
    command_df = cd.df
    return f'#################################################################\n\nPATIENT: {patient_name} - {full_date}\n\n{command_df}\n>>> '

def html_decode(str):
    return str.replace('<br>', '\n').replace('&lt;', '<').replace('&gt;', '>')

def standard_commands(command, history=None):
    treatment_note = ''
    for standard_command in command_dict[command]:
        if standard_command == 'e':
            treatment_note += command_dict[standard_command] + '\n' + input('General history/progress input: ') + '\n\n' if not history else history
        else:
            treatment_note += command_dict[standard_command] + '\n'    
    print('returned treatment_note', treatment_note)    
    return treatment_note


def init_consult():
    output = 'New Complaint:\n'

    questions_array = ['Site', 'Onset', 'Character', 'Radiation', 'Associated', 'Timing', 'Exacerbating', 'Relieving', 'Severity', 'Flags', 'Medication', 'Family History']
    for question in questions_array:
        output += f'{question}: ' + input(f'{question}: ') + '\n'

    pyperclip.copy('WNL')
    exam_array = ['Upper & Lower Neuro', 'ROM', 'Ortho Tests']
    for question in exam_array:
        output += f'{question}: ' + input(f'{question}: ') + '\n'
    
    output += 'Negative for 5D\'s & 3N\'s\nVerbal informed consent given, written/digital consent taken\n\n'
    output += 'Diagnos(es): ' + input('Diagnos(es): ')

    pyperclip.copy('mild lbp and stiffness')
    return output

def parse_commands(commands, history=None):
    treatment_note = ''
    if commands == ['']:
        return f'<{today}>'
    else:
        try:
            commands = re.search('\[(.+?)\]', str(commands)).group(1) if type(commands) is str else commands
        except AttributeError:
            print('no regex match')
            pass
        print(commands)
        if 'e' in commands:
            history_input = f"{input('General history/progress input: ')}\n\n" if not history else f'{history}\n\n'
        elif 'init' in commands:
            history_input = init_consult()
        else:
            history_input = ''
        for command in commands:
            command = command.strip()
            if command == 'e':
                continue
            if 's' == command or 'sl' == command or 'sd' == command or 'sdl' == command or 'sdu' == command:
                treatment_note += standard_commands(command, history)
            else:
                try:
                    treatment_note += command_dict[command]
                except KeyError:
                    user_input = input('Tx commands: ').split(',')
                    return parse_commands(user_input, commands[0])
        return f'<{today}>\n{history_input}{treatment_note}\n{str(commands) if len(commands) != 1 else f"{str(commands)}"}'

def build_service():
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.events']
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8083)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('calendar', 'v3', credentials=creds)
    return service