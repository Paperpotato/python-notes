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

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.events']

missing_notes = []
today = datetime.date.today().strftime("%d-%m-%Y")
full_date = datetime.date.today().strftime('%d %b %y')
print(today)

noteTemplates = {
    'd': today,
    #history
    'im': 'Cervical Spine: improved\nThoracic Spine: improved\nLumbar Spine: improved\nSacroIliac Joints: improved\nNo post-treatment soreness\n',
    'nim': 'No improvement',
    'e': 'Progress update:',
    #spinal regions and STT
    'c': 'C/Tx: C2/C5 supine manual, STT and ART to upper traps and levator scapularis, manual traction to cervical spine',
    't': 'T/Tx: T7/T10',
    'ls': 'LSI/Tx: L3/L4, L5/S1, RPI/LAS manual side posture, STT to bilateral multifidus and QLs, ART to piriformis and gluteals, PNF to hamstrings, myofascial release to low back fascia',
    'm': 'Manual adjustments: side-posture L/SI, supine C/S & T/S\nLess pain and increased ROM immediately following treatment',
    'l': 'Low force adjustments: prone activator full spine\nLess pain and increased ROM immediately following treatment',
    'lc': 'Activator C2/C5',
    #muscles'
    'bm': 'bilateral quadratus lumborum and multifidus',
    'lm': 'bilateral piriformis, hamstrings',
    'um': 'bilateral suboccipital',
    'sh': 'bilateral shoulders',
    'kn': 'pes anserine. manual traction of bilateral knees',
    #modalities
    # 'art': 'ART of above muscles', #ART already included in spinal regions & STT
    'dn': 'Dry needling of above muscles',
    'a': 'ART of above muscles',
    'ex': 'New exercises:',
    'sup': 'Supplements recommended:',
    's': ['im', 'c', 't', 'ls', 'm', 'lm', 'dn']
}

def command_prompt(patient_name):
    return f'#################################################################\n\nPATIENT: {patient_name} - {full_date}\nCOMMANDS:\n--std:\nim,c,t,ls,m,lm,dn \n--history: \nim/nim/e \n--std treatments: \nc/t/ls/(m)an/(l)ow \n--muscles: \nbm/lm/um/sh/kn \n--misc: \ndn/a/e/sup):\n'

def parse_commands(commands, prev_notes):
    full_notes = ''
    try:
        commands = re.search('\[(.+?)\]', str(commands)).group(1) if type(commands) is str else commands
    except AttributeError:
        print('no regex match')
        pass
    print(commands)
    if 'e' in commands and 's' not in commands:
        history_input = input('General history/progress input: ') + '\n\n'
        for command in noteTemplates['s']:
            full_notes = full_notes + noteTemplates[command] + '\n'
    elif 'e' in commands:
        history_input = input('General history/progress input: ') + '\n\n'
    else:
        history_input = ''
    # if 's' and 'e' in commands:
    #     full_notes = f'{prev_notes}\n\n{input("Additional notes: ")}'
    #     for command in noteTemplates['s']:
    #         full_notes = full_notes + noteTemplates[command] + '\n'
    if 's' in commands and len(commands) == 1:
        for command in noteTemplates['s']:
            full_notes = full_notes + noteTemplates[command] + '\n'
    ####### TODO: add sup catch AND EXERCISES
    elif 's' not in commands:
        for command in commands:
            command = command.strip()
            print(command)
            # command = re.sub("\'", '', command) if "\'" in command else command
            full_notes = full_notes + noteTemplates[command.strip().replace('\'', '')] + '\n'
    print('#################################################################')
    return f'<{today}>\n{history_input}{full_notes}\n{str(commands) if len(commands) != 1 else f"{str(commands)}"}'

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
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
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
                    print('attribute error. continuing...')
                # final_note = ''
                old_note = event['description']
                try:
                    found = re.search('\[(.+?)\]', old_note).group(1)
                except AttributeError:
                    found = '' 
                pyperclip.copy(found)
                # print(old_note)
                # if 'e' in event['description']:
                user_input = input(f'{old_note} -{event["summary"]}- (p to paste): ').split(',') if found else input(command_prompt(event['summary'])).split(',')
                if user_input == 'p':
                    #call function - parse_notes()
                    final_note = pyperclip.paste()
                else:
                    event['description'] = parse_commands(user_input, '')
                
                # print(event, final_note)
                service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()
                print('#################################################################')
            except KeyError:
                user_input = input(command_prompt(event['summary'])).split(',')
                #call parse notes and update event description
                event['description'] = parse_commands(user_input, '')
                # print(event, parse_commands(user_input, ''))
                service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()
                print('#################################################################')

    



if __name__ == '__main__':
    main()