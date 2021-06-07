import PySimpleGUI as sg
from database import create_database, update_database
from sample import sample_file, sample_mic
from compare import compare

layout = [
    [sg.Button('Open file', initial_folder='audio_database', file_types='*.wav'),
     sg.Button('Record audio'),
     sg.Text('Recording length:'),
     sg.Input(5, size=(5, 1)),
     sg.Text('[s]')],

    [sg.HorizontalSeparator()],

    [sg.Button('Run', button_color=('white', 'red')),
     sg.Button('Create database'),
     sg.Button('Update database')]
]

window = sg.Window('TP3').Layout(layout)

seg = 5
sample_fp = 'None'
while True:  # Event Loop
    event, values = window.Read()
    if values is not None:
        if values[0] is not None:
            seg = float(values[0])
    if event in (None, 'Exit'):
        break
    if event == 'Open file':
        try:
            sample_fp = sample_file()
        except FileNotFoundError:
            print('File not selected.')
            continue
        print('File selected.')
    elif event == 'Record audio':
        sample_fp = sample_mic(seg)
    elif event == 'Create database':
        create_database('audio_database')
    elif event == 'Update database':
        update_database('audio_database')
    elif event == 'Run':
        compare(sample_fp)
window.Close()
