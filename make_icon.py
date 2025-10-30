import os
import sys
from PIL import Image


def main():
    src = 'check.png'
    dst = 'check.ico'
    if len(sys.argv) >= 2:
        src = sys.argv[1]
    if len(sys.argv) >= 3:
        dst = sys.argv[2]

    img = Image.open(src).convert('RGBA')
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    img.save(dst, format='ICO', sizes=sizes)
    print(f"Saved {dst}")


if __name__ == '__main__':
    main()
