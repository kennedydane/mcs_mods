import socket
import struct
import time

# Server details
HOST = '172.22.0.2'
PORT = 19132

# Minecraft Bedrock Unconnected Ping packet structure
# See: https://wiki.vg/Bedrock_Protocol#Unconnected_Ping
PACKET_ID = 0x01
TIME = int(time.time() * 1000) # Time in milliseconds
MAGIC = b'\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78'
CLIENT_GUID = 98765  # A random client ID

# Pack the data using big-endian format
packet = struct.pack('>Bq16sq', PACKET_ID, TIME, MAGIC, CLIENT_GUID)

print(f"--- Minecraft UDP Connection Test ---")
print(f"Attempting to ping server at {HOST}:{PORT}...")

sock = None
try:
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5.0)  # Set a 5-second timeout

    # Send the packet
    sock.sendto(packet, (HOST, PORT))
    print("Ping packet sent.")

    # Wait for a response
    print("Waiting for response...")
    data, addr = sock.recvfrom(2048) # Buffer size for response
    
    print("\n✅ Success! Received a response from the server.")
    print(f"   Source: {addr}")
    print(f"   Response Data (hex): {data.hex()}")
    print("\nThis confirms the server is running and reachable from your machine.")
    print("The connection issue is likely specific to the Minecraft client itself.")

except socket.timeout:
    print("\n❌ Test Failed: Connection timed out.")
    print("The script sent a packet, but no response was received.")
    print("This is the classic symptom of a firewall blocking the connection.")
    print("\nPlease run the following command to allow traffic on this port:")
    print("sudo ufw allow 19132/udp")

except Exception as e:
    print(f"\nAn unexpected error occurred: {e}")

finally:
    if sock:
        sock.close()
