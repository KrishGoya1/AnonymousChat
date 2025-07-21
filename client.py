import socket
import threading

def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024).decode()
            if not msg:
                break
            print("\n" + msg)
        except:
            break

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 12345))

name = input("Your name: ")

# Join a lobby
lobby_prompt = client_socket.recv(1024).decode()
print(lobby_prompt)
lobby_code = input(">>> ").strip()
client_socket.send(lobby_code.encode())

# Start listening
threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

try:
    while True:
        msg = input()
        if msg.strip().lower() == "exit":
            client_socket.send(f"{name} has left the chat.".encode())
            break
        full_msg = f"{name}: {msg}"
        client_socket.send(full_msg.encode())
except KeyboardInterrupt:
    print("\nExiting chat.")
finally:
    client_socket.close()
