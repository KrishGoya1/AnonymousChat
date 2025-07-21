# server.py
import socket
import threading
from lobby import LobbyManager

lobby_manager = LobbyManager()

def handle_client(conn, addr):
    try:
        conn.send("Enter lobby code: ".encode())
        lobby_code = conn.recv(1024).decode().strip()

        if not lobby_code:
            conn.send("Invalid lobby code.\n".encode())
            conn.close()
            return

        lobby_manager.join_lobby(lobby_code, conn, addr)
        conn.send(f"Joined lobby '{lobby_code}'. Type 'exit' to leave.\n".encode())

        while True:
            msg = conn.recv(1024).decode()
            if not msg or msg.strip().lower() == "exit":
                break
            print(f"[{lobby_code}] {addr}: {msg}")
            lobby_manager.broadcast(lobby_code, msg, conn)

    except:
        pass
    finally:
        lobby_manager.leave_lobby(lobby_code, conn, addr)
        conn.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12345))
    server_socket.listen()
    print("Server is running. Waiting for clients...")

    try:
        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\nServer shutting down.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
