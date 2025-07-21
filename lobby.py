# lobby_manager.py
import threading
from collections import defaultdict

class LobbyManager:
    def __init__(self):
        self.lobbies = defaultdict(list)  # lobby_code -> [(conn, addr)]
        self.locks = defaultdict(threading.Lock)

    def join_lobby(self, lobby_code, conn, addr):
        with self.locks[lobby_code]:
            self.lobbies[lobby_code].append((conn, addr))
            print(f"{addr} joined lobby '{lobby_code}'")

    def leave_lobby(self, lobby_code, conn, addr):
        with self.locks[lobby_code]:
            self.lobbies[lobby_code] = [c for c in self.lobbies[lobby_code] if c[0] != conn]
            print(f"{addr} left lobby '{lobby_code}'")

            if not self.lobbies[lobby_code]:  # If lobby is empty, delete it
                del self.lobbies[lobby_code]
                del self.locks[lobby_code]
                print(f"Lobby '{lobby_code}' deleted.")

    def broadcast(self, lobby_code, message, sender_conn):
        with self.locks[lobby_code]:
            for conn, _ in self.lobbies[lobby_code]:
                if conn != sender_conn:
                    try:
                        conn.send(message.encode())
                    except:
                        conn.close()
                        self.lobbies[lobby_code].remove((conn, _))
    
    def list_lobbies(self):
        return list(self.lobbies.keys())
