import subprocess
import yaml
import re
import requests
from pathlib import Path
import time

# -------------------------------
# 配置
# -------------------------------
BASE_DIR = Path(__file__).parent

CLASH_SPEEDTEST_EXE = str(BASE_DIR / "clash-speedtest.exe")  # 如果不在同目录，请填完整路径

INPUT_YAML = r"C:\Users\higashi\AppData\Roaming\io.github.clash-verge-rev.clash-verge-rev\profiles\RyiaJarOeF1H.yaml"
AUTO_YAML  = r"C:\Users\higashi\AppData\Roaming\io.github.clash-verge-rev.clash-verge-rev\profiles\Ryia_Auto.yaml"

RESULT_INPUT = Path(AUTO_YAML).parent / "result_input.yaml"
RESULT_AUTO  = Path(AUTO_YAML).parent / "result_auto.yaml"

MIN_SPEED_MBPS = 0.5

CLASH_API = "http://127.0.0.1:9097"        # 外部控制器监听地址
CLASH_SECRET = "higashi8690"               # 外部控制器 API 密钥

# -------------------------------
# 清理旧测速结果
# -------------------------------
for f in (RESULT_INPUT, RESULT_AUTO):
    try:
        if f.exists():
            f.unlink()
            print(f"删除旧文件: {f}")
    except Exception as e:
        print(f"删除失败 {f}: {e}")

# -------------------------------
# 如果 Ryia_Auto.yaml 不存在，则初始化为 INPUT_YAML 内容
# -------------------------------
if not Path(AUTO_YAML).exists():
    print(f"{AUTO_YAML} 不存在，初始化为 {INPUT_YAML} 内容")
    content = Path(INPUT_YAML).read_text(encoding="utf-8")
    Path(AUTO_YAML).write_text(content, encoding="utf-8")

# -------------------------------
# 测速函数（在独立 PowerShell 窗口执行）
# -------------------------------
def speedtest(yaml_file: str, result_file: Path):
    if not Path(yaml_file).exists():
        print(f"配置文件不存在：{yaml_file}")
        return False

    print(f"\n开始测速：{yaml_file}")
    print(f"输出文件：{result_file}")

    # PowerShell 命令
    cmd = f'''
    & "{CLASH_SPEEDTEST_EXE}" `
    -c "{yaml_file}" `
    -concurrent 8 `
    -min-download-speed {MIN_SPEED_MBPS} `
    -output "{result_file}"
    pause
    '''

    # 新开 PowerShell 窗口执行
    subprocess.Popen([
        "powershell.exe",
        "-NoExit",
        "-Command",
        cmd
    ])

    # 等待 result 文件生成
    while not result_file.exists():
        time.sleep(2)

    print(f"{result_file.name} 已生成")

    # 等待文件大小稳定
    stable_count = 0
    last_size = -1
    while stable_count < 3:
        time.sleep(2)
        size = result_file.stat().st_size
        if size == last_size:
            stable_count += 1
        else:
            stable_count = 0
            last_size = size

    print(f"测速完成：{result_file}")
    return True

# -------------------------------
# 调用 clash-speedtest.exe 测速
# -------------------------------
speedtest(AUTO_YAML, RESULT_AUTO)     # 先测速历史节点库
speedtest(INPUT_YAML, RESULT_INPUT)   # 再测速最新订阅

# -------------------------------
# 读取测速结果
# -------------------------------
def load_result(path: Path):
    if not path.exists():
        print(f"结果文件不存在：{path}")
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    proxies = data.get("proxies", [])
    print(f"{path.name} 节点数量: {len(proxies)}")
    return proxies

nodes_auto  = load_result(RESULT_AUTO)
nodes_input = load_result(RESULT_INPUT)

# -------------------------------
# 合并、去重、按测速排序
# -------------------------------
all_nodes = nodes_input + nodes_auto

# 去重（server+port+type+uuid+password 唯一）
seen = set()
unique_nodes = []
for node in all_nodes:
    key = (
        node.get("server"),
        node.get("port"),
        node.get("type"),
        node.get("uuid", ""),
        node.get("password", "")
    )
    if key not in seen:
        seen.add(key)
        unique_nodes.append(node)

# 排序：解析 name 中的下载速度
def get_speed(node):
    name = node.get("name", "")
    m = re.search(r'([\d.]+)\s*MB/s', name)
    return float(m.group(1)) if m else 0

unique_nodes.sort(key=get_speed, reverse=True)
print(f"去重后节点数量: {len(unique_nodes)}")

# -------------------------------
# 生成 Ryia_Auto.yaml，只保留 proxies（不改规则）
# -------------------------------
base_conf = {"proxies": unique_nodes}

Path(AUTO_YAML).write_text(
    yaml.safe_dump(base_conf, allow_unicode=True, sort_keys=False),
    encoding="utf-8"
)
print(f"生成 Ryia_Auto.yaml：{AUTO_YAML}")

# -------------------------------
# 调用 Clash API 重载配置
# -------------------------------
try:
    headers = {"Authorization": f"Bearer {CLASH_SECRET}"} if CLASH_SECRET else {}
    resp = requests.put(f"{CLASH_API}/configs", headers=headers, json={"path": str(AUTO_YAML)})
    if resp.ok:
        print("Clash Verge 配置已重载")
    else:
        print("重载失败:", resp.text)
except Exception as e:
    print("调用 Clash API 失败:", e)