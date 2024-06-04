import asyncio
from camera.camera_stream import start_camera_stream


async def main():
    await start_camera_stream()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Process was interrupted")
