#!/usr/bin/env bash
# 停止由 start.sh 启动的 Django 和 Vite 进程。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_DIR="$ROOT/.run"
declare -a ROOT_PIDS=()
declare -a STOP_PIDS=()

is_liuying_process() {
    local process_id="$1"
    local command_line
    command_line="$(ps -p "$process_id" -o command= 2>/dev/null || true)"
    [[ "$command_line" =~ manage\.py[[:space:]]+runserver ||
       "$command_line" =~ npm[[:space:]]+run[[:space:]]+dev ||
       "$command_line" =~ /vite(\.js)?([[:space:]]|$) ]]
}

add_root_pid() {
    local process_id="$1"
    [[ "$process_id" =~ ^[0-9]+$ ]] || return 0
    kill -0 "$process_id" 2>/dev/null || return 0
    is_liuying_process "$process_id" || return 0
    ROOT_PIDS+=("$process_id")
}

for file in "$RUN_DIR/backend.pid" "$RUN_DIR/frontend.pid"; do
    [[ -f "$file" ]] && add_root_pid "$(head -n 1 "$file")"
done

# 兼容旧版启动脚本没有 PID 文件的情况；仅识别本项目命令，不按端口盲杀。
if command -v lsof >/dev/null 2>&1; then
    while IFS= read -r process_id; do
        [[ -n "$process_id" ]] && add_root_pid "$process_id"
    done < <(lsof -tiTCP:8000 -sTCP:LISTEN 2>/dev/null || true)
    while IFS= read -r process_id; do
        [[ -n "$process_id" ]] && add_root_pid "$process_id"
    done < <(lsof -tiTCP:5173 -sTCP:LISTEN 2>/dev/null || true)
fi

if [[ ${#ROOT_PIDS[@]} -eq 0 ]]; then
    echo "[stop] 未发现正在运行的流萤博客服务"
    rm -f "$RUN_DIR/backend.pid" "$RUN_DIR/frontend.pid"
    exit 0
fi

collect_tree() {
    local parent_id="$1"
    local child_id
    if command -v pgrep >/dev/null 2>&1; then
        while IFS= read -r child_id; do
            [[ -n "$child_id" ]] && collect_tree "$child_id"
        done < <(pgrep -P "$parent_id" 2>/dev/null || true)
    fi
    STOP_PIDS+=("$parent_id")
}

for process_id in "${ROOT_PIDS[@]}"; do
    collect_tree "$process_id"
done

echo "[stop] 正在停止后端和前端服务..."
kill -TERM "${STOP_PIDS[@]}" 2>/dev/null || true

for _ in 1 2 3 4 5; do
    alive=0
    for process_id in "${STOP_PIDS[@]}"; do
        kill -0 "$process_id" 2>/dev/null && alive=1
    done
    [[ "$alive" -eq 0 ]] && break
    sleep 1
done

for process_id in "${STOP_PIDS[@]}"; do
    if kill -0 "$process_id" 2>/dev/null; then
        kill -KILL "$process_id" 2>/dev/null || true
    fi
done

failed=0
for process_id in "${STOP_PIDS[@]}"; do
    kill -0 "$process_id" 2>/dev/null && failed=1
done

if [[ "$failed" -ne 0 ]]; then
    echo "[error] 部分进程无法停止，请检查权限后重试" >&2
    exit 1
fi

rm -f "$RUN_DIR/backend.pid" "$RUN_DIR/frontend.pid"
echo "[stop] 服务已停止"
