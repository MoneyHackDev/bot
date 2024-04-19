import multiprocessing
import time

def run_script(script_name):
    import subprocess
    subprocess.run(['python', script_name])

if __name__ == '__main__':
    scripts = ['bot1.py', 'bot2.py', 'bot3.py']
    processes = []

    try:
        for script in scripts:
            process = multiprocessing.Process(target=run_script, args=(script,))
            processes.append(process)
            process.start()

        for process in processes:
            process.join()

    except KeyboardInterrupt:
        print("Ctrl+C detected. Terminating child processes...")
        for process in processes:
            process.terminate()
            process.join()
