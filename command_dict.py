import datetime
import pandas as pd


today = datetime.date.today().strftime("%d-%m-%Y")

command_dict = {
    'd': today,
    #history
    'im': 'General progress:\nCervical Spine: improved\nThoracic Spine: improved\nLumbar Spine: improved\nSacroIliac Joints: improved\nNo post-treatment soreness\n',
    'n': 'No improvement',
    'e': 'History:',
    'init': '',
    #spinal regions and method
    'f': 'C/Tx: C2/C5 supine manual, STT and ART to upper traps and levator scapularis, manual traction to cervical spine\nT/Tx: T7/T10\nLSI/Tx: L3/L4, L5/S1, RPI/LAS manual side posture, STT to bilateral multifidus and QLs, ART to piriformis and gluteals, PNF to hamstrings, myofascial release to low back fascia',
    'tmj': 'Temporalis, masseter, ptyergoids STT and ART.',
    'c': 'C/Tx: C2/C5 supine manual, STT and ART to upper traps and levator scapularis, manual traction to cervical spine',
    't': 'T/Tx: T7/T10',
    'ls': 'LSI/Tx: L3/L4, L5/S1, RPI/LAS manual side posture, STT to bilateral multifidus and QLs, ART to piriformis and gluteals, PNF to hamstrings, myofascial release to low back fascia',
    'm': 'Manual adjustments: side-posture for L/SI, supine for C/S & T/S\nLess pain and increased ROM immediately following treatment',
    'l': 'Low force adjustments: prone activator full spine\nLess pain and increased ROM immediately following treatment',
    'lc': 'Activator C2/C5',
    #muscles'
    'bm': 'bilateral quadratus lumborum and multifidus',
    'lm': 'bilateral piriformis, hamstrings',
    'um': 'bilateral suboccipital',
    'sh': 'bilateral shoulders',
    'kn': 'pes anserine. manual traction of bilateral knees',
    'pf': 'low-dye taping of plantar fascia',
    'wr': 'low-dye taping of wrists for stability',
    'el': 'wrist extensors',
    'calf': 'peroneals, gastrocnemius and soleus',
    #modalities
    'dn': 'Dry needling of above muscles',
    'cup': 'Myofascial cupping',
    'a': 'ART of above muscles',
    'sd': ['e', 'im', 'c', 't', 'ls', 'm', 'lm', 'dn', 'a'],
    'sdl': ['e', 'im', 'ls', 'dn', 'c', 't', 'm', 'lm', 'a'],
    'sdu': ['e', 'im', 'c', 'dn', 't', 'ls', 'm', 'lm', 'a'],
    's': ['e', 'im', 'c', 't', 'ls', 'm', 'lm', 'a'],
    'sl': ['e', 'im', 'c', 't', 'ls', 'm', 'lm', 'dn', 'a']
}

initial_dict = {
    #'Negative for 5D\'s & 3N\'s'
    # ['Site', 'Onset', 'Character', 'Radiation', 'Associated', 'Timing', 'Exacerbating/Relieving', 'Severity']
}
command_df_raw = {
    'Std Tx': ['s', 'sd', 'sdu', 'sdl'],
    '  History': ['e', 'im', 'n', 'init'],
    '  Joints': ['f', 'c', 't', 'ls', 'tmj'],
    '  Muscles': ['bm', 'lm', 'um', 'sh', 'kn', 'pf', 'wr', 'el', 'calf'],
    '  Techniques': ['m', 'l', 'lc', 'dn', 'cup', 'a']
    }
max_length = 0
for key in command_df_raw:
    max_length = len(command_df_raw[key]) if len(command_df_raw[key]) >= max_length else max_length

for key in command_df_raw:
    delta = max_length - len(command_df_raw[key])
    for x in range(delta):
        command_df_raw[key].append('')

df = pd.DataFrame(data=command_df_raw)
df.to_string(index=False)

# print(df)