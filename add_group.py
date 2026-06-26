import yaml
import requests
from pathlib import Path

# -----------------------
# 配置
# -----------------------
YAML_FILE = r"C:\Users\higashi\AppData\Roaming\io.github.clash-verge-rev.clash-verge-rev\profiles\Ryia_Auto.yaml"
CLASH_API = "http://127.0.0.1:9097"
CLASH_SECRET = "higashi8690"

# -----------------------
# 读取 YAML
# -----------------------
path = Path(YAML_FILE)
with open(path, "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)

if "proxies" not in data or not data["proxies"]:
    print("未找到 proxies")
    exit()

print("===== 节点名称 =====")

for p in data["proxies"]:
    print(repr(p.get("name", "")))


# -----------------------
# 删除 CN 节点、无测速节点，并保留前5个 RO 节点
# -----------------------
removed = []
new_proxies = []

ro_count = 0

for p in data["proxies"]:
    name = p.get("name", "")
    upper_name = name.upper()

    # 删除没有测速结果的节点
    if "⬇️" not in name:
        removed.append(name)
        continue

    # 删除 CN 节点
    if "🇨🇳" in name or " CN " in upper_name:
        removed.append(name)
        continue

    # RO 节点只保留前5个
    if "🇷🇴" in name:
        ro_count += 1

        if ro_count > 5:
            removed.append(name)
            continue

    new_proxies.append(p)

data["proxies"] = new_proxies

print(f"共删除 {len(removed)} 个节点")

for n in removed:
    print("删除:", n)

print("\n保留的RO节点:")
for p in data["proxies"]:
    if "🇷🇴" in p["name"]:
        print(p["name"])
# -----------------------
# 提取节点名称
# -----------------------
proxy_names = [p["name"] for p in data["proxies"] if "name" in p]

# -----------------------
# 添加策略组
# -----------------------
data["proxy-groups"] = [
    {
        "name": "Proxy",
        "type": "select",
        "proxies": ["DIRECT"] + proxy_names
    }
]

# -----------------------
# 添加基础规则
# -----------------------
data["rules"] = [
    "GEOSITE,category-ads-all,REJECT",
    "GEOSITE,private,DIRECT",
    "GEOSITE,cn,DIRECT",
    "GEOIP,CN,DIRECT",
    "MATCH,Proxy"
]

# -----------------------
# 保存修改后的 YAML
# -----------------------
with open(path, "w", encoding="utf-8") as f:
    yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)

print("策略组已添加，规则已更新")

# -----------------------
# 通过 Clash API 重载配置
# -----------------------
headers = {"Authorization": f"Bearer {CLASH_SECRET}"} if CLASH_SECRET else {}
resp = requests.put(
    f"{CLASH_API}/configs",
    headers=headers,
    json={"path": YAML_FILE}
)

if resp.ok:
    print("Clash 配置已重载成功！")
else:
    print("配置重载失败:", resp.text)