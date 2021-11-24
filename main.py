from __future__ import print_function
import datetime
# from os import SCHED_IDLE

import pyperclip
import re
import functions as fx

today = datetime.date.today().strftime("%d-%m-%Y")

print('Writing notes for:', today)

pyperclip.copy('mild lbp and stiffness')

def main():
    service = fx.build_service()
    # Call the Calendar API
    yesterday = datetime.date.today() - datetime.timedelta(int(input('Please enter number of days before today: ')))
    yesterday_formatted = yesterday.strftime("%Y-%m-%d") + 'T00:00:00+08:00'
    yesterday_formatted_for_comparision = yesterday.strftime("%d-%m-%Y")
    print(today)
    print('Getting the upcoming 70 events')
    events_result = service.events().list(calendarId='primary', timeMin=yesterday_formatted,
                                        maxResults=100, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start_time = event['start'].get('dateTime', event['start'].get('time'))
        patient_name = event['summary']
        print(f'entry for: {patient_name}')
        event_title = patient_name.lower()
        if start_time == None or 'mx' in event_title or 'check' in event_title or 'cx' in event_title:
            print(f'Skipping event: {patient_name}')
        else:
            try:
                # CHECK IF THE PATIENT ALREADY EXISTS IN THE DATABASE, stored in JSON object in other file. 
                # IF SO, COPY AND PASTE NOTE AND INCREMENT COUNTER, ELSE, RUN THROUGH FULL PROMPT
                # IF COUNTER IS <=12, RUN THROUGH FULL PROMPT, RESET COUNTER AND REQUEST HISTORY. 
                
                #Solution is somple: store patient note objects in proper database, not in calendar notes. 
                
                # Get date from event. If it exists, it means the note was already written (today)
                previous_date = re.search('\d+-\d+-\d+', event['description'])
                try:
                    if previous_date.group(0) == today or previous_date.group(0) == yesterday_formatted_for_comparision:
                        #notes already exist for this patient
                        continue
                except AttributeError:
                    print('attribute error. Possibly invalid notes? continuing...')
                old_note = event['description']
                try:
                    found_commands = str(re.compile(r'\[(.+?)\]').findall(old_note)).replace('\'', '').replace('\"', '').replace(']', '').replace('[', '')
                except AttributeError:
                    found_commands = '' 
                    print('attribute error')
                pyperclip.copy(str(found_commands))
                old_note = fx.decode_html(old_note)
                user_input = input(f'\n~~~PREVIOUS NOTE~~~\n{old_note}\n-{patient_name}- (⌘ + v to paste): ').split(',') if found_commands else input(fx.command_prompt(patient_name)).split(',')
                pyperclip.copy(str(user_input))

                if user_input != ['']:
                    event['description'] = fx.parse_commands(user_input)
                else:
                    print(event['description'])
                    event['description'] = f'<{today}>' if event['description'] == None else f'<{today}>\n' + event['description']
                    print('No entry. Skipping...')
                
                # print(event, final_note)
                service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()
                fx.print_line()
            except KeyError:
                print('Key Error: no previous note')
                user_input = input(fx.command_prompt(patient_name)).split(',')
                event['description'] = fx.parse_commands(user_input)
                service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()
                fx.print_line()


if __name__ == '__main__':
    main()