import os
import shutil
import subprocess
from datetime import datetime

# ----------------------------
# 源文件（Clash 正在使用的配置）
# ----------------------------
SOURCE_FILE = (
    r"C:\Users\higashi\AppData\Roaming"
    r"\io.github.clash-verge-rev.clash-verge-rev"
    r"\profiles\Ryia_Auto.yaml"
)

# ----------------------------
# Git 仓库目录
# ----------------------------
REPO_PATH = r"E:\Clash Verge\clash-speedtest_Windows_x86_64"

# 仓库内保存的 yaml 文件名
TARGET_FILE = os.path.join(REPO_PATH, "Ryia_Auto.yaml")


def copy_yaml():
    """复制配置文件到 Git 仓库"""

    shutil.copy2(SOURCE_FILE, TARGET_FILE)
    print("✓ 已复制最新 YAML 到仓库")


def github_upload():
    """提交并上传 GitHub"""

    os.chdir(REPO_PATH)

    subprocess.run(["git", "add", "."], check=True)

    commit = subprocess.run(
        [
            "git",
            "commit",
            "-m",
            f"Update {datetime.now():%Y-%m-%d %H:%M:%S}"
        ],
        capture_output=True,
        text=True
    )

    # 没有变化
    if "nothing to commit" in (
        commit.stdout + commit.stderr
    ).lower():
        print("✓ 没有配置变化")
        return

    subprocess.run(["git", "push"], check=True)

    print("✓ GitHub 上传成功")


if __name__ == "__main__":
    copy_yaml()
    github_upload()