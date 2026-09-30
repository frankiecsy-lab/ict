"""建置 Windows x86-64 執行檔（PyInstaller onedir、windowed 無 console）。

用法：python scripts\\build_exe.py [--clean]
產物：dist/ICT-Trader-win/ICT-Trader.exe + _internal/（整夾 zip 分發）
.env 唔會打包——部署時放喺 exe 旁邊（本腳本自動由 .env.example 生成一份預設）。

用獨立乾淨 venv（.venv-win）build：global Python 裝咗成百個無關套件（torch/cv2/…），
PyInstaller hook-pandas.py 會將 pandas optional deps 全部收集入產物 → 1.5GB；
乾淨 venv 只 pin 必要依賴 → ~300MB。

註：PyInstaller 內置 hook-PySide6.py 已自動收集 Qt binaries/plugins，唔需要
--collect-submodules；futu package data files（VERSION.txt / proto）要明確 --collect-data futu。
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = ROOT / "dist" / "ICT-Trader-win"
VENV = ROOT / ".venv-win"
# 同 requirements.txt pin 一致（只收必要依賴）
PINNED = [
    "PySide6==6.11.2",
    "shiboken6==6.11.2",
    "protobuf==7.34.1",
    "python-dotenv==1.2.2",
    "futu_api==10.5.6508",
    "opencc-python-reimplemented==0.1.7",
    "pandas==3.0.2",
    "pyinstaller==6.22.2",
]


def _venv_python() -> Path:
    return VENV / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build ICT Trader Windows exe")
    parser.add_argument("--clean", action="store_true", help="先清走舊產物再 build")
    args = parser.parse_args()

    py = _venv_python()
    if not py.exists():
        print(f"[build] 建立乾淨 venv {VENV} …")
        rc = subprocess.call([sys.executable, "-m", "venv", str(VENV)], cwd=ROOT)
        if rc != 0:
            return rc
        rc = subprocess.call(
            [str(py), "-m", "pip", "install", "--quiet", "--disable-pip-version-check", *PINNED],
            cwd=ROOT,
        )
        if rc != 0:
            print("venv pip install 失敗", file=sys.stderr)
            return rc

    import shutil

    if args.clean or DIST_DIR.exists():
        shutil.rmtree(DIST_DIR, ignore_errors=True)

    cmd = [
        str(py), "-m", "PyInstaller", "--noconfirm",
        "--name", "ICT-Trader",
        "--windowed",
        "--collect-data", "futu",  # futu package data files（VERSION.txt / proto 等）
        str(ROOT / "main.py"),
    ]
    print("執行：", " ".join(cmd))
    rc = subprocess.call(cmd, cwd=ROOT)
    if rc != 0:
        print(f"PyInstaller 失敗（exit {rc}）", file=sys.stderr)
        return rc

    # PyInstaller 產物喺 dist/ICT-Trader/ → rename 做平台標識名
    built = ROOT / "dist" / "ICT-Trader"
    if not (built / "ICT-Trader.exe").exists():
        print("錯誤：未搵到產物 ICT-Trader.exe", file=sys.stderr)
        return 1
    shutil.move(str(built), str(DIST_DIR))

    # 生成預設 .env（exe frozen 模式讀 exe 旁邊）；唔覆蓋用戶已改過嘅
    env_dst = DIST_DIR / ".env"
    if not env_dst.exists():
        shutil.copy(ROOT / ".env.example", env_dst)

    n_files = sum(1 for p in DIST_DIR.rglob("*") if p.is_file())
    size_mb = sum(p.stat().st_size for p in DIST_DIR.rglob("*") if p.is_file()) / 1e6
    print(f"\n✅ 建置完成：{DIST_DIR / 'ICT-Trader.exe'}")
    print(f"   {n_files} 個檔案，共 {size_mb:.1f} MB（dist/ICT-Trader-win/ 整夾 zip 分發）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
