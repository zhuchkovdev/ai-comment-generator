import PySimpleGUI as sg
from model import generate_comment

# Constants
CODE_KEY = "CODE"
DOCSTRING_CODE = "DOCSTRING"

# Define layout
layout = [
    [ sg.Text("Source code") ],
    [ sg.Multiline(size=(50, 15), key=CODE_KEY, enable_events=True) ],
    [ sg.Button("Generate"), ],
    [ sg.Text("Generated docstring comment") ],
    [ sg.Multiline(size=(50, 4), disabled=True, no_scrollbar=True, key=DOCSTRING_CODE) ]
]

# Create window
window = sg.Window("Demo", layout, size=(800,400), resizable=True, element_justification='c')

# Event loop
while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    elif event == "Generate":
        code = values[CODE_KEY]
        window[DOCSTRING_CODE].update(generate_comment(code, 25))

window.close()