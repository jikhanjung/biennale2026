#!/usr/bin/env bash
# 2026 미학비엔날레 정적 사이트 배포 스크립트.
# 소스(index*.html + data/)를 nginx가 서빙하는 /srv/biennale2026 로 동기화한다.
#   접속: http://<서버IP>/biennale2026/   (nginx: sites-available/biennale2026)
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="/srv/biennale2026"

# 최초 1회: 대상 디렉토리가 없으면 기존 /srv/* 와 동일한 권한으로 생성
if [ ! -d "$DEST" ]; then
  echo "==> $DEST 생성 (honestjung:devops, 2775)"
  sudo install -d -o honestjung -g devops -m 2775 "$DEST"
fi

echo "==> $SRC -> $DEST 동기화"
rsync -a --delete \
  "$SRC/index.html" \
  "$SRC/index1.html" \
  "$SRC/index2.html" \
  "$SRC/index3.html" \
  "$SRC/data" \
  "$DEST/"

echo "==> 완료. http://<서버IP>/biennale2026/ 에서 확인하세요."
