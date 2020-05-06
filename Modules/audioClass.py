import threading
import socket
import pyaudio
import wave
import time
import queue

class initAudio:
    def __init__(self, forma=pyaudio.paInt16, channelsIn=2, channelsOut=2, rate=44100,chunk=4096, daemon = False, test=True):
        self.format = forma
        self.channelsIn = channelsIn
        self.channelsOut = channelsOut
        self.rate = rate
        self.chunk = chunk
        self.daemon = daemon

        print("Init audio system.")
        self.audio = pyaudio.PyAudio()
        print("Starting reader thread.")
        self.reader = readAudio(self.audio,forma=self.format,channels=self.channelsOut,
                                rate=self.rate,chunk=self.chunk, daemon=self.daemon, test=test)
        self.reader.daemon = True
        self.reader.start()

        print("Starting capture thread.")
        self.capture = micCapture(self.audio,forma=self.format,channels=self.channelsIn,
                                rate=self.rate,chunk=self.chunk, daemon=self.daemon)
        self.capture.daemon = True
        self.capture.start()

        #self.reader.frames = self.capture.audioFrame

        print("Audio init done !")
        
    
    def print_list_devices(self):
        for i in range(self.audio.get_device_count()):
            print (i, self.audio.get_device_info_by_index(i))
            print()

    def printDefaultDevices(self):
        print(self.audio.get_default_input_device_info())
        print(self.audio.get_default_output_device_info())


class micCapture(threading.Thread):
    def __init__(self, audio, forma=pyaudio.paInt16, channels=2, rate=44100,chunk=4096,daemon=False):
        threading.Thread.__init__(self)

        self.format = forma
        self.channels = channels
        self.rate = rate
        self.chunk = chunk
        self._run = True
        self.audio = audio
        self.audioFrame = queue.Queue()
        if daemon == True:
            micCapture.setDaemon(self,daemonic=True)
        #print(self.chunk)
        #self.frames = []

    def callback(self, in_data, frame_count, time_info, status):
        #print(len(in_data))
        #sent = self.network.client_soc.send(in_data)
        self.audioFrame.put(in_data)
        #print("sent {} bytes".format(len(in_data)))
        return (None, pyaudio.paContinue)

    def run(self):
        print("Ready to capture")
        self.stream = self.audio.open(format=self.format, channels=self.channels,
                rate=self.rate, input=True,
                frames_per_buffer=int(self.chunk/4),stream_callback=self.callback,start=False)
        #print(self.stream._frames_per_buffer)
        # while self._run:
        #     data = self.stream.read(self.CHUNK)
        #     #self.frames.append(data)
        #     try:
        #         self.network.client_soc.sendall(data)
        #     except socket.timeout:
        #         pass
        while self._run:
            time.sleep(0.1)
        print("capture done")

    def stop(self):
        self._run = False
        #time.sleep(1)
        self.stream.stop_stream()
        self.stream.close()

class readAudio(threading.Thread):
    def __init__(self,audio, forma=pyaudio.paInt16,channels=2,rate=44100,chunk=4096,test=True, daemon = False):
        threading.Thread.__init__(self)
        self.audio = audio
        self.frames = queue.Queue()
        self.format = forma
        self.channels = channels
        self.rate = rate
        self.chunk = chunk
        self._run = True
        self.buffer = 3

        if daemon == True:
            readAudio.setDaemon(self,daemonic=True)

        if test == True:
            self.testAudio()

        
        
    def testAudio(self):
        filename = "Media\\start.wav"
        wf = wave.open(filename, 'rb')

        stream = self.audio.open(format = self.audio.get_format_from_width(wf.getsampwidth()),
                channels = wf.getnchannels(),
                rate = wf.getframerate(),
                output = True)

        data = wf.readframes(1024)
        # Play the sound by writing the audio data to the stream
        while data != b'':
            #print(data)
            stream.write(data)
            data = wf.readframes(1024)
        stream.close()

    def run(self):
        self.stream = self.audio.open(format=self.format,
                channels=self.channels,
                rate=self.rate,
                output=True,start=False, frames_per_buffer=self.chunk)

        print("Ready to read")
        while self._run:
            #print(len(self.frames))
            if self.frames.qsize()>self.buffer and self.stream.is_active():
                try:
                    frame = self.frames.get_nowait()
                except queue.Empty:
                    pass
                else:
                    print("read {} bytes".format(len(frame)))
                    self.stream.write(frame)
            #time.sleep(0.1)
        print("Reader closed")

    def callback(self, in_data, frame_count, time_info, status):
        print("in callback")
        data = self.frames.get()
        return (data, pyaudio.paContinue)

    def stop(self):
        self._run = False
        #time.sleep(1)
        self.stream.stop_stream()
        self.stream.close()