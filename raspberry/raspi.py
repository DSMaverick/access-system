import PySimpleGUI as sg
import subprocess

def run_script(script_name, *args):
    try:
        subprocess.run(['python', script_name] + list(args), check=True)
    except subprocess.CalledProcessError as e:
        sg.popup(f"S-a produs o eroare in timp ce rula {script_name}\n{e}")

menu = [
    [sg.Button('Legatura cu Serverul')],
    [sg.Text('Pentru a face legatura cu serverul')],
    [sg.Text('Asigura-te ca Flask ruleaza pe unul dintre IPuri!')],
    [sg.Button('Start')],
    [sg.Text('Pentru a executa aplicatia din partea de RBI PI')],
    [sg.Text('')],
    [sg.Button('Exit')]

]

window = sg.Window('Meniu RBI', menu)

while True:
    event, values = window.read(timeout=100)

    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break
    elif event == 'Legatura cu Severul':
        run_script('requests.py')
    elif event == 'Start':
        run_script('main.py')

window.close()