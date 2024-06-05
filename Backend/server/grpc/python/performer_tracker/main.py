import asyncio
from performer_tracker import PerformerTracker


async def main():
    tracker = PerformerTracker()
    # Use asyncio.create_task to run both tasks concurrently
    await asyncio.gather(
        tracker.light_control_loop(),
        tracker.start_camera_stream()
    )

if __name__ == '__main__':
    try:
        # Use asyncio.run to start the main coroutine
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Process was interrupted")