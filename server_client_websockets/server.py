# server.py
import asyncio
import websockets
import json
import time

connected_clients = set()

async def send_time(websocket, path):
    connected_clients.add(websocket)
    try:
        while True:
            # Send the current time to all connected clients
            await asyncio.sleep(0.1)  # Send data desired frequency
            now = time.time()
            message = json.dumps({'time': now})
            ##### I try these implemantations but these methods send multiple message??##
            ##await asyncio.wait([client.send(message) for client in connected_clients])
            ##websockets.broadcast(connected_clients,message)
            
            await websocket.send(message)
            print("message",now)
            
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    finally:
        connected_clients.remove(websocket)

start_server = websockets.serve(send_time, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
