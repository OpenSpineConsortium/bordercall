"""speck6.py with the clamp's set-aside switched off (body.WALL_ACROSS_MAX = 0), for the count of
specks that stop a label parting without it."""
import speck6
from morphometry import body as BODY

BODY.WALL_ACROSS_MAX = 0
speck6.main()
