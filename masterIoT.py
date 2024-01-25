import multiprocessing
import subprocess

# Definir una función para ejecutar cada script
def run_script1(script):
    subprocess.call(['streamlit', 'run', script])  # Ejecutar el script con el comando 'python'

def run_script2(script):
    subprocess.call(['python', script])  # Ejecutar el script con el comando 'python'

if __name__ == '__main__':
    # Definir los nombres de los scripts a ejecutar
    front = 'front.py'
    backend = 'backend.py'

    # Crear dos procesos para ejecutar los scripts
    p1 = multiprocessing.Process(target=run_script1, args=(front,))
    p2 = multiprocessing.Process(target=run_script2, args=(backend,))

    # Iniciar los procesos
    p1.start()
    p2.start()

    # Esperar a que los procesos terminen
    p1.join()
    p2.join()