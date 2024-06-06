"""
Author: Jack Beaumont
Date: 06/06/2024

This module initiates a PerformerTracker, handling light control and camera
streaming concurrently.
"""

import asyncio
import logging
from performer_tracker import PerformerTracker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """
    Main coroutine to initiate and run the PerformerTracker.

    This function creates an instance of PerformerTracker and runs
    its light control loop and camera stream concurrently.

    Parameters:
    None

    Returns:
    None
    """
    tracker = PerformerTracker()
    # Use asyncio.create_task to run both tasks concurrently
    await asyncio.gather(
        tracker.light_control_loop(), tracker.start_camera_stream()
    )


if __name__ == "__main__":
    try:
        # Use asyncio.run to start the main coroutine
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Process was interrupted")
