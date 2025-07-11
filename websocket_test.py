import asyncio
import websockets

async def test_connection():
    try:
        async with websockets.connect('ws://192.168.1.210:8333/mcp') as ws:
            print("WebSocket connection established successfully!")
            await ws.send("ping")
            response = await ws.recv()
            print(f"Received response: {response}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
