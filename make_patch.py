"""
Builds the Little Busters! Converted Edition (Switch) "CG fit" exefs patch for
Atmosphere.

Usage:
    python make_patch.py <path to exefs 'main'> [output dir]

4:3 event CGs are shown whole everywhere: in the story as soon as they appear,
in the stick-scroll view, and in the CG gallery. Backgrounds, sprites, the UI
and the few CGs that are not 1280x960 keep their vanilla framing.

How it works
------------
The game renders at 1280x720 and its event CGs are 1280x960. The engine's
event-CG scroller (cEvScroll) already has a zoom-out mode: a zoom tween at
+0xd88 (type +0xdb4, value +0xdb8) holding z in [-1, 0]; its per-frame renderer
draws the CG with scale = 1 + z*(1 - screenH/imageH) around a top-centre pivot,
so z = -1 is the full 4:3 frame.

A routine in the zero padding after .text (text+0x38d2c0) decides which images
are "fitted CGs": the image ID (+0xa78) is an EVENTCG.PAK entry whose canvas is
1280x960 (bitmap at text+0x38d800: 174 full CGs plus 145 expression parts; the
engine composes a CG and its expression part into one image object, which then
carries the part's ID), the image is about 4:3, and it is taller than the
screen.

  1. fit_image(): for a fitted CG, crop (+0xc54/+0xc58) and the port's default
     crop anchor (+0xbc8/+0xbcc) = 0, and the transform at +0x1560 = scale
     screenH/imageH around (screenW/2, 0), set with the engine's own setter.
  2. The story's CG setup call (text+0x264168, after cEvScroll::SetTargetV)
     runs fit_image, so CGs appear fitted on their first frame and after every
     expression swap (a swap reloads the image, which resets its transform).
  3. cEvScroll::Start() (text+0x18ebe8): start fitted CGs with z = -1, so the
     stick-scroll view and the CG gallery open on the whole image.
  4. The two places that restore the image when the scroll view ends
     (text+0x192914 in End(), text+0x191cb8 in the scroller loop's inlined
     copy of it) re-fit it in story mode.
  5. The exit "zoom back in" animation is skipped in story mode
     (text+0x191984, +0x1919c0, +0x1919d8).

Unlike CLANNAD, the LB port adds no camera pans over CGs, so no move hooks are
needed.

Every site's original bytes are checked before anything is written.
"""
import os
import struct
import sys

try:
    import lz4.block
except ImportError:
    sys.exit("This script needs the 'lz4' package:  python -m pip install lz4")

SUPPORTED_BUILD = "DF3FAB24E1D0C6E8F5EBB006009A2B1CCAAEFF0D"  # Little Busters! v1.0.0 main
PATCH_NAME = "lb_cg_fit"

FULL = [
    (0x264168, "a2a7fc97",
     "b1a40494"),
    (0x18ebe8, "68d23691e9031f32090100f9",
     "e00313aa01fa07941f2003d5"),
    (0x192914, "b77efc97",
     "d0ea0794"),
    (0x191cb8, "ce81fc97",
     "e7ed0794"),
    (0x191984, "0820201e",
     "beee0714"),
    (0x1919c0, "0820201e",
     "afee0714"),
    (0x1919d8, "0820201e",
     "a9ee0714"),
    (0x38d2c0, None,
     "fd7bbea9fd030091f35301a9f30300aab30300b4687a4ab909a50f513f19057128030054"
     "0a0000904a0120912b7d03534b496b38290900126b25c91a4b020036e00313aa9b22f397"
     "f403002ae00313aa4002f397a807009009dd48b91f00096b2d0100548a06140b0b741e53"
     "4a010b6b4a558a5a5f4100716c0000542000805202000014e0031f2af35341a9fd7bc2a8"
     "c0035fd6fd7bbea9fd030091f30b00f9f30300aad7ffff97e0030034e00313aa2802f397"
     "a807009009dd48b90ad948b92001221e0100221e0018211e0c00261e8c5d1812ad148052"
     "8c010d2a8001271e0140201e4201221e03102c1e4208231ee303271e7f560cb97f5a0cb9"
     "7fca0bb97fce0bb909ac82526002098be1031f2ae2031f2ae3031f2ae4031f2ae5031f2a"
     "0494f497f30b40f9fd7bc2a8c0035fd6fd7bbea9fd030091f30b00f9f30300aa68d23691"
     "49008052090100f9603246f9acffff976000003400103e1e60ba0dbdf30b40f9fd7bc2a8"
     "c0035fd6fd7bbea9fd030091f30b00f9f30302aaed02f897e00313aac4ffff97f30b40f9"
     "fd7bc2a8c0035fd6fd7bbfa9fd030091e593f497686a4cb91f05007161000054603246f9"
     "b9ffff97fd7bc1a8c0035fd6696a4cb93f050071600000540820201ea12a02546d11f817"
     "000000000000000000000000000000000000000000000000000000000000000000000000"
     "000000000000000000000000000000000000000000000000000000000000000000000000"
     "000000000000000000000000000000000000000000000000000000000000000000000000"
     "000000000000000000000000000000000000000000000000000000000000000000000000"
     "000000000000000000000000000000000000000000000000000000000000000000000000"
     "000000000000000000000000000000000000000000000000000000000000000000000000"
     "000000000000000000000000000000000000000000000000000000000000000000000000"
     "000000000000000000000000000000000000000000000000000000000000000000000000"
     "000000000000000000000000000000000000000000000000000000000000000000000000"
     "000000000000000000000000000000000000000000000000000000000000000000000000"
     "000000000000000000000000000000000000000000000000000000000000000000000000"
     "000000000000000000000000000000000000000000000000000000000000000000000000"
     "000000000000000000000000000000000000000000000000000000000000000000000000"
     "000000000000000000000000000000000000000000000000000000000000000000000000"
     "000000000000000000000000000000000000000000000000000000000000000000000000"
     "000000000000000000000000000000000000000000000000000000000000000000000000"
     "000000000000000000000000000000000000000000000000000000000000000000000000"
     "000000000000000000000000000000000000000000000000000000000000000000000000"
     "000000000000000000000000000000000000000000000000000000000000000000000000"
     "000000000000000000000000000000000000000000000000000000000000000000000000"
     "000000000000000000000000000000000000000000000000000000000000000000000000"
     "000000000000000000000000000000000000000000000000000000000000000000000000"
     "000000000000000000000000000000000000000000000000000000000000000000000000"
     "000000000000000000000000000000000000000000000000000000000000000000000000"
     "000000000000000000000000ffffffffffffffffffffffffffffffffffffffffffffefff"
     "ffffffefc3ffffffffffffffffffffff1f"),
]

NSO_HEADER_SIZE = 0x100  # IPS offsets for exefs patches are relative to the NSO header


def load_nso_text(path):
    d = open(path, "rb").read()
    if d[:4] != b"NSO0":
        sys.exit(f"{path} is not an NSO file (expected the exefs 'main').")
    flags = struct.unpack_from("<I", d, 0xC)[0]
    file_off, mem_off, size = struct.unpack_from("<III", d, 0x10)
    comp_size = struct.unpack_from("<I", d, 0x60)[0]
    raw = d[file_off:file_off + comp_size]
    if flags & 1:
        raw = lz4.block.decompress(raw, uncompressed_size=size)
    # pad to the page-aligned mapping so the cave (zero padding) can be checked
    raw += bytes((-len(raw)) % 0x1000)
    return raw, mem_off, d[0x40:0x60]


def make_ips(records):
    out = bytearray(b"PATCH")
    for off, data in records:
        if off >= 1 << 24 or off == 0x454F46:
            sys.exit("offset not representable in IPS")
        out += off.to_bytes(3, "big") + len(data).to_bytes(2, "big") + data
    out += b"EOF"
    return bytes(out)


def check(text, patches):
    for addr, orig, new in patches:
        new = bytes.fromhex(new)
        cur = text[addr:addr + len(new)]
        want = bytes(len(new)) if orig is None else bytes.fromhex(orig)
        if cur == new:
            sys.exit("This 'main' already contains the patch.")
        if cur != want:
            sys.exit(f"Unexpected bytes at text+0x{addr:x}; this build is not supported.")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main_path = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(__file__))

    text, text_mem_off, build_id = load_nso_text(main_path)
    bid_hex = build_id.hex().upper()
    print(f"Build ID : {bid_hex}")
    if not bid_hex.startswith(SUPPORTED_BUILD) or text_mem_off != 0:
        sys.exit("Only Little Busters! Converted Edition v1.0.0 (build " + SUPPORTED_BUILD + ") is supported.")
    bid_name = bid_hex[:40]

    check(text, FULL)
    records = [(a + NSO_HEADER_SIZE, bytes.fromhex(n)) for a, _, n in FULL]
    ips_dir = os.path.join(out_dir, "atmosphere", "exefs_patches", PATCH_NAME)
    os.makedirs(ips_dir, exist_ok=True)
    ips_path = os.path.join(ips_dir, bid_name + ".ips")
    open(ips_path, "wb").write(make_ips(records))
    print(f"Wrote    : {ips_path}")

    pch_path = os.path.join(out_dir, f"{PATCH_NAME}.pchtxt")
    with open(pch_path, "w", newline="\n") as f:
        f.write(f"@nsobid-{bid_name}\n\n")
        f.write("# Little Busters! Converted Edition - show 4:3 event CGs whole\n")
        f.write("@flag offset_shift 0x100\n\n")
        f.write("@enabled\n")
        for a, _, n in FULL:
            f.write(f"{a:08X} {n.upper()}\n")
        f.write("@stop\n")
    print(f"Wrote    : {pch_path}")


if __name__ == "__main__":
    main()
