import socket
def poke():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('0.0.0.0', 8888))
    s.sendall('poke')

if __name__=="__main__":
    poke()
