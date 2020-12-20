from __future__ import print_function
import datetime
# from os import SCHED_IDLE
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
command_df = cd.df

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

    return output

def command_prompt(patient_name):
    return f'#################################################################\n\nPATIENT: {patient_name} - {full_date}\n\n{command_df}\n>>> '

def standard_commands(command):
    treatment_note = ''
    for standard_command in command_dict[command]:
        if standard_command == 'e':
            treatment_note += command_dict[standard_command] + '\n' + input('General history/progress input: ') + '\n\n'
        else:
            treatment_note += command_dict[standard_command] + '\n'        
    return treatment_note

def parse_commands(commands):
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
            history_input = input('General history/progress input: ') + '\n\n'
        elif 'init' in commands:
            history_input = init_consult()
        else:
            history_input = ''
        for command in commands:
            command = command.strip()
            if command == 'e':
                continue
            if 's' == command or 'sl' == command or 'sd' == command or 'sdl' == command or 'sdu' == command:
                treatment_note += standard_commands(command)
            else:
                treatment_note += command_dict[command]
        return f'<{today}>\n{history_input}{treatment_note}\n{str(commands) if len(commands) != 1 else f"{str(commands)}"}'

def main():
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
    yesterday = datetime.date.today() - datetime.timedelta(1)
    yesterday_formatted = yesterday.strftime("%Y-%m-%d") + 'T00:00:00+08:00'
    yesterday_formatted_for_comparision = yesterday.strftime("%d-%m-%Y")
    now = datetime.date.today().strftime("%Y-%m-%d") + 'T00:00:00+08:00'
    print(now)
    print('Getting the upcoming 70 events')
    events_result = service.events().list(calendarId='primary', timeMin=yesterday_formatted,
                                        maxResults=70, singleEvents=True,
                                        orderBy='startTime').execute()

    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start_date = event['start'].get('dateTime', event['start'].get('date'))
        start_time = event['start'].get('dateTime', event['start'].get('time'))
        print(f'entry for: {event["summary"]}')
        if start_time == None or 'Mx' in event['summary']:
            print(f'Skipping event: {event["summary"]}')
        else:
            try:
                previous_date = re.search('\d+-\d+-\d+', event['description'])
                # print(f'Found date: {previous_date.group(0)}')
                try:
                    if previous_date.group(0) == today or previous_date.group(0) == yesterday_formatted_for_comparision:
                        # print("today's note found, skipping...")
                        continue
                except AttributeError:
                    print('attribute error. Possibly invalid notes? continuing...')
                # final_note = ''
                old_note = event['description']
                # print('OLD_NOTE: ', old_note)
                try:
                    found_commands = str(re.compile(r'\[(.+?)\]').findall(old_note)).replace('\'', '').replace('\"', '').replace(']', '').replace('[', '')
                except AttributeError:
                    found_commands = '' 
                    print('attribute error')
                pyperclip.copy(str(found_commands))
                old_note = old_note.replace('<br>', '\n').replace('&lt;', '<').replace('&gt;', '>')
                user_input = input(f'\n~~~PREVIOUS NOTE~~~\n{old_note}\n-{event["summary"]}- (⌘ + v to paste): ').split(',') if found_commands else input(command_prompt(event['summary'])).split(',')
                pyperclip.copy(str(user_input))

                if user_input != ['']:
                    try:
                        event['description'] = parse_commands(user_input)
                    except KeyError:
                        # Add user_input into clipboard, parse that and execute parse_commands? 
                        
                        print('Key Error: add commands first')
                        user_input = input(f'\n~~~PREVIOUS NOTE~~~\n{old_note}\n-{event["summary"]}- (⌘ + v to paste): ').split(',') if found_commands else input(command_prompt(event['summary'])).split(',')
                        event['description'] = parse_commands(user_input)
                else:
                    print(event['description'])
                    event['description'] = f'<{today}>' if event['description'] == None else f'<{today}>\n' + event['description']
                    print('No entry. Skipping...')
                
                # print(event, final_note)
                service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()
                print('#################################################################')
            except KeyError:
                print('Key Error: no previous note')
                user_input = input(command_prompt(event['summary'])).split(',')
                event['description'] = parse_commands(user_input)
                service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()
                print('#################################################################')


if __name__ == '__main__':
    main()