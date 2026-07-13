#!/usr/bin/env python3
"""Parametric enclosure for the room multisensor (docs/08-presence-sensors.md).

Two printed parts, no supports needed:
  base.stl — wall-mount back box: ESP32 ledge, USB-C cutout, vents, keyhole
  lid.stl  — sensor faceplate: LD2410C radar window (1 mm thin wall),
             AM312 PIR lens hole, BH1750 light aperture, M3 screw holes

Regenerate after editing parameters:
  pip install manifold3d trimesh numpy
  python generate_enclosure.py

Orientation: X = width (right+), Y = height (up+), Z = depth (out of wall+).
Origin: interior cavity center in X/Y, Z=0 at interior floor (inside of back wall).
"""

import numpy as np
import trimesh
from manifold3d import Manifold

# ---------------------------------------------------------------- parameters
P = {
    # interior cavity
    "int_w": 92.0,          # interior width
    "int_h": 62.0,          # interior height
    "int_d": 20.0,          # interior depth of the base (lid lip adds more)
    "wall": 2.0,            # wall thickness
    "back": 2.0,            # back wall thickness
    # lid
    "face": 2.5,            # lid faceplate thickness
    "lip_h": 5.0,           # lid lip that slides into the base
    "lip_t": 1.8,           # lip wall thickness
    "clear": 0.20,          # lid-to-base clearance per side (print tolerance)
    # ESP32 DevKit 38-pin (board rests on a ledge frame, headers hang inside)
    "esp_l": 55.2,          # board length + tolerance
    "esp_w": 29.2,          # board width + tolerance
    "esp_ledge": 3.0,       # ledge width under the board edges
    "esp_ledge_h": 6.0,     # ledge height above interior floor
    "esp_cx": -14.0,        # board center X (leaves right side for USB slack)
    "esp_cy": -13.0,        # board center Y (lower half)
    # USB-C cutout in the right wall (board USB faces right)
    "usb_w": 13.0,          # cutout width (along Y)
    "usb_h": 9.0,           # cutout height (along Z, starts at ledge top)
    # LD2410C radar, mounted against lid interior, upper-left
    "rad_w": 22.6,          # module width + tolerance
    "rad_h": 16.6,          # module height + tolerance
    "rad_cx": -25.0,
    "rad_cy": 17.0,
    "rad_window": 1.0,      # thinned faceplate over the radar (24 GHz window)
    "rad_pocket_t": 1.6,    # pocket wall thickness
    "rad_pocket_h": 4.0,    # pocket wall height
    # AM312 PIR, upper-right, lens pokes through the face
    "pir_d": 12.6,          # lens hole diameter
    "pir_cx": 25.0,
    "pir_cy": 17.0,
    # BH1750 light aperture, below the PIR
    "lux_d": 6.0,
    "lux_cx": 25.0,
    "lux_cy": -2.0,
    # vents (BME280 corner, bottom-left; and right wall above USB)
    "vent_n": 6,            # slots per group
    "vent_w": 1.8,          # slot width
    "vent_l": 12.0,         # slot length (along Z)
    "vent_pitch": 4.5,
    # wall-mount keyhole in the back wall
    "key_d_big": 8.0,
    "key_d_small": 4.0,
    "key_slot": 8.0,
    "key_cy": 20.0,
    # lid screws: M3 self-tapping into corner bosses (two opposite corners)
    "boss_d": 7.0,
    "boss_hole": 2.7,
    "screw_head_d": 6.4,
    "screw_hole": 3.4,
}

EPS = 0.01  # boolean overlap fudge


def box(w, h, d, cx=0.0, cy=0.0, z0=0.0):
    """Axis-aligned box centered on (cx, cy) in XY, from z0 to z0+d."""
    return Manifold.cube([w, h, d]).translate([cx - w / 2, cy - h / 2, z0])


def cyl(d, h, cx=0.0, cy=0.0, z0=0.0):
    """Z-axis cylinder, diameter d, from z0 to z0+h."""
    return Manifold.cylinder(h, d / 2, d / 2, 64).translate([cx, cy, z0])


def boss_positions(p):
    bx = p["int_w"] / 2 - p["boss_d"] / 2 - 0.5
    by = p["int_h"] / 2 - p["boss_d"] / 2 - 0.5
    return [(-bx, -by), (bx, by)]  # two opposite corners


def build_base(p):
    W, H, D, w, b = p["int_w"], p["int_h"], p["int_d"], p["wall"], p["back"]

    shell = box(W + 2 * w, H + 2 * w, D + b, z0=-b)
    cavity = box(W, H, D + EPS, z0=0)
    base = shell - cavity

    # ESP32 ledge frame: board rests on it, pin headers hang into the opening
    fo_w, fo_h = p["esp_l"] + 2 * p["esp_ledge"], p["esp_w"] + 2 * p["esp_ledge"]
    frame = box(fo_w, fo_h, p["esp_ledge_h"], p["esp_cx"], p["esp_cy"]) - box(
        p["esp_l"] - 2 * p["esp_ledge"], p["esp_w"] - 2 * p["esp_ledge"],
        p["esp_ledge_h"] + EPS, p["esp_cx"], p["esp_cy"], -EPS / 2)
    # board pocket walls: 2 mm tall rim just outside the board footprint
    rim = box(p["esp_l"] + 2 * 1.6, p["esp_w"] + 2 * 1.6,
              p["esp_ledge_h"] + 2.0, p["esp_cx"], p["esp_cy"]) - box(
        p["esp_l"], p["esp_w"], p["esp_ledge_h"] + 2.0 + EPS,
        p["esp_cx"], p["esp_cy"], -EPS / 2)
    base = base + frame + rim

    # USB-C cutout through the right wall, floor at ledge height
    usb = box(2 * w + EPS, p["usb_w"], p["usb_h"],
              W / 2 + w / 2, p["esp_cy"], p["esp_ledge_h"])
    base = base - usb

    # vent slots: left wall (BME280 corner, low) and right wall (high)
    for i in range(p["vent_n"]):
        y = -H / 2 + 8 + i * p["vent_pitch"]
        base = base - box(2 * w + EPS, p["vent_w"], p["vent_l"],
                          -(W / 2 + w / 2), y, (D - p["vent_l"]) / 2)
        y2 = H / 2 - 8 - i * p["vent_pitch"]
        base = base - box(2 * w + EPS, p["vent_w"], p["vent_l"],
                          W / 2 + w / 2, y2, (D - p["vent_l"]) / 2)

    # keyhole wall mount in the back wall
    key = cyl(p["key_d_big"], b + EPS, 0, p["key_cy"], -b - EPS / 2) + \
        cyl(p["key_d_small"], b + EPS, 0, p["key_cy"] + p["key_slot"],
            -b - EPS / 2) + \
        box(p["key_d_small"], p["key_slot"], b + EPS,
            0, p["key_cy"] + p["key_slot"] / 2, -b - EPS / 2)
    base = base - key

    # lid screw bosses in two opposite corners
    for (bx, by) in boss_positions(p):
        base = base + (cyl(p["boss_d"], D, bx, by) -
                       cyl(p["boss_hole"], D + EPS, bx, by, -EPS / 2))
    return base


def build_lid(p):
    W, H, w = p["int_w"], p["int_h"], p["wall"]
    F, c = p["face"], p["clear"]
    z_face = p["int_d"]  # lid face sits on top of the base walls

    lid = box(W + 2 * w, H + 2 * w, F, z0=z_face)

    # lip that slides into the base cavity
    lip_o = box(W - 2 * c, H - 2 * c, p["lip_h"], z0=z_face - p["lip_h"])
    lip_i = box(W - 2 * c - 2 * p["lip_t"], H - 2 * c - 2 * p["lip_t"],
                p["lip_h"] + EPS, z0=z_face - p["lip_h"] - EPS / 2)
    lid = lid + (lip_o - lip_i)

    # radar window: thin the faceplate to rad_window over the module area
    lid = lid - box(p["rad_w"] + 4, p["rad_h"] + 4, F - p["rad_window"] + EPS,
                    p["rad_cx"], p["rad_cy"], z_face - EPS / 2)
    # radar pocket walls on the lid interior to locate the module
    pk_w, pk_h = p["rad_w"] + 2 * p["rad_pocket_t"], p["rad_h"] + 2 * p["rad_pocket_t"]
    pocket = box(pk_w, pk_h, p["rad_pocket_h"],
                 p["rad_cx"], p["rad_cy"], z_face - p["rad_pocket_h"]) - box(
        p["rad_w"], p["rad_h"], p["rad_pocket_h"] + EPS,
        p["rad_cx"], p["rad_cy"], z_face - p["rad_pocket_h"] - EPS / 2)
    lid = lid + pocket

    # PIR lens hole and light-sensor aperture
    lid = lid - cyl(p["pir_d"], F + EPS, p["pir_cx"], p["pir_cy"],
                    z_face - EPS / 2)
    lid = lid - cyl(p["lux_d"], F + EPS, p["lux_cx"], p["lux_cy"],
                    z_face - EPS / 2)

    # screw holes + countersinks aligned with the base bosses,
    # plus lip notches so the lip clears the bosses standing in the corners
    for (bx, by) in boss_positions(p):
        lid = lid - cyl(p["screw_hole"], F + p["lip_h"] + EPS, bx, by,
                        z_face - p["lip_h"] - EPS / 2)
        lid = lid - cyl(p["screw_head_d"], 1.6, bx, by,
                        z_face + F - 1.6 + EPS)
        lid = lid - cyl(p["boss_d"] + 0.7, p["lip_h"] + EPS, bx, by,
                        z_face - p["lip_h"] - EPS / 2)
    return lid


def export(m, path):
    mesh = m.to_mesh()
    tm = trimesh.Trimesh(
        vertices=np.array(mesh.vert_properties)[:, :3],
        faces=np.array(mesh.tri_verts))
    tm.fix_normals()
    assert tm.is_watertight, f"{path} is not watertight!"
    tm.export(path)
    print(f"{path}: watertight, {len(tm.faces)} tris, "
          f"size {np.round(tm.extents, 1)} mm, volume {tm.volume / 1000:.1f} cm3")


if __name__ == "__main__":
    export(build_base(P), "base.stl")
    export(build_lid(P), "lid.stl")
