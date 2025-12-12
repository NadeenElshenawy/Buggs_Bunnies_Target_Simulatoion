import asyncio
import websockets
import json
import uuid
import ssl

SERVER_URL = "wss://localhost:8000"  # Note ws:// instead of wss://

async def connect_to_server():
    
    ssl_context=ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.load_verify_locations("cert.pem")
    ssl_context.check_hostname=False
    
    async with websockets.connect(SERVER_URL,ssl=ssl_context) as websocket:

        print("Connected to server!")

        register_msg = await websocket.recv()
        print("SERVER:", register_msg)

        # Ping
        await websocket.send(json.dumps({"type": "ping"}))
        print("Sent ping")
        print("SERVER:", await websocket.recv())

        # Security test request
        payload = {
            "type": "security_test_request",
            "agent_id": "agent-" + str(uuid.uuid4())[:8]
        }
        await websocket.send(json.dumps(payload))
        print("Sent security_test_request")
        print("SERVER:", await websocket.recv())

if __name__ == "__main__":
    asyncio.run(connect_to_server())
