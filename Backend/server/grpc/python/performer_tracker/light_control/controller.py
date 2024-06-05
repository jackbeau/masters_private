from pyartnet import ArtNetNode
import logging

logger = logging.getLogger(__name__)


class LightController:
    def __init__(self, node_ip, port, universe_id):
        self.node = ArtNetNode(node_ip, port=port)
        self.universe = self.node.add_universe(universe_id)
        self.channels = {}
        logger.info(f"LightController initialized with IP: {node_ip}, Port: {port}, Universe: {universe_id}")

    def add_channel(self, name, start, width=1):
        self.channels[name] = self.universe.add_channel(start=start, width=width)
        logger.info(f"Added channel {name} starting at {start} with width {width}")

    def set_channel_values(self, name, values):
        if name in self.channels:
            self.channels[name].set_values(values)
            logger.debug(f"Set values for channel {name}: {values}")
