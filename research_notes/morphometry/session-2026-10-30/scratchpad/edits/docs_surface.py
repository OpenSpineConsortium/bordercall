import sys
shapes, init = sys.argv[1], sys.argv[2]

def swap(src, old, new, count=1):
    assert src.count(old) == count, (old[:80], src.count(old))
    return src.replace(old, new)

src = open(shapes, encoding="ascii").read()
src = swap(src, '''"""Shapes beside the straight lines: curves, arcs, circles, ellipses and splines, planes and flat
polygons, and volumes, each in the world's millimetres of a mask's affine, as morphoview.lines'
ends are, and each carried onto a FleXray render by morphoview.projection's camera.''', '''"""Shapes beside the straight lines: curves, arcs, circles, ellipses and splines, planes and flat
polygons, curved surfaces, and volumes, each in the world's millimetres of a mask's affine, as
morphoview.lines' ends are, and each carried onto a FleXray render by morphoview.projection's
camera.''')
src = swap(src, '''How the render sees a plane is the angle
the ray through its point makes with it: none where the plane is seen edge on, as a line, and 90
degrees face on.
''', '''How the render sees a plane is the angle
the ray through its point makes with it: none where the plane is seen edge on, as a line, and 90
degrees face on.

A surface is triangles of the world: through a grid of points; a height above a plane over the
rectangle a patch would be, on a grid fine enough that the middle of every triangle's edge lies
within the tolerance of the surface; through points as they are, triangulated by Delaunay's rule
where they fall on the plane fitted to them; or the least-squares quadric over that plane drawn
over the same triangles, a height of degree two in the plane's two directions, which a concave
end-plate's dip below its rim is. Its rim is the curve of the edges only one triangle has, and its
sag how far it departs from its rim's plane. A flat triangle of the world is a triangle of the
render, its corners projected, so a surface projects exactly, as a polyline does, and the pixels
whose rays meet it, its shadow, are those whose centres its projected triangles cover. A surface
reaching behind the source has no one picture on a cone beam's render and is refused.
''')
open(shapes, "w", encoding="ascii").write(src)

src = open(init, encoding="ascii").read()
src = swap(src, '''X-rays FleXray renders from the same CT by morphoview.projection, FleXray's own camera, and
morphoview.shapes gives curves, planes, polygons and volumes that project through it; the research
note research_notes/morphometry/README.md says, in its section "Carrying the lines onto FleXray's
X-rays", how each is held to what FleXray renders.

    python -m morphoview project --lines lines.csv --frames frames.csv --manifest manifest.json --file images/<stem>_v00.png --labels MASK.nii.gz --scheme enhance --out DIR
"""''', '''X-rays FleXray renders from the same CT by morphoview.projection, FleXray's own camera, and
morphoview.shapes gives curves, planes, polygons, curved surfaces and volumes that project through
it; the research note research_notes/morphometry/README.md says, in its section "Carrying the
lines onto FleXray's X-rays", how each is held to what FleXray renders. A render of SchwingNet's
pipeline is named by its manifest and file, one of its realism programme by its folder, sample and
CT, with that sample's FLUX edits and the filter's verdicts on them listed where their folders are
given.

    python -m morphoview project --lines lines.csv --frames frames.csv --manifest manifest.json --file images/<stem>_v00.png --labels MASK.nii.gz --scheme enhance --out DIR
    python -m morphoview project --lines lines.csv --frames frames.csv --realism RENDER --sample <sample_id> --ct CT.nii.gz --edits EDIT --filter FILTER --labels MASK.nii.gz --scheme enhance --out DIR
"""''')
open(init, "w", encoding="ascii").write(src)
print("ok")
