#!/usr/bin/env python3
"""중철(saddle-stitch) 임포지션 PDF 생성.

data/Pamphlet_Page01.tif ~ Page12.tif (A2, 세로) 12쪽을
A3 가로 6장으로 펼쳐 배치한다. A3 가로 한 장 = A4 세로 두 쪽(좌|우).

각 쪽은 인쇄 시 A4로 출력되므로, A2 원본을 A4 칸에 꽉 차게(여백 없이) 배치한다.
원본 12쪽 모두 √2 비율(A 규격)이라 칸에 정확히 맞아 왜곡이 없다.

용지 묶음 순서(좌 | 우):
    1장 바깥: 12 | 1      1장 안쪽: 2 | 11
    2장 바깥: 10 | 3      2장 안쪽: 4 | 9
    3장 바깥:  8 | 5      3장 안쪽: 6 | 7

실행:  .venv-pamphlet/bin/python make_booklet.py
출력:  data/Pamphlet_booklet_A3.pdf
"""

import io
from pathlib import Path

from PIL import Image, ImageCms
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

Image.MAX_IMAGE_PIXELS = None  # 대형 스캔본 허용

DATA = Path("data")
OUT = DATA / "Pamphlet_booklet_A3.pdf"

# 1쪽(표지)은 Pamphlet_Page01_alternative.tif 로 바꾸려면 아래 값을 교체.
PAGE_FILE = {
    1: "Pamphlet_Page01.tif",
    2: "Pamphlet_Page02.tif",
    3: "Pamphlet_Page03.tif",
    4: "Pamphlet_Page04.tif",
    5: "Pamphlet_Page05.tif",
    6: "Pamphlet_Page06.tif",
    7: "Pamphlet_Page07.tif",
    8: "Pamphlet_Page08.tif",
    9: "Pamphlet_Page09.tif",
    10: "Pamphlet_Page10.tif",
    11: "Pamphlet_Page11.tif",
    12: "Pamphlet_Page12.tif",
}

# 중철 임포지션: (좌쪽 번호, 우쪽 번호)를 묶음 순서대로.
SHEETS = [
    (12, 1),
    (2, 11),
    (10, 3),
    (4, 9),
    (8, 5),
    (6, 7),
]

PAGE_W, PAGE_H = landscape(A3)   # 420 x 297 mm (pt 단위)
HALF_W = PAGE_W / 2              # A4 한 칸의 폭


_SRGB = ImageCms.createProfile("sRGB")


def load(page_num: int) -> ImageReader:
    im = Image.open(DATA / PAGE_FILE[page_num])
    if im.mode == "RGB":
        return ImageReader(im)
    icc = im.info.get("icc_profile")
    if icc:
        # 박혀 있는 CMYK 프로파일(U.S. Web Coated SWOP v2 등)을 적용해 sRGB로 변환.
        # 단순 im.convert("RGB")는 프로파일을 무시해 채도 높은 빨강/핑크 색이 틀어진다.
        src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
        im = ImageCms.profileToProfile(im, src, _SRGB, outputMode="RGB")
    else:
        im = im.convert("RGB")
    return ImageReader(im)


def main() -> None:
    c = canvas.Canvas(str(OUT), pagesize=(PAGE_W, PAGE_H))
    for left, right in SHEETS:
        # 좌측 칸
        c.drawImage(load(left), 0, 0, width=HALF_W, height=PAGE_H)
        # 우측 칸
        c.drawImage(load(right), HALF_W, 0, width=HALF_W, height=PAGE_H)
        c.showPage()
    c.save()
    print(f"완료: {OUT}  ({len(SHEETS)} A3 pages)")


if __name__ == "__main__":
    main()
