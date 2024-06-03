import os

# Paths
USER_FOLDER = 'users'
UNCERTAIN_FOLDER = 'uncertain'

# Camera settings
CAMERA_ID = 3
SAVE_INTERVAL = 30

# Homography settings
SRC_POINTS = [
    [202, 152],
    [428, 112],
    [522, 245],
    [225, 312]
]
DST_POINTS = [
    [0, 0],
    [300, 0],
    [300, 210],
    [0, 210]
]

# Light settings
LIGHT_NODE_IP = 'localhost'
LIGHT_NODE_PORT = 6454
LIGHT_UNIVERSE_ID = 0
MAX_PAN = 540
MAX_TILT = 270
KP = 0.1

# ReID model settings
REID_MODEL_NAME = 'osnet_x1_0'

# General settings
SHOW_WINDOW = True
LOGGING_LEVEL = 'DEBUG'
