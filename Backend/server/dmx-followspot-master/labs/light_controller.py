import asyncio
import math
from pyartnet import ArtNetNode

class LightController:
    def __init__(self, node_ip, port, universe_id):
        self.node = ArtNetNode(node_ip, port=port)
        self.universe = self.node.add_universe(universe_id)
        self.channels = {}

    def add_channel(self, name, start, width=1):
        self.channels[name] = self.universe.add_channel(start=start, width=width)

    def set_channel_values(self, name, values):
        if name in self.channels:
            self.channels[name].set_values(values)

class PanTiltCalculator:
    @staticmethod
    def calculate_pan_tilt(x0, y0, z0, xt, yt, zt):
        delta_x = xt - x0
        delta_y = yt - y0
        delta_z = zt - z0
        
        distance = math.sqrt(delta_x**2 + delta_y**2 + delta_z**2)
        pan = math.degrees(math.atan2(delta_y, delta_x))
        tilt = math.degrees(math.asin(delta_z / distance))
        
        return pan, tilt

    @staticmethod
    def angle_to_dmx(angle, max_angle, min_dmx=0, max_dmx=255):
        return int((angle + max_angle / 2) / max_angle * (max_dmx - min_dmx) + min_dmx)

    @staticmethod
    def pan_angle_to_dmx(pan_angle, max_pan):
        return PanTiltCalculator.angle_to_dmx(pan_angle, max_pan)

    @staticmethod
    def tilt_angle_to_dmx(tilt_angle, max_tilt):
        return PanTiltCalculator.angle_to_dmx(tilt_angle + 90, max_tilt)

class LightPositionUpdater:
    @staticmethod
    def update_light_position(current_pan, current_tilt, target_pan, target_tilt, k_p):
        pan_difference = target_pan - current_pan
        tilt_difference = target_tilt - current_tilt
        
        pan_adjustment = k_p * pan_difference
        tilt_adjustment = k_p * tilt_difference
        
        new_pan = current_pan + pan_adjustment
        new_tilt = current_tilt + tilt_adjustment
        
        return new_pan, new_tilt

async def update_channels(light_controller, x0, y0, z0, xt, yt, zt, max_pan, max_tilt, k_p):
    current_pan, current_tilt = 0, 0
    target_pan, target_tilt = PanTiltCalculator.calculate_pan_tilt(x0, y0, z0, xt, yt, zt)

    try:
        while True:
            new_pan, new_tilt = LightPositionUpdater.update_light_position(current_pan, current_tilt, target_pan, target_tilt, k_p)
            
            pan_dmx = PanTiltCalculator.pan_angle_to_dmx(new_pan, max_pan)
            tilt_dmx = PanTiltCalculator.tilt_angle_to_dmx(new_tilt, max_tilt)
            
            light_controller.set_channel_values('pan', [pan_dmx])
            light_controller.set_channel_values('tilt', [tilt_dmx])
            light_controller.set_channel_values('shutter', [254])
            light_controller.set_channel_values('dimmer', [255])
            
            current_pan, current_tilt = new_pan, new_tilt
            await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        print("Update channels task was cancelled")

async def main():
    light_controller = LightController('localhost', port=6454, universe_id=0)
    light_controller.add_channel('pan', start=1)
    light_controller.add_channel('tilt', start=2)
    light_controller.add_channel('shutter', start=4)
    light_controller.add_channel('dimmer', start=5)

    x0, y0, z0 = 0, 0, 5
    xt, yt, zt = 1, -3, 0
    max_pan = 540
    max_tilt = 270
    k_p = 0.1

    update_task = asyncio.create_task(update_channels(light_controller, x0, y0, z0, xt, yt, zt, max_pan, max_tilt, k_p))

    try:
        await update_task
    except asyncio.CancelledError:
        update_task.cancel()
        try:
            await update_task
        except asyncio.CancelledError:
            print("Main task was cancelled")

# Run the main function in the asyncio event loop
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Process was interrupted")
