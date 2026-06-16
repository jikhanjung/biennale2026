#!/usr/bin/env bash
# 2026 미학비엔날레 정적 사이트 배포 스크립트.
# 소스(index*.html + data/)를 nginx가 서빙하는 /srv/2026biennale 로 동기화한다.
#   접속(정규): https://biennale.app/        (nginx: sites-available/biennale.app, 루트 서빙 + HSTS)
#   접속(레거시): http://<서버IP>/2026biennale/  (nginx: sites-available/2026biennale, 동일 디렉토리)
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="/srv/2026biennale"

# 최초 1회: 대상 디렉토리가 없으면 기존 /srv/* 와 동일한 권한으로 생성
if [ ! -d "$DEST" ]; then
  echo "==> $DEST 생성 (honestjung:devops, 2775)"
  sudo install -d -o honestjung -g devops -m 2775 "$DEST"
fi

echo "==> $SRC -> $DEST 동기화"
rsync -a --delete --delete-excluded \
  --exclude='*_old*.png' \
  "$SRC/index.html" \
  "$SRC/index_list.html" \
  "$SRC/index1.html" \
  "$SRC/index2.html" \
  "$SRC/index3.html" \
  "$SRC/index4.html" \
  "$SRC/data" \
  "$DEST/"

echo "==> 완료. https://biennale.app/ 에서 확인하세요. (레거시: http://<서버IP>/2026biennale/)"
