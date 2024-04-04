import asyncio
import websockets
import cv2  # Assuming you want to process frames using OpenCV
import numpy as np

async def handle_connection(websocket, path):
    async for message in websocket:  # Iterate through messages

        # Directly access the frame data (already a bytes object)
        frame_data = message

        # Decode frame data into a NumPy array
        frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_UNCHANGED)  # Adjust color mode as needed

        # Process or display the frame using OpenCV
        cv2.imshow('Camera Stream', frame)
        cv2.waitKey(1)  # Adjust delay for smoother display

start_server = websockets.serve(handle_connection, "0.0.0.0", 8080)  # Replace with your server IP and port
asyncio.get_event_loop().run_until_complete(start_server)
print("Server is running")
asyncio.get_event_loop().run_forever()
