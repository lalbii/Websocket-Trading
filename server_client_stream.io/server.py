#importing required libraries
import socketio
import asyncio
import uvicorn
import time

sio = socketio.AsyncServer(async_mode='asgi')
app = socketio.ASGIApp(sio)

@sio.event
async def connect(sid, environ):
    print('Client connected:', sid)
    asyncio.create_task(stream_data_to_client(sid))

@sio.event
async def disconnect(sid):
    print('Client disconnected:', sid)

async def stream_data_to_client(sid):
     while True:
        # Simulating some data to stream
        data = {"data": "Streaming data...", "timestamp": time.time()}
        await sio.emit('stream', data, to=sid)
        await asyncio.sleep(0.1)  # Adjustment how freuqently data streaming...

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8765)

