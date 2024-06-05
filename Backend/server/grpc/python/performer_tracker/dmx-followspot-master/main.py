import asyncio
from performer_tracker import PerformerTracker


async def main():
    tracker = PerformerTracker()
    await tracker.start_camera_stream()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Process was interrupted")
