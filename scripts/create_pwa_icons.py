"""Generate portable course icons using only Python's standard library."""
from pathlib import Path
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1]


def chunk(kind, data):
    checksum = zlib.crc32(kind + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", checksum)


def icon(size):
    rows = bytearray()
    for y in range(size):
        rows.append(0)  # PNG filter: none.
        for x in range(size):
            px, py = x / size, y / size
            color = (23, 36, 58)
            # A folder and a check mark, with generous maskable-icon padding.
            if 0.20 <= px <= 0.80 and 0.34 <= py <= 0.72:
                color = (219, 234, 254)
            if 0.20 <= px <= 0.45 and 0.27 <= py <= 0.35:
                color = (219, 234, 254)
            if 0.37 <= px <= 0.51 and abs(py - (px + 0.13)) < 0.035:
                color = (20, 100, 170)
            if 0.49 <= px <= 0.68 and abs(py - (-px + 1.13)) < 0.035:
                color = (20, 100, 170)
            rows.extend(color)
    header = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(bytes(rows))) + chunk(b"IEND", b"")


def main():
    public = ROOT / "public"
    public.mkdir(exist_ok=True)
    for size in (192, 512):
        path = public / f"pwa-icon-{size}.png"
        path.write_bytes(icon(size))
        print(f"Created {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
