import threading
import socket
import time
import queue

class initNetwork(threading.Thread):
    def __init__(self,host, port, recv_queue, send_queue, chunk):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.recv_queue = recv_queue
        self.send_queue = send_queue
        self.chunk = chunk
        self.socket = None
        while self.socket is None:
            self.socket = self.init_network(self.host, self.port)
            if self.socket is not None:
                self.instantiateClass()
            else:
                print("retrying in 5 seconds")
                time.sleep(5)
        
        print("network ok")
        
    
    def run(self):
        self.netSend.start()
        self.netRecv.start()
        while True:
            if self.netRecv.connected == False or self.netSend.connected==False:
                print("Disconnected")
                self.netRecv.connected == False
                self.netSend.connected == False
                time.sleep(1)
                self.socket = None
                while self.socket is None:
                    self.socket = self.init_network(self.host, self.port)
                    if self.socket is not None:
                        self.instantiateClass()
                        self.netSend.start()
                        self.netRecv.start()
                    else:
                        print("retrying in 5 seconds")
                        time.sleep(5)
            time.sleep(0.1)

        print("Network failed")


    def instantiateClass(self):
        self.netSend = networkSend(self.socket,self.send_queue)
        self.netRecv = networkReceive(self.socket,self.recv_queue,self.chunk)
        self.netSend.daemon = True
        self.netRecv.daemon = True
        self.netRecv.connected == True
        self.netSend.connected == True

    def init_network(self, host, port):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            soc.connect((host, port))
        except ConnectionRefusedError:
            print("connexion refused by server")
            return None
        except TimeoutError:
            print("Time out on server")
            return None
        else:
        #self.client_soc.settimeout(10)
            print("Connected with server")
            return soc





class networkSend(threading.Thread):
    def __init__(self, socket, send_queue):
        threading.Thread.__init__(self)
        self.socket = socket
        self.send_queue = send_queue
        self.connected = True
         
    def run(self):
        print("send loop ok")
        while self.connected:
            try:
                cmd = self.send_queue.get_nowait()
            except queue.Empty:
                #print("No command in queue")
                pass
            else:
                try:
                    self.socket.send(cmd)
                    #print("sent {} bytes".format(len(cmd)))
                    
                except ConnectionResetError:
                    print("Connexion lost with server")
                    self.connected = False
                    #time.sleep(5)
                    #self.init_network()
                    break
                except ConnectionAbortedError:
                    print("Server aborded connexion")
                    self.connected = False
                    #time.sleep(5)
                    #self.init_network()
                except OSError:
                    print("Socket not connected")
                    self.connected = False
                    #time.sleep(5)
                    #self.init_network()
 
        #self.socket.close()
        print("Bye bye send !")


class networkReceive(threading.Thread):
    def __init__(self, socket,recv_queue,chunk):
        threading.Thread.__init__(self) 
        self.socket = socket
        self.recv_queue = recv_queue
        self.chunk = chunk
        self.connected = True


    def run(self):
        print("receive loop ok")
        in_data =b""
        while self.connected:
            try:
                
                while len(in_data) != self.chunk:
                    in_data +=  self.socket.recv(self.chunk)

                if self.recv_queue.qsize() > 10:
                    with self.audio.reader.frames.mutex:
                        self.audio.reader.frames.queue.clear()
                self.recv_queue.put_nowait(in_data)
                
                #print(in_data)
            except ConnectionResetError:
                print("Connexion to server lost")
                self.connected = False
            except socket.timeout:
                print("recv time out")
                self.connected = False
            except Exception as e:
                print(e)
                self.connected = False
                #pass
        print("Bye bye recv.")

    
            