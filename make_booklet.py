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

실행:  .venv-pamphlet/bin/python make_booklet.py [입력디렉토리]
       입력디렉토리 생략 시 data/ 사용.
출력:  <입력디렉토리>/Pamphlet_booklet_A3.pdf
"""

import argparse
import io
from pathlib import Path

from PIL import Image, ImageCms
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

Image.MAX_IMAGE_PIXELS = None  # 대형 스캔본 허용

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

# 한 쪽은 인쇄 시 A4(210 x 297 mm)로 출력된다. 원본 A2 스캔본을 그대로 박으면
# 파일이 수십 MB가 되므로, A4 출력 해상도(DPI)에 맞춰 다운샘플 후 JPEG로 압축한다.
# 300 DPI면 인쇄 화질에 충분하고 화질 열화가 사실상 보이지 않는다.
OUTPUT_DPI = 300
JPEG_QUALITY = 85
CELL_PX_W = round(HALF_W / 72 * OUTPUT_DPI)   # A4 폭(pt)→인치→px
CELL_PX_H = round(PAGE_H / 72 * OUTPUT_DPI)   # A4 높이(pt)→인치→px


_SRGB = ImageCms.createProfile("sRGB")


def load(data: Path, page_num: int) -> ImageReader:
    im = Image.open(data / PAGE_FILE[page_num])
    if im.mode != "RGB":
        icc = im.info.get("icc_profile")
        if icc:
            # 박혀 있는 CMYK 프로파일(U.S. Web Coated SWOP v2 등)을 적용해 sRGB로 변환.
            # 단순 im.convert("RGB")는 프로파일을 무시해 채도 높은 빨강/핑크 색이 틀어진다.
            src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
            im = ImageCms.profileToProfile(im, src, _SRGB, outputMode="RGB")
        else:
            im = im.convert("RGB")

    # A4 칸 해상도보다 크면 축소(이미 작으면 그대로 둬 화질 손실을 막는다).
    if im.width > CELL_PX_W or im.height > CELL_PX_H:
        im.thumbnail((CELL_PX_W, CELL_PX_H), Image.LANCZOS)

    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    buf.seek(0)
    return ImageReader(buf)


def main() -> None:
    ap = argparse.ArgumentParser(description="중철 임포지션 PDF 생성")
    ap.add_argument(
        "data_dir", nargs="?", default="data", type=Path,
        help="Pamphlet_PageNN.tif 가 있는 입력 디렉토리 (기본: data)",
    )
    args = ap.parse_args()
    data = args.data_dir
    out = data / "Pamphlet_booklet_A3.pdf"

    c = canvas.Canvas(str(out), pagesize=(PAGE_W, PAGE_H))
    for left, right in SHEETS:
        # 좌측 칸
        c.drawImage(load(data, left), 0, 0, width=HALF_W, height=PAGE_H)
        # 우측 칸
        c.drawImage(load(data, right), HALF_W, 0, width=HALF_W, height=PAGE_H)
        c.showPage()
    c.save()
    print(f"완료: {out}  ({len(SHEETS)} A3 pages)")


if __name__ == "__main__":
    main()
