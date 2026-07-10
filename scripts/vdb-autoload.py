"""vdb 启动预热 + 索引过期检测

用途：
  1. 预热 Chroma 连接（消除首查延迟）
  2. 检测 skills/ 是否比索引新
  3. 检测到过期时自动重建（--force）或提示

用法：
  python3 vdb-autoload.py            # 预热 + 被动检测，过期提示
  python3 vdb-autoload.py --force    # 预热 + 过期自动重建
  python3 vdb-autoload.py --check    # 只检测不预热

放置位置：~/.hermes/scripts/vdb-autoload.py
install.sh 在安装最后自动执行一次。
"""

import sys, os
import argparse

VDB_DIR = os.path.expanduser("~/.hermes/vdb")
HERMES_HOME = os.path.expanduser("~/.hermes")
ENV_PATH = os.path.join(HERMES_HOME, ".env")

# 确保 vdb 在 Python 路径
if VDB_DIR not in sys.path:
    sys.path.insert(0, VDB_DIR)

# 从 .env 读取 API Key
if not os.environ.get("SILICONFLOW_API_KEY"):
    if os.path.exists(ENV_PATH):
        for line in open(ENV_PATH):
            if line.startswith("SILICONFLOW_API_KEY="):
                val = line.split("=", 1)[1].strip().strip("\"'")
                os.environ["SILICONFLOW_API_KEY"] = val
                break


def warmup():
    """预热 Chroma 连接。"""
    try:
        from matcher import _get_collection, is_healthy
        _get_collection()
        return is_healthy()
    except Exception as e:
        print(f"[vdb] 预热失败: {e}")
        return False


def check_stale():
    """检查索引是否过期。"""
    try:
        from indexer import check_index_stale
        stale, reason = check_index_stale()
        return stale, reason
    except Exception as e:
        return True, str(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="vdb 预热 + 索引检测")
    parser.add_argument("--force", action="store_true", help="过期自动重建")
    parser.add_argument("--check", action="store_true", help="只检测不预热")
    args = parser.parse_args()

    if args.check:
        stale, reason = check_stale()
        if stale:
            print(f"[vdb] 索引过期: {reason}")
            print("[vdb] 运行：cd ~/.hermes/vdb && source .venv/bin/activate && PYTHONPATH=$PWD python3 -c \"from indexer import build_index; build_index(force=True)\"")
        else:
            print("[vdb] 索引最新")
        sys.exit(0 if not stale else 1)

    # 预热
    ok = warmup()
    if ok:
        print("[vdb] ✅ Chroma 预热完成")
    else:
        print("[vdb] ⚠️  Chroma 不可用，vdb 将降级为 skills_list 回退")

    # 检测过期
    stale, reason = check_stale()
    if stale:
        print(f"[vdb] ⚠️  索引过期: {reason}")
        if args.force:
            print("[vdb]   自动重建中...")
            sys.path.insert(0, VDB_DIR)
            from indexer import build_index
            build_index(force=True)
        else:
            print("[vdb]   运行以下命令重建：")
            print("       cd ~/.hermes/vdb && source .venv/bin/activate && PYTHONPATH=$PWD python3 -c \"from indexer import build_index; build_index(force=True)\"")
    else:
        print("[vdb] ✅ 索引最新")
