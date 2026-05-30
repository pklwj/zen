# 从Bangumi拉取ComicInfo.xml

2026年5月29日

## 工具核心功能一览

1. **全格式兼容**：原生支持 `CBZ` / `ZIP` 漫画压缩包（CBZ 本质就是改名的 ZIP）；
2. **批量处理**：支持一次性导入多个漫画文件夹，批量执行任务；
3. **智能识别**：自动清洗杂乱文件名、提取漫画卷号，无需手动修改文件；
4. **Bangumi 数据抓取**：自动获取漫画中文名、作者、作画、出版社、简介、评分、标签、发行日期；
5. **容错损坏文件**：无视 `Bad CRC-32` 校验错误，老旧 / 损坏压缩包也能正常写入元数据；
6. **多线程加速**：多线程并发处理漫画文件，大幅提升批量处理速度；
7. **标准 XML 输出**：生成行业通用 `ComicInfo.xml`，适配 99% 主流漫画阅读器。

```python
import os
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom
import zipfile
import re
import requests
import time
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ==============================================================================
# 性能与全局配置区
# ==============================================================================
MAX_WORKERS = 4
# 优先从系统环境变量获取 Token，若没有则使用默认（建议生产环境不硬编码）
BGM_TOKEN = os.getenv("BANGUMI_TOKEN", "eQBFKrLUr8g0RqLrukNmfVC6QLSR0gCzQxlqtUxw")
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif')

# Bangumi API 全局配置 & 缓存
API_REQUEST_DELAY = 0.8       # 请求间隔，防IP/Token封禁
SEARCH_CACHE = dict()          # 搜索结果缓存
SUBJECT_CACHE = dict()         # 条目详情缓存
cache_lock = threading.Lock()  # 线程锁，确保多线程下缓存读写安全

# 全局请求会话 + 重试策略
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[429, 500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

# ==============================================================================
# Bangumi 网络数据请求模块
# ==============================================================================
def search_bangumi_subject(keywords, token=None):
    with cache_lock:
        if keywords in SEARCH_CACHE:
            print(f"💾 搜索结果命中缓存: {keywords}")
            return SEARCH_CACHE[keywords]

    url = "https://api.bgm.tv/v0/search/subjects"
    headers = {
        "User-Agent": "ComicScraper/1.0 (Windows)",
        "Accept": "application/json"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # 修正：Bangumi API 中 type=1 代表书籍(Book)，包含漫画与小说
    payload = {
        "keyword": keywords,
        "filter": {"type": [1]},  
        "limit": 5
    }

    try:
        time.sleep(API_REQUEST_DELAY)  # 限流保护
        response = session.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        res_data = response.json().get("data", [])
        
        with cache_lock:
            SEARCH_CACHE[keywords] = res_data
        return res_data
    except requests.exceptions.RequestException as e:
        print(f"❌ 搜索请求失败: {str(e)[:60]}")
        with cache_lock:
            SEARCH_CACHE[keywords] = []  
        return []

def get_bangumi_comic_info(subject_id, token=None):
    sid = str(subject_id)
    with cache_lock:
        if sid in SUBJECT_CACHE:
            print(f"💾 条目详情命中缓存: ID {subject_id}")
            return SUBJECT_CACHE[sid]

    url = f"https://api.bgm.tv/v0/subjects/{subject_id}"
    headers = {
        "User-Agent": "ComicScraper/1.0 (Windows)",
        "Accept": "application/json"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        time.sleep(API_REQUEST_DELAY)  # 限流保护
        response = session.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        res_data = response.json() if response.json() else {}
        
        with cache_lock:
            SUBJECT_CACHE[sid] = res_data
        return res_data
    except Exception as e:
        print(f"❌ 获取条目详情失败(ID:{subject_id}): {str(e)[:60]}")
        with cache_lock:
            SUBJECT_CACHE[sid] = {}  
        return []

# ==============================================================================
# XML 生成与文件名清洗模块
# ==============================================================================
def generate_comic_info_xml(data, volume_number, page_count=0, item_title=""):
    root = ET.Element("ComicInfo", {
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xmlns:xsd": "http://www.w3.org/2001/XMLSchema"
    })

    name_cn = data.get("name_cn") or data.get("name")
    ET.SubElement(root, "Series").text = name_cn
    ET.SubElement(root, "Number").text = str(volume_number)
    ET.SubElement(root, "Volume").text = str(volume_number)
    ET.SubElement(root, "Title").text = item_title if item_title else f"第 {volume_number} 卷"

    if page_count > 0:
        ET.SubElement(root, "PageCount").text = str(page_count)

    summary = data.get("summary", "")
    if summary:
        ET.SubElement(root, "Summary").text = summary

    date_str = data.get("date", "")
    if date_str:
        parts = date_str.split("-")
        if len(parts) >= 1 and parts[0]:
            ET.SubElement(root, "Year").text = parts[0]
        if len(parts) >= 2 and parts[1]:
            ET.SubElement(root, "Month").text = str(int(parts[1]))
        if len(parts) >= 3 and parts[2]:
            ET.SubElement(root, "Day").text = str(int(parts[2]))

    infobox = data.get("infobox", [])
    writers, pencillers, publishers = [], [], []
    total_volumes = "0"

    for item in infobox:
        key = item.get("key", "")
        value_data = item.get("value", "")

        values = [v.get("v", "") for v in value_data if "v" in v] if isinstance(value_data, list) else [value_data]
        values = [v for v in values if v]
        if not values:
            continue

        if key in ["作者", "原作", "原案"]:
            writers.extend(values)
        elif key in ["作画", "插画", "插图", "漫画"]:
            pencillers.extend(values)
        elif key in ["出版社"]:
            publishers.extend(values)
        elif key in ["册数", "卷数"]:
            total_volumes = values[0].replace("卷", "").replace("册", "").strip()

    if writers:
        ET.SubElement(root, "Writer").text = ", ".join(writers)
    if pencillers:
        ET.SubElement(root, "Penciller").text = ", ".join(pencillers)
    elif writers:
        ET.SubElement(root, "Penciller").text = ", ".join(writers)

    if publishers:
        ET.SubElement(root, "Publisher").text = ", ".join(publishers)

    if total_volumes.isdigit() and int(total_volumes) > 0:
        ET.SubElement(root, "Count").text = total_volumes

    rating = data.get("rating", {}).get("score")
    if rating:
        ET.SubElement(root, "CommunityRating").text = str(rating)

    tags = [t.get("name") for t in data.get("tags", []) if t.get("name")]
    if tags:
        ET.SubElement(root, "Tags").text = ", ".join(tags[:10])

    ET.SubElement(root, "Manga").text = "Yes"
    ET.SubElement(root, "Web").text = f"https://bgm.tv/subject/{data.get('id')}"

    xml_str = ET.tostring(root, encoding="utf-8")
    parsed_str = minidom.parseString(xml_str)
    return parsed_str.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")

def clean_comic_name(filename):
    name = os.path.splitext(filename)[0]
    name = re.sub(r'\[.*?\]|\(.*?\)', '', name)
    name = re.sub(r'(?i)\b(vol\.?|v|ch\.?|chapter|tome)\s*\d+\b', '', name)
    name = re.sub(r'第\s*\d+\s*[卷话册本]', '', name)
    name = re.sub(r'\b\d+\b', '', name)
    name = name.strip(" -_[]().")
    return name

def extract_volume_number(filename):
    match = re.search(r'(?:[Vv]ol\.?|[Vv]|[第第])\s*(\d+)', filename)
    if match:
        return int(match.group(1))
    match = re.search(r'(\d+)', filename)
    if match:
        return int(match.group(1))
    return 1

# ==============================================================================
# 核心工作流
# ==============================================================================
def inject_xml_into_zip_worker(file_info):
    file_path, bgm_data, filename = file_info
    vol_num = extract_volume_number(filename)
    page_count = 0
    has_comic_info = False

    try:
        with zipfile.ZipFile(file_path, 'r') as zin:
            for item in zin.infolist():
                try:
                    actual_filename = item.filename.encode('cp437').decode('utf-8')
                except Exception:
                    actual_filename = item.filename

                if actual_filename.lower() == 'comicinfo.xml':
                    has_comic_info = True
                if actual_filename.lower().endswith(IMAGE_EXTENSIONS):
                    page_count += 1

        xml_content = generate_comic_info_xml(bgm_data, volume_number=vol_num, page_count=page_count)

        if has_comic_info:
            temp_zip = file_path + ".temp"
            with zipfile.ZipFile(file_path, 'r') as zin:
                with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zout:
                    for item in zin.infolist():
                        try:
                            af = item.filename.encode('cp437').decode('utf-8')
                        except Exception:
                            af = item.filename
                        if af.lower() == 'comicinfo.xml':
                            continue
                        try:
                            zout.writestr(item, zin.read(item.filename))
                        except Exception:
                            continue
                    zout.writestr('ComicInfo.xml', xml_content, compress_type=zipfile.ZIP_DEFLATED)
            shutil.move(temp_zip, file_path)
            return f"⚡ [更新] 成功替换旧 XML (第 {vol_num} 卷/共 {page_count} 页) -> {filename}"
        else:
            with zipfile.ZipFile(file_path, 'a', compression=zipfile.ZIP_DEFLATED) as zout:
                zout.writestr('ComicInfo.xml', xml_content)
            return f"⚡ [秒过] 成功追加 XML (第 {vol_num} 卷/共 {page_count} 页) -> {filename}"

    except Exception:
        try:
            with zipfile.ZipFile(file_path, 'a', compression=zipfile.ZIP_DEFLATED) as zout:
                zout.writestr('ComicInfo.xml', generate_comic_info_xml(bgm_data, vol_num, 0))
            return f"⚠️ [强制写入] 压缩包损坏，已成功注入XML -> {filename}"
        except Exception as e:
            return f"❌ 无法处理 -> {filename} (原因: {e})"

# ==============================================================================
# 核心业务逻辑封装
# ==============================================================================
def process_single_directory(target_dir):
    print(f"\n📂 -----------------------------------------------------")
    print(f"📂 正在处理目录: {target_dir}")
    print(f"📂 -----------------------------------------------------")

    files = [f for f in os.listdir(target_dir) if f.lower().endswith(('.zip', '.cbz'))]
    if not files:
        print("💡 未在此文件夹内找到 .zip 或 .cbz 格式的漫画文件，跳过。")
        return False

    guessed_names = set()
    for f in files:
        cleaned = clean_comic_name(f)
        if cleaned:
            guessed_names.add(cleaned)

    if not guessed_names:
        search_keyword = input("🤔 未能自动解析出漫画名字，请手动输入名称搜索: ").strip()
    else:
        default_search = list(guessed_names)[0]
        print(f"🤖 智能识别出的漫画名字为: 【{default_search}】")
        search_keyword = input(f"直接[回车]以此名字搜索，或输入新名字(输入s跳过本文件夹): ").strip()
        if search_keyword.lower() == 's':
            return False
        if not search_keyword:
            search_keyword = default_search

    if not search_keyword:
        print("⏩ 关键字为空，跳过此文件夹。")
        return False

    print(f"🌐 正在 Bangumi 搜索 '{search_keyword}'...")
    search_results = search_bangumi_subject(search_keyword, token=BGM_TOKEN)

    if not search_results:
        print("❌ 未能在 Bangumi 上搜到相关书籍/漫画。")
        manual_id = input("💡 请手动输入 bgm.tv 条目 ID (直接回车跳过当前文件夹): ").strip()
        if manual_id.isdigit():
            selected_subject_id = int(manual_id)
        else:
            return False
    else:
        print("\n🔍 找到以下最匹配的 Bangumi 结果:")
        for idx, item in enumerate(search_results):
            name_cn = item.get("name_cn") or "无中文名"
            name_origin = item.get("name")
            score = item.get("score", "暂无评分")
            date = item.get("date", "未知日期")
            print(f" [{idx + 1}] {name_cn} / {name_origin} ({date}) [评分: {score}]")

        choice = input(f"\n请选择对应的条目序号 (直接回车默认选 1): ").strip()
        choice_idx = int(choice) - 1 if (choice.isdigit() and 0 < int(choice) <= len(search_results)) else 0
        selected_subject_id = search_results[choice_idx]["id"]

    print("⏳ 正在获取该条目的全量元数据...")
    bgm_data = get_bangumi_comic_info(selected_subject_id, token=BGM_TOKEN)
    if not bgm_data:
        print("❌ 获取元数据失败，跳过该文件夹。")
        return False

    final_title = bgm_data.get('name_cn') or bgm_data.get('name')
    print(f"🚀 元数据已就绪！并发数: {MAX_WORKERS}，正在处理: 《{final_title}》...")

    tasks = [(os.path.join(target_dir, f), bgm_data, f) for f in files]
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(inject_xml_into_zip_worker, task): task for task in tasks}
        for future in as_completed(futures):
            print(future.result())

    elapsed = time.time() - start_time
    print(f"🎉 当前文件夹 【{final_title}】 处理完成！累计耗时: {elapsed:.2f} 秒。")

    return True

# ==============================================================================
# 主程序
# ==============================================================================
def main():
    print("=========================================================")
    print(" 🎬 Bangumi 漫画刮削器 (纯命令行·线程安全优化版) ")
    print("=========================================================")

    print("请粘贴漫画文件夹路径（每行一个，可带双引号，支持右键直接粘贴）")
    print("输入完成后，按【回车】输入空行结束输入！")
    print("---------------------------------------------------------")

    chosen_directories = []
    while True:
        try:
            line = input().strip()
        except EOFError:
            break
        if not line:
            break
        # 去除两侧引号并标准化路径
        path = line.strip('"\'').strip()
        if os.path.isdir(path):
            chosen_directories.append(path)
        else:
            print(f"⚠️  无效路径已跳过: {line}")

    if not chosen_directories:
        print("\n👋 未输入有效路径，程序退出")
        return

    print("\n" + "="*50)
    print(f"📋 成功识别到 {len(chosen_directories)} 个有效文件夹：")
    for index, folder_path in enumerate(chosen_directories, 1):
        print(f"{index}. {folder_path}")
    print("="*50)

    input("\n按回车键开始批量处理所有文件夹...")

    total_dirs = len(chosen_directories)
    print(f"\n✅ 共选中 {total_dirs} 个文件夹，开始处理...")

    global_start_time = time.time()
    for i, directory in enumerate(chosen_directories, 1):
        print(f"\n====================== 进度: {i}/{total_dirs} ======================")
        process_single_directory(directory)

    total_elapsed = time.time() - global_start_time
    print(f"\n🏁 全部处理完成！总耗时: {total_elapsed:.2f} 秒")
    
    with cache_lock:
        SEARCH_CACHE.clear()
        SUBJECT_CACHE.clear()

if __name__ == '__main__':
    main()
```