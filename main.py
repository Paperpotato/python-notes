from __future__ import print_function
import datetime
import pickle
import os.path
from typing import final
import pyperclip
import re
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import command_dict as cd

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.events']

today = datetime.date.today().strftime("%d-%m-%Y")
full_date = datetime.date.today().strftime('%d %b %y')
print('Writing notes for:', today)

command_dict = cd.command_dict

def init_consult():
    output = 'New Complaint:\n'

    questions_array = ['Site', 'Onset', 'Character', 'Radiation', 'Associated', 'Timing', 'Exacerbating/Relieving', 'Severity', 'Flags', 'Medication', 'Family History']
    for question in questions_array:
        output += f'{question}: ' + input(f'{question}: ') + '\n'

    pyperclip.copy('WNL')
    exam_array = ['Upper & Lower Neuro', 'ROM', 'Ortho Tests']
    for question in exam_array:
        output += f'{question}: ' + input(f'{question}: ') + '\n'
    
    output += 'Negative for 5D\'s & 3N\'s\nVerbal informed consent given, written/digital consent taken\n\n'
    output += 'Diagnos(es): ' + input('Diagnos(es): ')

    return output

def command_prompt(patient_name):
    return f'#################################################################\n\nPATIENT: {patient_name} - {full_date}\nCOMMANDS:\n--std--\nim,f,m,lm,dn \n--history-- \nim/n/e/init \n--std regions & technique-- \n[b/l/r]f/c/t/ls/(m)an/lo/lc/ \n--muscles-- \nbm/lm/um/sh/kn \n--misc-- \ndn/a/sup/cup\n'

def standard_commands():
    treatment_note = ''
    for standard_command in command_dict['s']:
        treatment_note = treatment_note + command_dict[standard_command] + '\n'        
    return treatment_note

def custom_commands(commands):
    treatment_note = ''
    for custom_command in commands:
        treatment_note = treatment_note + command_dict[custom_command.strip()] + '\n'
    return treatment_note

def parse_commands(commands):
    treatment_note = ''
    try:
        commands = re.search('\[(.+?)\]', str(commands)).group(1) if type(commands) is str else commands
    except AttributeError:
        print('no regex match')
        pass
    print(commands)
    if 'e' in commands:
        history_input = input('General history/progress input: ') + '\n\n'
        commands.remove('e')
    elif 'init' in commands:
        history_input = init_consult()
    else:
        history_input = ''
    if 's' in commands:
        treatment_note += standard_commands()
        commands.remove('s')
    else:
        treatment_note += custom_commands(commands)
    print('#################################################################')
    return f'<{today}>\n{history_input}{treatment_note}\n{str(commands) if len(commands) != 1 else f"{str(commands)}"}'

def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
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

    # Call the Calendar API
    # now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    now = datetime.date.today().strftime("%Y-%m-%d") + 'T05:00:00Z'
    print(now)
    print('Getting the upcoming 50 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=50, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start_date = event['start'].get('dateTime', event['start'].get('date'))
        start_time = event['start'].get('dateTime', event['start'].get('time'))
        print(f'entry for: {event["summary"]}')
        if start_time == None:
            print(f'Skipping: {event["summary"]}')
        else:
            try:
                previous_date = re.search('<(.+?)>', event['description'])
                try:
                    if previous_date.group(1) == today:
                        continue
                except AttributeError:
                    print('attribute error. Possibly invalid notes? continuing...')
                # final_note = ''
                old_note = event['description']
                print('OLD_NOTE: ', old_note)
                try:
                    found_commands = str(re.compile(r'\[(.+?)\]').findall(old_note)).replace('\'', '').replace('\"', '').replace(']', '').replace('[', '')
                except AttributeError:
                    found_commands = '' 
                    print('attribute error')
                pyperclip.copy(found_commands)
                old_note = old_note.replace('<br>', '\n').replace('&lt;', '<').replace('&gt;', '>')
                user_input = input(f'\n~~~PREVIOUS NOTE~~~\n{old_note}\n-{event["summary"]}- (⌘ + v to paste): ').split(',') if found_commands else input(command_prompt(event['summary'])).split(',')
                event['description'] = parse_commands(user_input)
                
                # print(event, final_note)
                service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()
                print('#################################################################')
            except KeyError:
                user_input = input(command_prompt(event['summary'])).split(',')
                event['description'] = parse_commands(user_input)
                service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()
                print('#################################################################')


if __name__ == '__main__':
    main()