#!/usr/bin/env bash
# 建置 Ubuntu x86-64 執行檔（PyInstaller onedir）——喺 WSL Ubuntu 內 native build。
# 用法：wsl -d Ubuntu -- bash -lc "cd /mnt/d/coding/ICT_v1 && bash scripts/build_ubuntu.sh" [--clean]
# 產物：<repo>/dist/ICT-Trader-ubuntu/ict-trader + _internal/（整夾 tar.gz 分發）
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="$REPO/dist/ICT-Trader-ubuntu"
VENV="$REPO/.venv-ubuntu"

# 1) 系統依賴（idempotent）：tzdata=zoneinfo 市場時區；libgl/libegl=Qt offscreen smoke
if ! dpkg -s tzdata libgl1 libegl1 >/dev/null 2>&1; then
    echo "[build] 安裝系統依賴 tzdata / libgl1 / libegl1 …"
    sudo apt-get update -qq
    sudo apt-get install -y -qq --no-install-recommends tzdata libgl1 libegl1 ca-certificates python3-venv
fi

# 2) venv（首次建立；已存在則重用）
if [ ! -x "$VENV/bin/python" ]; then
    echo "[build] 建立 $VENV …"
    python3 -m venv "$VENV"
fi
"$VENV/bin/pip" install --quiet --disable-pip-version-check \
    "PySide6==6.11.2" \
    "shiboken6==6.11.2" \
    "protobuf==7.34.1" \
    "python-dotenv==1.2.2" \
    "futu_api==10.5.6508" \
    "opencc-python-reimplemented==0.1.7" \
    "pandas==3.0.2" \
    "pyinstaller==6.22.2"

# 3) build（--clean 或舊產物存在 → 先清）
if [ "${1:-}" = "--clean" ] || [ -d "$DIST_DIR" ]; then
    rm -rf "$DIST_DIR"
fi
cd "$REPO"
# PyInstaller 內置 hook-PySide6.py 已自動收集 Qt binaries/plugins；futu data files（VERSION.txt / proto）要明確 collect
"$VENV/bin/pyinstaller" --noconfirm \
    --name ict-trader \
    --collect-data futu \
    main.py

# PyInstaller 產物喺 dist/ict-trader/ → rename 做平台標識名
mv "$REPO/dist/ict-trader" "$DIST_DIR"

# 4) 預設 .env（frozen 模式讀 exe 旁邊）；唔覆蓋用戶已改過嘅
if [ ! -f "$DIST_DIR/.env" ]; then
    cp "$REPO/.env.example" "$DIST_DIR/.env"
fi

n_files=$(find "$DIST_DIR" -type f | wc -l)
size_mb=$(du -sm "$DIST_DIR" | cut -f1)
echo ""
echo "✅ Ubuntu build 完成：$DIST_DIR/ict-trader（${n_files} 個檔案，共 ${size_mb} MB）"
echo "   分發：tar czf ICT-Trader-ubuntu.tar.gz -C dist ICT-Trader-ubuntu"
