"""Which head camera the simulated duck has (2026-11-18). One place, so the 3D scene, the picture, the detectors and
the words the brain gets all agree.

  beta (default)  the retail Microduck's camera, as Pollen measured it on a beta unit (robotd-params CameraIntrinsics::beta,
                  2026-10-28): GC2093, mounted upright -> a LANDSCAPE picture, about 85° wide and 55° tall.
  prototype       the older look (the prototype's IMX219 mounted a quarter turn off): a PORTRAIT picture about 45° wide
                  and 73° tall - what the simulator showed until 2026-11-18.

Choose with the environment variable ANKA_CAMERA=prototype (the launchers pass it on to every program they start)."""
import math
import os

MODEL = "prototype" if os.environ.get("ANKA_CAMERA", "beta").strip().lower() == "prototype" else "beta"

RENDER_W, RENDER_H = 640, 360          # what Pollen's body server renders (a 16:9 frame), before any turning
if MODEL == "beta":
    FOVY_RENDER = 55.0                 # MuJoCo's fovy = the rendered frame's vertical angle
    TURN = "none"                      # the frame comes out the right way up
    FOV_V = FOVY_RENDER
    FOV_H = math.degrees(2 * math.atan(RENDER_W / RENDER_H * math.tan(math.radians(FOVY_RENDER / 2))))   # ≈ 85.6
    # the model's head camera, turned so that (after the body server's own 180° turn) the picture is upright
    MODEL_CAMERA_QUAT = "0 0.707107 -0.707107 0"
else:
    FOVY_RENDER = 45.0                 # the model's default
    TURN = "cw"                        # the frame comes out on its side: a clockwise turn puts it upright
    FOV_H = FOVY_RENDER
    FOV_V = math.degrees(2 * math.atan(RENDER_W / RENDER_H * math.tan(math.radians(FOVY_RENDER / 2))))   # ≈ 72.7
    MODEL_CAMERA_QUAT = None           # the model as Pollen made it

PICTURE_W, PICTURE_H = (RENDER_W, RENDER_H) if TURN == "none" else (RENDER_H, RENDER_W)
CAM_H = 0.20                           # his eyes are about 20 cm above the floor


def floor_distance(fraction_up):
    """With the head level: how far away a floor spot is that lies this far up from the picture's bottom (0 = bottom)."""
    below = math.atan((0.5 - fraction_up) * 2 * math.tan(math.radians(FOV_V / 2)))
    return CAM_H / math.tan(below) if below > 0 else float("inf")


def side_angle(fraction_in):
    """Degrees from straight ahead of something this far in from the picture's left/right edge (0 = the edge)."""
    return math.degrees(math.atan((0.5 - fraction_in) * 2 * math.tan(math.radians(FOV_H / 2))))
