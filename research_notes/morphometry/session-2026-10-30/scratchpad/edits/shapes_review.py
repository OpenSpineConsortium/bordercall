"""The shapes review's fixes to morphoview/shapes.py, each an exact replacement."""
import sys

path = sys.argv[1]
text = open(path, encoding="ascii").read()
EDITS = [
    ("""segment of the world is a straight segment of the render, its ends projected, so a polyline
projects exactly, and a smooth curve within its tolerance times the magnification. A segment that
runs behind the source is cut where it reaches the source's plane, since no ray of the render
passes behind the source, and what is left of the curve is kept as the pieces it falls into.
""",
     """segment of the world is a straight segment of the render, its ends projected, so a polyline
projects exactly, and a smooth curve within its tolerance as the render enlarges it: under a cone
beam by the magnification, sdd over the depth, and off the beam's axis by up to one over the cosine
of the ray's angle to the axis besides, for a slip along the ray's tilt; under parallel rays not at
all. A segment that runs behind the source is cut where it reaches the source's plane, since no ray
of the render passes behind the source, and what is left of the curve is kept as the pieces it
falls into. Shapes hold arrays, so each is equal only to itself.
"""),
    ("""(the smallest singular vector of the centred points, with its root mean square residual); its
patch is a flat polygon, a rectangle about the point unless corners are given, and a flat polygon
projects as a closed curve.""",
     """(the smallest singular vector of the centred points, with its root mean square residual); its
patch is the rectangle of the half sides asked for about the point, and a flat polygon, a patch or
one built from its corners, projects as a closed curve."""),
    ("""step), so where the volume's path_length is above zero FleXray's channel for its label is too on
a render of attenuating voxels, FleXray's channel being the attenuation summed over the same
points (fxr/drr/rendering.py, render_drr's rendered).
""",
     """step). FleXray's channel for the label is the attenuation summed over the same points, read
between voxels as grid_sample's bilinear mode reads it (fxr/drr/rendering.py, render_drr's
rendered), so on a volume of one attenuation the channel is that attenuation times the path
length at every pixel, and on a CT, whose bone borders air, the channel is above zero where the
path length is.
"""),
    ("""@dataclass(frozen=True)
class Curve2D:""", """@dataclass(frozen=True, eq=False)
class Curve2D:"""),
    ("""@dataclass(frozen=True)
class Curve:""", """@dataclass(frozen=True, eq=False)
class Curve:"""),
    ("""@dataclass(frozen=True)
class Plane:""", """@dataclass(frozen=True, eq=False)
class Plane:"""),
    ("""@dataclass(frozen=True)
class Polygon:""", """@dataclass(frozen=True, eq=False)
class Polygon:"""),
    ("""@dataclass(frozen=True)
class Volume:""", """@dataclass(frozen=True, eq=False)
class Volume:"""),
    ("""    \"\"\"The circle of `radius` about `centre` in the plane of `normal`, closed.\"\"\"
    centre, n = np.asarray(centre, float), unit(normal)
""", """    \"\"\"The circle of `radius` about `centre` in the plane of `normal`, closed.\"\"\"
    if not (math.isfinite(radius) and radius > 0):
        raise ValueError("a circle's radius is above zero")
    centre, n = np.asarray(centre, float), unit(normal)
"""),
]
for old, new in EDITS:
    if text.count(old) != 1:
        sys.exit("not found once: %r" % old[:70])
    text = text.replace(old, new)
open(path, "w", encoding="ascii", newline="\n").write(text)
print("shapes.py: %d edits" % len(EDITS))
