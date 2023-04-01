import socket
import threading
import pickle

HEADER = 1024
PORT = 19699
SERVER = "" #Replace with your server machine ip
ADDR = (SERVER, PORT)
PAYLOAD_BITS = 8

connections = set()

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected")
    connected = True
    connections.add(conn)
    print(f"CONNECTIONS: {connections}")
    data = b''
    while connected:
        data += conn.recv(HEADER)
        msg_length = int(data[:PAYLOAD_BITS])#.decode()
        data = data[PAYLOAD_BITS:]
        # print(f"\x1b[31mSERVER MESSAGE LENGTH: {msg_length}\x1b[0m")
        while len(data)<msg_length:
            data += conn.recv(HEADER)

        message=pickle.loads(data)
        if(message == "!DISCONNECT"):
            print(f"\x1b[31m{conn} DISCONNETED\x1b[0m")
            connected=False
            connections.discard(conn)
        else:
            send(conn, data[:msg_length],msg_length)
            data = data[msg_length:]
    conn.close()
    
def send(conn, data, msg_length):
    for c in connections:
        if c is not conn:
            send_length = str(msg_length).encode('utf-8')
            send_length = b' '*(PAYLOAD_BITS-len(send_length)) + send_length
            message = send_length+data
            # print(f"\x1b[34mSERVER SIDE SENDING MESSAGE: {message}\x1b[0m")
            c.send(message)


def start():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(ADDR)
        server.listen(5)
        print(f"[LISTENING] server is listening on {SERVER, PORT}")
        threading.Thread(target=send)
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count()-1}")

print("[STARTING] server is starting...")
start()