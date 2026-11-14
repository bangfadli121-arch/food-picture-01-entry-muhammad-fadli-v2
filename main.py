import hashlib
import os
import shutil
import sys


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as image_file:
        for chunk in iter(lambda: image_file.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fail(message):
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def main():
    source = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    destination_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    destination = os.path.join(destination_dir, "entry.png")

    try:
        source_size = os.path.getsize(source)
    except OSError as error:
        fail(f"cannot access source {source}: {error}")

    if source_size > 1048576:
        fail(f"source is larger than 1048576 bytes ({source_size} bytes)")

    try:
        os.makedirs(destination_dir, exist_ok=True)
        shutil.copyfile(source, destination)
    except OSError as error:
        fail(f"cannot copy image to {destination}: {error}")

    try:
        destination_size = os.path.getsize(destination)
        source_hash = sha256(source)
        destination_hash = sha256(destination)
    except OSError as error:
        fail(f"cannot verify image copy: {error}")

    if source_size != destination_size or source_hash != destination_hash:
        fail("copied image does not match the source")

    try:
        with open(destination, "rb") as image_file:
            image_data = image_file.read()
    except OSError as error:
        fail(f"cannot read copied image {destination}: {error}")

    if not (image_data.startswith(b"\x89PNG\r\n\x1a\n") or image_data.startswith(b"\xff\xd8\xff")):
        fail("copied image has neither a PNG signature nor a JPEG start marker")

    if image_data.startswith(b"\x89PNG\r\n\x1a\n"):
        if len(image_data) < 24 or image_data[12:16] != b"IHDR":
            fail("PNG image is missing a valid IHDR dimension header")
        width = int.from_bytes(image_data[16:20], "big")
        height = int.from_bytes(image_data[20:24], "big")
    else:
        width = height = None
        offset = 2
        sof_markers = {
            0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
            0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF,
        }
        while offset < len(image_data):
            if image_data[offset] != 0xFF:
                offset += 1
                continue
            while offset < len(image_data) and image_data[offset] == 0xFF:
                offset += 1
            if offset >= len(image_data):
                break
            marker = image_data[offset]
            offset += 1
            if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7 or marker == 0x01:
                if marker == 0xD9:
                    break
                continue
            if offset + 2 > len(image_data):
                break
            segment_length = int.from_bytes(image_data[offset:offset + 2], "big")
            if segment_length < 2 or offset + segment_length > len(image_data):
                break
            if marker in sof_markers:
                if segment_length < 7:
                    break
                height = int.from_bytes(image_data[offset + 3:offset + 5], "big")
                width = int.from_bytes(image_data[offset + 5:offset + 7], "big")
                break
            if marker == 0xDA:
                break
            offset += segment_length
        if width is None or height is None:
            fail("JPEG image is missing a valid SOF dimension marker")

    if width > 1024 or height > 1024:
        fail(f"image dimensions exceed 1024 pixels ({width}x{height})")

    print(f"Copied {destination} ({destination_size} bytes, sha256 {destination_hash})")


if __name__ == "__main__":
    main()
