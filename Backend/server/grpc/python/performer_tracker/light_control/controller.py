"""
Author: Jack Beaumont
Date: 06/06/2024

This module contains classes and methods for controlling lighting systems
using the Art-Net protocol.
"""

from pyartnet import ArtNetNode
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class LightController:
    """
    A controller for managing lighting channels via the Art-Net protocol.
    """

    def __init__(self, node_ip: str, port: int, universe_id: int):
        """
        Initialize the LightController with the given node IP, port, and
        universe ID.

        Parameters:
        node_ip (str): The IP address of the Art-Net node
        port (int): The port number to use for the Art-Net node
        universe_id (int): The ID of the universe to control
        """
        self.node = ArtNetNode(node_ip, port=port)
        self.universe = self.node.add_universe(universe_id)
        self.channels = {}
        logger.info(
            f"LightController initialized with IP: {node_ip}, Port: {port}, "
            f"Universe: {universe_id}"
        )

    def add_channel(self, name: str, start: int, width: int = 1):
        """
        Add a channel to the universe.

        Parameters:
        name (str): The name of the channel
        start (int): The start address of the channel
        width (int): The width of the channel (default is 1)
        """
        self.channels[name] = self.universe.add_channel(
            start=start, width=width
        )
        logger.info(
            f"Added channel {name} starting at {start} with width {width}"
        )

    def set_channel_values(self, name: str, values: list):
        """
        Set the values for a given channel.

        Parameters:
        name (str): The name of the channel
        values (list): The values to set for the channel
        """
        if name in self.channels:
            self.channels[name].set_values(values)
            logger.debug(f"Set values for channel {name}: {values}")
        else:
            logger.warning(f"Channel {name} not found. Unable to set values.")
