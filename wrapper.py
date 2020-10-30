import os
import signal
import platform
import datetime
import time
import requests
import subprocess as sub
from threading import Thread

PY_FILE = "client.py"
PY_PATH = os.path.join("usr/local/bin/client-prescient", PY_FILE)
LOG_FILE2 = "log.log"
LOG_FILE = os.path.join("usr/local/bin/client-prescient", LOG_FILE2)

PAUSE = 8

SERVER_URL_GET = "http://prescient.cfapps.eu10.hana.ondemand.com/statecam"
# SERVER_URL_SET = "http://localhost:8000/state/r/"
# SERVER_URL_GET = "http://localhost:8000/state/"

state = 0


def getState():
    try:
        s = int(requests.get(SERVER_URL_GET).text)

        if s == 1:
            return True

    except Exception as e:
        print(e)
        return False

    return False


class Wrapper(object):
    def __init__(self, path, exe):
        self.active = False

        self.run(path, exe)

    @staticmethod
    def log(text):
        with open(LOG_FILE2, "a") as file:
            s = datetime.datetime.now().strftime("%H:%M:%S - %B %d, %Y") + " : " + text + "\n"
            print(s)
            file.write(s)

    def run(self, path, exe):
        while True:
            while self.active:
                p = Poper(path, exe)
                p.run()

                while not p.done:
                    isKilled = not getState()
                    if isKilled:
                        self.active = False
                        print("Disabled...")
                        self.log("Disabled...")

                        try:
                            os.kill(p.p.pid, signal.SIGTERM)
                        except PermissionError:
                            os.system("Taskkill /PID %d /F" % p.p.pid)
                        break

                    time.sleep(PAUSE)

                self.log(str(p.code) + " - " + str(p.out))

                if not self.active:
                    break

                print("Restarting...")
                self.log("Restarting")
                time.sleep(PAUSE)

            if not self.active:
                self.active = getState()

            if not self.active:
                time.sleep(PAUSE)


class Poper(object):
    def __init__(self, path, executable=None, stdout=True, stdin=False, stderr=False, shell=False, encoding=False):
        self.p = None
        self.done = False
        self.killed = False
        self.code = None
        self.out = ""

        self.args = [path] if executable is None else [executable, path]

        self.stdout = None if not stdout else sub.PIPE
        self.stdin = None if not stdin else sub.PIPE
        self.stderr = None if not stderr else sub.PIPE

        self.shell = shell
        self.encoding = None if not encoding else encoding

    def run(self):
        self.p = sub.Popen(self.args, shell=self.shell, stdout=self.stdout, stdin=self.stdin, stderr=self.stderr,
                           encoding=self.encoding, universal_newlines=True)
        self.listen()

    def listen(self):
        def readInThread(this):
            for line in iter(this.p.stdout.readline, b""):
                if this.p.poll() is not None or this.killed:
                    this.code = this.p.poll()
                    this.done = True
                    break

                if type(line) == bytes:
                    line = line.decode()

                if line != "":
                    this.out += line

                time.sleep(0.1)

        self.process = Thread(target=readInThread, args=[self])
        self.process.start()


if __name__ == "__main__":
    if platform.system() == "Windows":
        Wrapper(PY_PATH, "python")
    else:
        Wrapper(PY_PATH, "python3")
