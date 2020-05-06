from Modules.consoleClass import clientConsole
from Modules.audioClass import initAudio
from Modules.networkClass import initNetwork
import threading

import time

class app(threading.Thread):
    def __init__(self,console, audio, network):
        threading.Thread.__init__(self)
        self.console = console
        self.audio = audio
        self.network = network
        self.network.daemon = True
        self.network.start()

    def run(self):
        while True:
            #print("la")
            cmd = self.console.getCmd()

            if cmd == "bye":
                #print("ici")
                break
            elif cmd =="bufferin":
                print("Buffer in has {} frames.".format(self.audio.capture.audioFrame.qsize()))
            elif cmd =="bufferout":
                print("Buffer out has {} frames.".format(self.audio.reader.frames.qsize()))
            elif cmd =="buffers":
                print("Buffer out has {} frames.".format(self.audio.reader.frames.qsize()))
                print("Buffer in has {} frames.".format(self.audio.capture.audioFrame.qsize()))
            elif cmd == "acquire start":
                self.audio.capture.stream.start_stream()
            elif cmd == "acquire stop":
                self.audio.capture.stream.stop_stream()
            elif cmd == "reader start":
                self.audio.reader.stream.start_stream()
            elif cmd == "reader stop":
                self.audio.reader.stream.stop_stream()
            elif cmd == "reset":
                with self.audio.capture.audioFrame.mutex:
                    self.audio.capture.audioFrame.queue.clear()
            elif "setbuffer" in cmd:
                data = cmd.split(" ")[1]
                self.audio.chunk =int(data)
                self.network.chunk = int(data)
            elif cmd == "testaudio":
                self.audio.reader.testAudio()
                
            elif cmd == "start":
                self.audio.capture.stream.start_stream()
                self.audio.reader.stream.start_stream()

            

            time.sleep(0.1)
        self.audio.capture.stop()
        self.audio.reader.stop()
        self.audio.audio.terminate()

        print("exit")


console = clientConsole(daemon=True, autoStart=True)
audio = initAudio(chunk=1024,daemon=True, test=False)
network = initNetwork("192.168.1.10", 10000, audio.reader.frames,audio.capture.audioFrame,chunk=1024)
app = app(console,audio, network)
app.start()





