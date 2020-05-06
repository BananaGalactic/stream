import threading
import queue
import time

class clientConsole(threading.Thread):
    def __init__(self,daemon=False , autoStart=False):
        threading.Thread.__init__(self)
        self._run = True
        self.cmd_queue = queue.Queue()

        if daemon == True:
            clientConsole.setDaemon(self,daemonic=True)

        if autoStart == True:
            self.start()

    def run(self):
        print("Type help for list of commands.")
        while self._run:
            try:
                out_data = input("")
            except EOFError:
                break
            else:
                self.cmd_queue.put(out_data)
                if out_data=='bye':
                    self.stop()
                    break
                    
                if out_data=='help':
                    self.printCommands()
                
        print("Console thread stopped")


    def printCommands(self):
        print("")
        print("  Commands  |  Options   |          Info                   ")
        print("-----------------------------------------------------------")
        print("  bye       |    None    |  Exit program                   ")
        print("  help      |    None    |  Display all available commands ")
        print("  acquire   | start/stop |  Start/stop mic capture         ")
        print("  bufferin  |    None    |  Give size of the input buffer  ")

    def stop(self):
        #print("stopping")
        self._run = False
        #time.sleep(0.1)

    def getCmd(self):
        try:
            cmd = self.cmd_queue.get_nowait()
            return cmd
        except queue.Empty:
            return ""
        
        


if __name__ == "__main__":
    console = clientConsole(daemon=False)
    try:
        while True:
            cmd = console.getCmd()
            if cmd == "bye":
                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting from keyboard")
        console.stop()
    console.join()
    print("Bye")
        
    


