#!/usr/bin/env bash
# =====================================================================
# 流萤博客 一键启动脚本（Linux / macOS / git-bash）
#
# 虚拟环境约定：.venv/（已存在则直接复用）
# 第一次跑：自动创建 .venv、装 Python / npm 依赖、跑 migrate
# 之后再跑：直接前台并行启动 Django 8000 + Vite 5173
# Ctrl+C 或 ./stop.sh 同时停止两个进程
# =====================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

command -v npm >/dev/null 2>&1 || {
    echo "[error] 未找到 npm，请先安装 Node.js"
    exit 1
}

# Windows 上 git-bash 的 venv 路径不一样
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    VENV_BIN=".venv/Scripts"
    PY_BOOT="python"
else
    VENV_BIN=".venv/bin"
    PY_BOOT="python3"
fi

command -v "$PY_BOOT" >/dev/null 2>&1 || {
    echo "[error] 未找到 $PY_BOOT，请先安装 Python"
    exit 1
}

# -------- 1. 后端虚拟环境 .venv/ -------------------------------------
REQ_STAMP=".venv/.requirements-installed"
if [[ ! -f "$VENV_BIN/activate" ]]; then
    echo "[setup] 创建 Python 虚拟环境 .venv/"
    "$PY_BOOT" -m venv .venv
    # shellcheck disable=SC1090
    source "$VENV_BIN/activate"
    echo "[setup] 安装 Python 依赖"
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    touch "$REQ_STAMP"
else
    # shellcheck disable=SC1090
    source "$VENV_BIN/activate"
    if [[ ! -f "$REQ_STAMP" || requirements.txt -nt "$REQ_STAMP" ]] ||
        ! python -c "import django" 2>/dev/null; then
        echo "[setup] 安装更新后的 Python 依赖"
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        touch "$REQ_STAMP"
    fi
fi

# -------- 2. 数据库 migrate ------------------------------------------
echo "[setup] 检查数据库迁移"
python manage.py migrate --noinput

# -------- 3. 前端 node_modules ---------------------------------------
NODE_STAMP="frontend/node_modules/.package-lock.json"
if [[ ! -f "$NODE_STAMP" ||
      frontend/package.json -nt "$NODE_STAMP" ||
      ( -f frontend/package-lock.json && frontend/package-lock.json -nt "$NODE_STAMP" ) ]]; then
    echo "[setup] 安装更新后的前端依赖（首次会比较久）"
    (cd frontend && npm install)
fi

# -------- 4. 并行启动 ------------------------------------------------
port_in_use() {
    python - "$1" <<'PY'
import socket
import sys

with socket.socket() as sock:
    sock.settimeout(0.5)
    sys.exit(0 if sock.connect_ex(("127.0.0.1", int(sys.argv[1]))) == 0 else 1)
PY
}

if port_in_use 8000; then
    echo "[error] 端口 8000 已被占用，请先运行 ./stop.sh 或关闭占用程序"
    exit 1
fi
if port_in_use 5173; then
    echo "[error] 端口 5173 已被占用，请先运行 ./stop.sh 或关闭占用程序"
    exit 1
fi

echo ""
echo "============================================================"
echo "  后端: http://127.0.0.1:8000"
echo "  前端: http://localhost:5173  （开发请访问这个）"
echo "  停止: Ctrl+C 或另开终端运行 ./stop.sh"
echo "============================================================"
echo ""

RUN_DIR="$ROOT/.run"
mkdir -p "$RUN_DIR"
rm -f "$RUN_DIR/backend.pid" "$RUN_DIR/frontend.pid"

cleanup() {
    echo ""
    echo "[stop] 收到中断信号，关闭子进程..."
    trap - INT TERM
    bash "$ROOT/stop.sh" || {
        [[ -n "${BACKEND_PID:-}" ]] && kill "$BACKEND_PID" 2>/dev/null || true
        [[ -n "${FRONTEND_PID:-}" ]] && kill "$FRONTEND_PID" 2>/dev/null || true
    }
    wait 2>/dev/null || true
    rm -f "$RUN_DIR/backend.pid" "$RUN_DIR/frontend.pid"
    exit 0
}
trap cleanup INT TERM

python manage.py runserver 127.0.0.1:8000 &
BACKEND_PID=$!
printf '%s\n' "$BACKEND_PID" > "$RUN_DIR/backend.pid"

(cd frontend && exec npm run dev -- --host 127.0.0.1 --strictPort) &
FRONTEND_PID=$!
printf '%s\n' "$FRONTEND_PID" > "$RUN_DIR/frontend.pid"

set +e
wait "$BACKEND_PID" "$FRONTEND_PID"
STATUS=$?
set -e
rm -f "$RUN_DIR/backend.pid" "$RUN_DIR/frontend.pid"
exit "$STATUS"
