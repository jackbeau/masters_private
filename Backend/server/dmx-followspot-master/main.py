import asyncio
from camera.camera_stream import start_camera_stream
from config.settings import LIGHT_NODE_IP, LIGHT_NODE_PORT, LIGHT_UNIVERSE_ID

async def main():
    await start_camera_stream()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Process was interrupted")
