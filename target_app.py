import asyncio  # Asynchronous event handling
import websockets  # WebSocket communication
import json  # JSON encoding/decoding
import uuid  # Unique ID generation
import ssl  # TLS encryption
from pathlib import Path  # File path handling

# ------------------------------------------------------------
# PART 1 — Device Identity
# ------------------------------------------------------------

TARGET_DEVICE_ID = "TARGET-" + str(uuid.uuid4())[:8]  # Generate unique target ID
TARGET_PORT = 8000

print(f"Target Device ID: {TARGET_DEVICE_ID}")
print("-" * 40)

# ------------------------------------------------------------
# PART 2 — Lightweight JSON Storage Setup
# ------------------------------------------------------------

STORAGE_DIR = Path(".")
SETTINGS_FILE = STORAGE_DIR / "settings.json"
LOGS_FILE = STORAGE_DIR / "logs.json"
METADATA_FILE = STORAGE_DIR / "last_scan_metadata.json"


def save_json(filepath, data):
    """Save Python dict/list into a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_json(filepath):
    """Load data from a JSON file, return None if missing."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None


def setup_storage():
    """Ensure settings, logs, and metadata JSON files exist."""
    if not SETTINGS_FILE.exists():
        save_json(SETTINGS_FILE, {"target_id": TARGET_DEVICE_ID, "port": TARGET_PORT})
    if not LOGS_FILE.exists():
        save_json(LOGS_FILE, [])
    if not METADATA_FILE.exists():
        save_json(METADATA_FILE, {"last_scan_time": None, "agent_source": None})


def log_event(event_type, details):
    """Append an event to logs.json, keep last 100 events."""
    logs = load_json(LOGS_FILE) or []
    logs.append({"event": event_type, "details": details})
    save_json(LOGS_FILE, logs[-100:])

# ------------------------------------------------------------
# PART 3 — JSON Validation (Simple Schema)
# ------------------------------------------------------------

def validate_message(msg):
    """
    Validate incoming JSON message structure.
    Expected schema:
    {
        "type": "security_test_request" | "ping",
        "agent_id": "string"
    }
    """
    if not isinstance(msg, dict):
        return False, "Message must be a JSON object"
    if msg.get("type") not in ["security_test_request", "ping"]:
        return False, "Invalid or missing 'type' field"
    if msg.get("type") == "security_test_request" and "agent_id" not in msg:
        return False, "Missing 'agent_id' in security_test_request"
    return True, "Valid message"

# ------------------------------------------------------------
# PART 4 — WebSocket Request Handler
# ------------------------------------------------------------

async def handle_target_request(websocket):
    print(f"Connection received from: {websocket.remote_address}")
    log_event("CONNECTION_RECEIVED", {"remote": str(websocket.remote_address)})

    # Send registration info when connection opens
    await websocket.send(json.dumps({
        "type": "target_register",
        "target_id": TARGET_DEVICE_ID
    }))

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                await websocket.send(json.dumps({"error": "Invalid JSON"}))
                continue

            # Validate message
            is_valid, error_msg = validate_message(data)
            if not is_valid:
                await websocket.send(json.dumps({"error": error_msg}))
                log_event("INVALID_MESSAGE", {"reason": error_msg})
                continue

            # --------------------------
            # HEARTBEAT handler
            # --------------------------
            if data["type"] == "ping":
                await websocket.send(json.dumps({
                    "type": "pong",
                    "target_id": TARGET_DEVICE_ID
                }))
                continue

            # --------------------------
            # SECURITY TEST REQUEST FLOW
            # --------------------------
            if data["type"] == "security_test_request":
                agent_id = data["agent_id"]
                print(f"Security Test Requested by agent: {agent_id}")

                # Simulated user consent system
                user_consent = "ACCEPTED"

                # Update metadata
                save_json(METADATA_FILE, {
                    "last_scan_time": asyncio.get_event_loop().time(),
                    "agent_source": agent_id
                })

                log_event("CONSENT_RESPONSE", {"agent_id": agent_id, "consent": user_consent})

                # Send response
                await websocket.send(json.dumps({
                    "type": "consent_response",
                    "target_id": TARGET_DEVICE_ID,
                    "agent_id": agent_id,
                    "consent": user_consent
                }))

    finally:
        print("Connection closed")
        log_event("CONNECTION_CLOSED", {})

# ------------------------------------------------------------
# PART 5 — TLS SETUP + SERVER RUN
# ------------------------------------------------------------

async def main():
    setup_storage()  # Prepare JSON files

    # Create TLS context
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain("cert.pem", "key.pem")  # TLS certs

    print("⚠ TLS enabled — but certificates must be added manually")
    print(f"Starting secure WebSocket server on port {TARGET_PORT}...")
    print("-" * 40)

    async with websockets.serve(
        handle_target_request,
        "0.0.0.0",
        TARGET_PORT,
        ssl=ssl_context
    ):
        await asyncio.Future()  # Keeps server running forever

if __name__ == "__main__":
    asyncio.run(main())
