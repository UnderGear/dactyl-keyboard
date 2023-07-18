from shapes import controllers
from shapes import plates
from shapes import trackball
import json

# from .trackball_in_wall import *


controller_list = dict(
    pcb_mount=controllers.PCBMountController,
    original=controllers.OriginalController,
    external=controllers.ExternalController,
)

plate_list = dict(
    notch=plates.NotchPlate,
    undercut=plates.UndercutPlate,
    hole=plates.HolePlate,
    nub=plates.NubPlate,
)

trackball_list = dict(
    none=None,
    trackball=trackball.Trackball,
)


class Controllers:
    def __init__(self, name, *args, **kwargs):
        pass
