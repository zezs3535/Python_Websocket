import random
import asyncio
import websockets

from time import sleep

async def SendMsg(websocket, path):
    for x in range(0, 10):
        rand_number = random.randint(1,1000)
        sleep(0.5)
        await websocket.send(str(rand_number))
    await websocket.send(str("Done!"))

async def main(websocket, path):
    name = await websocket.recv()
    print(f" {name}")

    Send_ = asyncio.ensure_future(SendMsg(websocket, path))
    print("Main Asyncio Start")
    asyncio.as_completed(Send_)

start_server = websockets.serve(main, "220.125.134.80", 8785)
loop = asyncio.get_event_loop()
loop.run_until_complete(start_server)
loop.run_forever()
