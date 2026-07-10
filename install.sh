#!/usr/bin/env bash
# Hermes Micro Framework 安装脚本
#
# 用法:
#   bash install.sh                    自动检测新装/存量
#   bash install.sh --force            强制全量覆盖（新装机）
#   bash install.sh --dry              预览变更不执行
#   bash install.sh --profile <name>   安装到指定 profile（如 --profile work）
#
# ⚠ profile 安全：
#   如果你在 profile 会话中运行 install.sh，默认会装到 ~/.hermes/（全局），
#   而不是你当前 profile 的目录 ~/.hermes/profiles/<name>/。
#   Hermes 对自身所处目录感知弱，请务必用 --profile 参数指定目标。
#
# 重点文件说明:
#   SOUL.md, memories/USER.md
#   如果是已有用户（~/.hermes/ 存在），这三个文件不会被覆盖。
#   新装机用户会全部复制。
#   已有用户请手动 diff 后按需合并。

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
HERMES_DIR="${HOME}/.hermes"
IS_NEW=false
FORCE=false
DRY=false
PROFILE=""

# ── 参数 ────────────────────────────────────────────────────────────
while [ $# -gt 0 ]; do
    case "$1" in
        --force) FORCE=true ;;
        --dry)   DRY=true ;;
        --profile) PROFILE="${2:-}"; [ -n "$PROFILE" ] || { echo "--profile 需要参数"; exit 2; }; shift ;;
        --profile=*) PROFILE="${1#*=}" ;;
    esac
    shift
done

# ── Profile 检测 ────────────────────────────────────────────────────
if [ -n "$PROFILE" ]; then
    HERMES_DIR="${HOME}/.hermes/profiles/${PROFILE}"
    echo "  [profile] 目标: $HERMES_DIR"
    export HERMES_SKILL_DIR="${HERMES_DIR}/skills"
    echo "  [profile] 已设 HERMES_SKILL_DIR=$HERMES_SKILL_DIR"
elif command -v hermes &>/dev/null; then
    ACTIVE_PROFILE=$(hermes profile list 2>/dev/null | grep '◆' | awk '{print $2}' | head -1)
    if [ -n "$ACTIVE_PROFILE" ] && [ "$ACTIVE_PROFILE" != "default" ]; then
        echo "=========================================="
        echo " ⚠ 检测到当前活跃 profile: $ACTIVE_PROFILE"
        echo " ⚠ 当前目标目录是 ~/.hermes/（全局），不是 $ACTIVE_PROFILE 的目录"
        echo " ⚠ 如果要安装到 $ACTIVE_PROFILE，请用:"
        echo "    bash install.sh --profile $ACTIVE_PROFILE"
        echo "=========================================="
        echo ""
    fi
fi

if [ ! -d "$HERMES_DIR" ]; then
    IS_NEW=true
fi

echo "=========================================="
echo " Hermes Micro Framework — 安装脚本"
echo "=========================================="
echo ""
echo "  源目录: $REPO_DIR"
echo "  目标目录: $HERMES_DIR"
if $IS_NEW; then
    echo "  类型: 全新安装"
elif $FORCE; then
    echo "  类型: 强制覆盖"
else
    echo "  类型: 存量更新（保留核心配置）"
fi
echo ""

# ── 函数: 复制 ───────────────────────────────────────────────────────
do_cp() {
    local src="$1" dst="$2" label="$3"
    if $DRY; then
        echo "  [DRY] cp -r $src $dst  ← $label"
        return
    fi
    mkdir -p "$(dirname "$dst")"
    cp -r "$src" "$dst"
    echo "  ✓ $label"
}

# ── 1. 核心配置（按新装/存量决定）─────────────────────────────────
echo "── 第 1 步: 核心配置 ―――――――――――――――――――――――――――――――――――"

if $IS_NEW || $FORCE; then
    do_cp "$REPO_DIR/SOUL.md"            "$HERMES_DIR/SOUL.md"                      "SOUL.md"
    do_cp "$REPO_DIR/memories/USER.md"   "$HERMES_DIR/memories/USER.md"             "memories/USER.md"
else
    echo "  ⚠ 检测到已有 ~/.hermes/ 目录（存量用户）"
    echo "  ⚠ SOUL.md / memories/USER.md 不会被自动覆盖"
    echo "  ⚠ 请手动对比后按需合并:"
    echo "     diff -u ~/.hermes/SOUL.md  $REPO_DIR/SOUL.md"
    echo "     diff -u ~/.hermes/memories/USER.md $REPO_DIR/memories/USER.md"
    echo ""
fi

# ── 2. .env 模板 ────────────────────────────────────────────────────
echo "── 第 2 步: .env 配置 ―――――――――――――――――――――――――――――――――――"
if [ ! -f "$HERMES_DIR/.env" ]; then
    do_cp "$REPO_DIR/.env.example" "$HERMES_DIR/.env" ".env（模板）"
    echo "   请编辑 $HERMES_DIR/.env，填入你的 SILICONFLOW_API_KEY"
else
    echo "  ✓ .env 已存在，跳过（需要新字段请手动合并）"
fi
echo ""

# ── 3. 技能目录 ─────────────────────────────────────────────────────
echo "── 第 3 步: 技能目录 ―――――――――――――――――――――――――――――――――――"
if [ -d "$REPO_DIR/skills" ]; then
    count_before=$(find "$HERMES_DIR/skills" -name "SKILL.md" 2>/dev/null | wc -l)
    if $IS_NEW || $FORCE; then
        do_cp "$REPO_DIR/skills/" "$HERMES_DIR/skills/" "skills/（全量）"
    else
        # 遍历分类子目录（core/workflow/methodology/infrastructure/integration）
        for cat_dir in "$REPO_DIR/skills"/*/; do
            cat_name=$(basename "$cat_dir")
            # 跳过 templates（作为单文件处理）
            [ "$cat_name" = "templates" ] && continue
            for skill_dir in "$cat_dir"*/; do
                [ -d "$skill_dir" ] || continue
                name=$(basename "$skill_dir")
                target="$HERMES_DIR/skills/$name"
                if [ ! -d "$target" ]; then
                    do_cp "$skill_dir" "$target" "skills/$name（${cat_name}，新增）"
                else
                    echo "  - skills/$name 已存在，跳过"
                fi
            done
        done
        # 处理 templates/ 下的单文件
        for f in "$REPO_DIR/skills/templates"/*.md; do
            [ -f "$f" ] || continue
            name=$(basename "$f")
            target="$HERMES_DIR/skills/$name"
            if [ ! -f "$target" ]; then
                do_cp "$f" "$target" "skills/$name（新增）"
            else
                echo "  - skills/$name 已存在，跳过"
            fi
        done
    fi
    count_after=$(find "$HERMES_DIR/skills" -name "SKILL.md" 2>/dev/null | wc -l)
    echo "  技能总数: $count_before → $count_after"
fi
echo ""

# ── 4. vdb 工具链 ──────────────────────────────────────────────────
echo "── 第 4 步: vdb 工具链 ――――――――――――――――――――――――――――――――"
if [ -d "$REPO_DIR/vdb" ]; then
    mkdir -p "$HERMES_DIR/vdb"
    for f in sparse.py embed.py indexer.py matcher.py __init__.py; do
        if [ -f "$REPO_DIR/vdb/$f" ]; then
            do_cp "$REPO_DIR/vdb/$f" "$HERMES_DIR/vdb/$f" "vdb/$f"
        fi
    done
fi
echo ""

# ── 5. scripts ──────────────────────────────────────────────────────
echo "── 第 5 步: 辅助脚本 ――――――――――――――――――――――――――――――――――"
if [ -d "$REPO_DIR/scripts" ]; then
    mkdir -p "$HERMES_DIR/scripts"
    for f in "$REPO_DIR/scripts"/*; do
        name=$(basename "$f")
        do_cp "$f" "$HERMES_DIR/scripts/$name" "scripts/$name"
    done
fi
echo ""

# ── 6. vdb 环境初始化 ──────────────────────────────────────────────
echo "── 第 6 步: vdb 环境初始化 ――――――――――――――――――――――――――――――"
if $DRY; then
    echo "  [DRY] 跳过环境初始化"
elif $IS_NEW || $FORCE; then
    if [ -f "$HERMES_DIR/scripts/init-vdb.sh" ]; then
        if [ -n "$PROFILE" ]; then
            echo "  运行: bash $HERMES_DIR/scripts/init-vdb.sh --profile $PROFILE"
            bash "$HERMES_DIR/scripts/init-vdb.sh" --profile "$PROFILE"
        else
            echo "  运行: bash $HERMES_DIR/scripts/init-vdb.sh"
            bash "$HERMES_DIR/scripts/init-vdb.sh"
        fi
    else
        echo "  ⚠ scripts/init-vdb.sh 未找到，跳过"
    fi
else
    echo "  检测到已有 ~/.hermes/vdb/.venv，跳过"
    if [ -n "$PROFILE" ]; then
        echo "  如需重建: bash $HERMES_DIR/scripts/init-vdb.sh --profile $PROFILE"
    else
        echo "  如需重建: bash $HERMES_DIR/scripts/init-vdb.sh"
    fi
fi
echo ""

# ── 7. vdb 预热 + 索引检测 ──────────────────────────────────────────
echo "── 第 7 步: vdb 预热 + 索引检测 ―――――――――――――――――――――――――――"
if $DRY; then
    echo "  [DRY] 跳过 vdb 预热"
else
    PYTHON=""
    if [ -d "$HERMES_DIR/vdb/.venv" ]; then
        PYTHON="$HERMES_DIR/vdb/.venv/bin/python3"
    else
        PYTHON="python3"
    fi
    if [ -f "$HERMES_DIR/scripts/vdb-autoload.py" ]; then
        PYTHONPATH="$HERMES_DIR/vdb" "$PYTHON" "$HERMES_DIR/scripts/vdb-autoload.py" --force 2>&1 || true
    else
        echo "  ⚠ scripts/vdb-autoload.py 未找到，跳过"
    fi
fi
echo ""

# ── 完成 ────────────────────────────────────────────────────────────
echo "=========================================="
if $DRY; then
    echo " DRY RUN 完成 — 未执行任何实际变更"
else
    echo " 安装完成"
    echo ""
    echo " 下一步:"
    if $IS_NEW; then
        echo "   1. 编辑 $HERMES_DIR/.env 填入 SILICONFLOW_API_KEY"
        echo "   2. 重启 Hermes 会话"
        echo "   3. 运行 'hermes chat' 验证"
        echo ""
        echo " 多 profile 用户:"
        if [ -n "$PROFILE" ]; then
            echo "   已安装到 profile $PROFILE，vdb 自动扫描 $HERMES_SKILL_DIR"
            echo "   后续重建索引：bash $HERMES_DIR/scripts/init-vdb.sh --profile $PROFILE"
        else
            echo "   默认 vdb 扫描 ~/.hermes/skills/，profile 用户更多支持："
            echo "   bash install.sh --profile <name>   # 安装到指定 profile"
            echo "   或设置环境变量："
            echo "   export HERMES_SKILL_DIR=~/.hermes/profiles/<name>/skills"
        fi
    else
        echo "   1. 手动合并 SOUL.md / USER.md（见上方提示）"
        echo "   2. 重启 Hermes 会话"
    fi
fi
echo "=========================================="
