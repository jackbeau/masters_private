import math
import logging

logger = logging.getLogger(__name__)

class PanTiltCalculator:
    @staticmethod
    def calculate_pan_tilt(x0, y0, z0, xt, yt, zt):
        delta_x = xt - x0
        delta_y = yt - y0
        delta_z = zt - z0
        
        distance = math.sqrt(delta_x**2 + delta_y**2 + delta_z**2)
        pan = math.degrees(math.atan2(delta_y, delta_x))
        tilt = math.degrees(math.asin(delta_z / distance))
        
        logger.debug(f"Calculated pan: {pan}, tilt: {tilt}")
        return pan, tilt

    @staticmethod
    def angle_to_dmx(angle, max_angle, min_dmx=0, max_dmx=255):
        dmx_value = int((angle + max_angle / 2) / max_angle * (max_dmx - min_dmx) + min_dmx)
        logger.debug(f"Converted angle {angle} to DMX value {dmx_value}")
        return dmx_value

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
        
        logger.debug(f"Updated light position to pan: {new_pan}, tilt: {new_tilt}")
        return new_pan, new_tilt
