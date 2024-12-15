import PySimpleGUI as sg
import subprocess
import threading
import webbrowser

def run_script(script_name, *args):
    try:
        subprocess.run(['python', script_name] +list(args), check=True)
    except subprocess.CalledProcessError as e:
        sg.popup(f"S-a produs o eroare in timp ce rula {script_name}:\n{e}")

def open_webpage(url):
    webbrowser.open(url)

menu = [
    [sg.Button('Antrenare Sistem')],
    [sg.Text('Antrenarea sistemul folosind imagini din training-data')],
    [sg.Button('Predictie')],
    [sg.Text('Predicere folosind o imagine sample si sistemul antrenat')],
    [sg.Button('Initializare Baza de Date')],
    [sg.Text('Initializarea Bazei de Date si rularea schemei.sql')],
    [sg.Button('Start Server')],
    [sg.Text('Pornim serverul Flask pentru a putea primi date din RBI')],
    [sg.Button('Loguri de Access')],
    [sg.Text('Afisarea datelor inregistrate')],
    [sg.Text('')],
    [sg.Button('Exit')]
]

#Create the window for the menu
window = sg.Window('Meniu Server', menu)

#Event loop to process events and get the values of inputs
while True:
    event, values = window.read(timeout=100)  #Timeout to check the queue periodically
    
    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break
    elif event == 'Loguri de Access':
        open_webpage('http://127.0.0.1:5000/')
    elif event == 'Antrenare Sistem':
        run_script('machine_learning.py', 'face.png', 'train')
    elif event == 'Predictie':
        run_script('machine_learning.py', 'face.png', 'predict')
    elif event == 'Initializare Baza de Date':
        run_script('backend.py', 'initdb')
    elif event == 'Start Server':
        threading.Thread(target=run_script, args=('backend.py', 'run')).start()

#Close the window
window.close()