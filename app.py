# app.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from collections import defaultdict
import asyncio
import threading
import sys
from datetime import datetime
from fastapi.staticfiles import StaticFiles
import os


MAX_MSG_LENGTH = 500

app = FastAPI()
app.mount("/static", StaticFiles(directory=os.path.dirname(__file__)), name="static")

lobbies = defaultdict(list)  # lobby_code -> list of WebSockets
locks = defaultdict(asyncio.Lock)
shutdown_flag = False  # Will be set True when we want to exit

@app.get("/")
async def get():
    with open("chat.html") as f:
        return HTMLResponse(f.read())

@app.websocket("/ws/{lobby_code}/{username}")
async def websocket_endpoint(websocket: WebSocket, lobby_code: str, username: str):
    await websocket.accept()
    async with locks[lobby_code]:
        lobbies[lobby_code].append(websocket)
    await broadcast(lobby_code, f"🔵 {username} joined.", websocket)

    try:
        while True:
            data = await websocket.receive_text()
            if len(data.strip()) == 0 or len(data) > MAX_MSG_LENGTH:
                continue
            await broadcast(lobby_code, f"{username}: {data}", websocket)
    except WebSocketDisconnect:
        await remove_connection(lobby_code, websocket, username)

async def broadcast(lobby_code: str, message: str, sender_ws: WebSocket = None):
    async with locks[lobby_code]:
        for ws in lobbies[lobby_code]:
            try:
                await ws.send_text(message)
            except:
                pass




async def remove_connection(lobby_code: str, websocket: WebSocket, username: str):
    async with locks[lobby_code]:
        if websocket in lobbies[lobby_code]:
            lobbies[lobby_code].remove(websocket)
        if not lobbies[lobby_code]:
            del lobbies[lobby_code]
            del locks[lobby_code]
    await broadcast(lobby_code, f"🔴 {username} left.")

async def shutdown_all_connections():
    print("\nShutting down all WebSocket connections...")
    for lobby_code in list(lobbies.keys()):
        async with locks[lobby_code]:
            for ws in lobbies[lobby_code]:
                try:
                    await ws.send_text("⚠️ Server is shutting down.")
                    await ws.close()
                except:
                    pass
            lobbies[lobby_code].clear()
        del lobbies[lobby_code]
        del locks[lobby_code]
    print("All connections closed.")

def wait_for_shutdown():
    global shutdown_flag
    print("Press 'q' then Enter to stop the server...")
    while True:
        cmd = input()
        if cmd.strip().lower() == "q":
            shutdown_flag = True
            break

# Start the shutdown watcher thread
threading.Thread(target=wait_for_shutdown, daemon=True).start()

# Custom event loop to inject shutdown
import uvicorn

if __name__ == "__main__":
    config = uvicorn.Config(app=app, host="127.0.0.1", port=8000, log_level="info")
    server = uvicorn.Server(config)

    async def run_with_shutdown():
        global shutdown_flag
        task = asyncio.create_task(server.serve())
        while not shutdown_flag:
            await asyncio.sleep(0.5)
        await shutdown_all_connections()
        task.cancel()
        print("Server shutdown complete.")
        sys.exit()

    asyncio.run(run_with_shutdown())
