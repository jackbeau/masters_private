"""
Author: Jack Beaumont
Date: 06/06/2024

This module contains classes and methods for calculating pan and tilt angles
and converting them to DMX values, as well as updating light positions based
on these values.
"""

import math
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class PanTiltCalculator:
    """
    A calculator for determining pan and tilt angles based on 3D coordinates
    and converting these angles to DMX values.
    """

    @staticmethod
    def calculate_pan_tilt(
        x0: float, y0: float, z0: float, xt: float, yt: float, zt: float
    ) -> tuple:
        """
        Calculate the pan and tilt angles required to move from the initial
        coordinates (x0, y0, z0) to the target coordinates (xt, yt, zt).

        Parameters:
        x0 (float): Initial x-coordinate
        y0 (float): Initial y-coordinate
        z0 (float): Initial z-coordinate
        xt (float): Target x-coordinate
        yt (float): Target y-coordinate
        zt (float): Target z-coordinate

        Returns:
        tuple: Pan and tilt angles in degrees
        """
        delta_x = xt - x0
        delta_y = yt - y0
        delta_z = zt - z0

        distance = math.sqrt(delta_x**2 + delta_y**2 + delta_z**2)
        pan = math.degrees(math.atan2(delta_y, delta_x))
        tilt = math.degrees(math.asin(delta_z / distance))

        logger.debug(f"Calculated pan: {pan}, tilt: {tilt}")
        return pan, tilt

    @staticmethod
    def angle_to_dmx(
        angle: float, max_angle: float, min_dmx: int = 0, max_dmx: int = 255
    ) -> int:
        """
        Convert an angle to a DMX value.

        Parameters:
        angle (float): The angle to convert
        max_angle (float): The maximum angle
        min_dmx (int): The minimum DMX value (default is 0)
        max_dmx (int): The maximum DMX value (default is 255)

        Returns:
        int: The corresponding DMX value
        """
        dmx_value = int(
            (angle + max_angle / 2) / max_angle * (max_dmx - min_dmx) + min_dmx
        )
        logger.debug(f"Converted angle {angle} to DMX value {dmx_value}")
        return dmx_value

    @staticmethod
    def pan_angle_to_dmx(pan_angle: float, max_pan: float) -> int:
        """
        Convert a pan angle to a DMX value.

        Parameters:
        pan_angle (float): The pan angle to convert
        max_pan (float): The maximum pan angle

        Returns:
        int: The corresponding DMX value for the pan angle
        """
        return PanTiltCalculator.angle_to_dmx(pan_angle, max_pan)

    @staticmethod
    def tilt_angle_to_dmx(tilt_angle: float, max_tilt: float) -> int:
        """
        Convert a tilt angle to a DMX value.

        Parameters:
        tilt_angle (float): The tilt angle to convert
        max_tilt (float): The maximum tilt angle

        Returns:
        int: The corresponding DMX value for the tilt angle
        """
        return PanTiltCalculator.angle_to_dmx(tilt_angle + 90, max_tilt)


class LightPositionUpdater:
    """
    A utility for updating light positions based on current and target
    pan and tilt angles using a proportional control approach.
    """

    @staticmethod
    def update_light_position(
        current_pan: float,
        current_tilt: float,
        target_pan: float,
        target_tilt: float,
        k_p: float,
    ) -> tuple:
        """
        Update the light's position based on current and target pan and tilt
        angles.

        Parameters:
        current_pan (float): Current pan angle
        current_tilt (float): Current tilt angle
        target_pan (float): Target pan angle
        target_tilt (float): Target tilt angle
        k_p (float): Proportional gain constant

        Returns:
        tuple: New pan and tilt angles
        """
        pan_difference = target_pan - current_pan
        tilt_difference = target_tilt - current_tilt

        pan_adjustment = k_p * pan_difference
        tilt_adjustment = k_p * tilt_difference

        new_pan = current_pan + pan_adjustment
        new_tilt = current_tilt + tilt_adjustment

        logger.debug(
            f"Updated light position to pan: {new_pan}, tilt: {new_tilt}"
        )
        return new_pan, new_tilt
