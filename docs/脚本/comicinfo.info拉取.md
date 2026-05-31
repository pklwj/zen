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
import re
import time
import zipfile
import functools
import xml.etree.ElementTree as ET
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ==============================================================================
# 性能与全局配置区
# ==============================================================================
MAX_WORKERS = 4
# 优先从系统环境变量获取 Token，若没有则使用默认
BGM_TOKEN = os.getenv("BANGUMI_TOKEN", "eQBFKrLUr8g0RqLrukNmfVC6QLSR0gCzQxlqtUxw")
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif'}
API_REQUEST_DELAY = 0.8  # 请求间隔，防IP/Token封禁

# 全局请求会话 + 重试策略 (自动处理网络波动，无需手写 while 循环)
session = requests.Session()
retry_strategy = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

# 💡 优化 1：预编译正则表达式 (提升批量处理性能，避免重复编译)
CLEAN_NAME_PATTERN = re.compile(
    r'(?i)\[.*?\]|\(.*?\)|'
    r'\b(?:vol\.?|v|ch\.?|chapter|tome)\s*\d+\b|'
    r'第\s*\d+\s*[卷话册本]|'
    r'\b\d+\b'
)
VOLUME_PATTERN = re.compile(r'(?:[Vv]ol\.?|[Vv]|第)\s*(\d+)|(\d+)')

# ==============================================================================
# Bangumi 网络数据请求模块
# ==============================================================================
# 💡 优化 2：利用 lru_cache 自动实现线程安全的内存缓存，干掉手动字典和 threading.Lock
@functools.lru_cache(maxsize=None)
def search_bangumi_subject(keywords, token=None):
    url = "https://api.bgm.tv/v0/search/subjects"
    headers = {"User-Agent": "ComicScraper/1.0 (Windows)", "Accept": "application/json"}
    if token: headers["Authorization"] = f"Bearer {token}"

    payload = {"keyword": keywords, "filter": {"type": [1]}, "limit": 5}

    try:
        time.sleep(API_REQUEST_DELAY)  # 限流保护 (命中缓存时不会执行此行)
        response = session.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        res_data = response.json().get("data", [])
        print(f"🌐 搜索成功: {keywords} (找到 {len(res_data)} 条)")
        return tuple(res_data)  # lru_cache 要求返回值可哈希，转为 tuple
    except requests.exceptions.RequestException as e:
        print(f"❌ 搜索请求失败: {str(e)[:60]}")
        return tuple()

@functools.lru_cache(maxsize=None)
def get_bangumi_comic_info(subject_id, token=None):
    url = f"https://api.bgm.tv/v0/subjects/{subject_id}"
    headers = {"User-Agent": "ComicScraper/1.0 (Windows)", "Accept": "application/json"}
    if token: headers["Authorization"] = f"Bearer {token}"

    try:
        time.sleep(API_REQUEST_DELAY)
        response = session.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json() or {}
    except Exception as e:
        print(f"❌ 获取条目详情失败(ID:{subject_id}): {str(e)[:60]}")
        return {}

# ==============================================================================
# XML 生成与文件名清洗模块
# ==============================================================================
def generate_comic_info_xml(data, volume_number, page_count=0, item_title=""):
    root = ET.Element("ComicInfo", {
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xmlns:xsd": "http://www.w3.org/2001/XMLSchema"
    })

    # 💡 优化 3：使用辅助函数消灭满屏的 if 判断
    def add_node(tag, text):
        if text not in (None, ""):
            ET.SubElement(root, tag).text = str(text)

    add_node("Series", data.get("name_cn") or data.get("name"))
    add_node("Number", volume_number)
    add_node("Volume", volume_number)
    add_node("Title", item_title or f"第 {volume_number} 卷")
    if page_count > 0: add_node("PageCount", page_count)
    add_node("Summary", data.get("summary"))

    # 日期处理
    if date_str := data.get("date"):
        parts = date_str.split("-")
        if len(parts) >= 1: add_node("Year", parts[0])
        if len(parts) >= 2 and parts[1]: add_node("Month", int(parts[1]))
        if len(parts) >= 3 and parts[2]: add_node("Day", int(parts[2]))

    # 解析 Infobox (使用 set 提升 in 判断效率)
    writers, pencillers, publishers = [], [], []
    total_volumes = "0"
    for item in data.get("infobox", []):
        key, val_data = item.get("key", ""), item.get("value", "")
        values = [v.get("v", "") for v in val_data if "v" in v] if isinstance(val_data, list) else [val_data]
        values = [v for v in values if v]
        if not values: continue

        if key in {"作者", "原作", "原案"}: writers.extend(values)
        elif key in {"作画", "插画", "插图", "漫画"}: pencillers.extend(values)
        elif key == "出版社": publishers.extend(values)
        elif key in {"册数", "卷数"}: total_volumes = values[0].replace("卷", "").replace("册", "").strip()

    add_node("Writer", ", ".join(writers) if writers else None)
    add_node("Penciller", ", ".join(pencillers) if pencillers else ", ".join(writers))
    add_node("Publisher", ", ".join(publishers) if publishers else None)
    if total_volumes.isdigit() and int(total_volumes) > 0: add_node("Count", total_volumes)

    if rating := data.get("rating", {}).get("score"): add_node("CommunityRating", rating)
    tags = [t.get("name") for t in data.get("tags", []) if t.get("name")]
    if tags: add_node("Tags", ", ".join(tags[:10]))

    add_node("Manga", "Yes")
    add_node("Web", f"https://bgm.tv/subject/{data.get('id')}")

    # 💡 优化 4：抛弃 minidom，使用原生 ET.indent (避免产生多余空行 Bug)
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")

def clean_comic_name(filename):
    name = Path(filename).stem
    return CLEAN_NAME_PATTERN.sub('', name).strip(" -_[]().")

def extract_volume_number(filename):
    match = VOLUME_PATTERN.search(filename)
    if match: return int(match.group(1) or match.group(2))
    return 1

# ==============================================================================
# 核心工作流 (ZIP 注入)
# ==============================================================================
def inject_xml_into_zip_worker(file_info):
    file_path, bgm_data, filename = file_info
    vol_num = extract_volume_number(filename)
    
    try:
        temp_zip = file_path + ".temp"
        page_count = 0
        has_comic_info = False

        # 💡 优化 5：统一使用“读写分离”的流式搬运，干掉臃肿的 if-else 分支
        with zipfile.ZipFile(file_path, 'r') as zin, \
             zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zout:
            
            for item in zin.infolist():
                try:
                    actual_filename = item.filename.encode('cp437').decode('utf-8')
                except Exception:
                    actual_filename = item.filename

                if actual_filename.lower() == 'comicinfo.xml':
                    has_comic_info = True
                    continue  # 过滤掉旧的 XML
                
                if Path(actual_filename).suffix.lower() in IMAGE_EXTENSIONS:
                    page_count += 1
                    
                zout.writestr(item, zin.read(item.filename))

            # 注入包含真实页数的新 XML
            xml_content = generate_comic_info_xml(bgm_data, vol_num, page_count)
            zout.writestr('ComicInfo.xml', xml_content)

        # 原子替换
        os.replace(temp_zip, file_path)
        action = "更新" if has_comic_info else "秒过"
        return f"⚡ [{action}] 成功注入 XML (第 {vol_num} 卷/共 {page_count} 页) -> {filename}"

    except Exception as e:
        # 兜底：如果压缩包损坏，尝试强制追加
        try:
            with zipfile.ZipFile(file_path, 'a', compression=zipfile.ZIP_DEFLATED) as zout:
                zout.writestr('ComicInfo.xml', generate_comic_info_xml(bgm_data, vol_num, 0))
            return f"⚠️ [强制写入] 压缩包损坏，已成功注入XML -> {filename}"
        except Exception as final_e:
            return f"❌ 无法处理 -> {filename} (原因: {final_e})"

# ==============================================================================
# 核心业务逻辑封装
# ==============================================================================
def process_single_directory(target_dir):
    print(f"\n📂 -----------------------------------------------------")
    print(f"📂 正在处理目录: {target_dir}")
    print(f"📂 -----------------------------------------------------")

    # 💡 优化 6：使用 pathlib 优雅地获取文件列表
    folder = Path(target_dir)
    files = [f for f in folder.iterdir() if f.suffix.lower() in {'.zip', '.cbz'}]
    
    if not files:
        print("💡 未在此文件夹内找到 .zip 或 .cbz 格式的漫画文件，跳过。")
        return False

    # 智能识别名字
    guessed_names = {clean_comic_name(f.name) for f in files if clean_comic_name(f.name)}
    if not guessed_names:
        search_keyword = input("🤔 未能自动解析出漫画名字，请手动输入名称搜索: ").strip()
    else:
        default_search = list(guessed_names)[0]
        print(f"🤖 智能识别出的漫画名字为: 【{default_search}】")
        search_keyword = input(f"直接[回车]以此名字搜索，或输入新名字(输入s跳过本文件夹): ").strip()
        if search_keyword.lower() == 's': return False
        if not search_keyword: search_keyword = default_search

    if not search_keyword:
        print("⏩ 关键字为空，跳过此文件夹。")
        return False

    print(f"🌐 正在 Bangumi 搜索 '{search_keyword}'...")
    # 注意：lru_cache 返回的是 tuple，需要转回 list 方便后续操作
    search_results = list(search_bangumi_subject(search_keyword, token=BGM_TOKEN))

    if not search_results:
        print("❌ 未能在 Bangumi 上搜到相关书籍/漫画。")
        manual_id = input("💡 请手动输入 bgm.tv 条目 ID (直接回车跳过当前文件夹): ").strip()
        if not manual_id.isdigit(): return False
        selected_subject_id = int(manual_id)
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

    tasks = [(str(f), bgm_data, f.name) for f in files]
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(inject_xml_into_zip_worker, task) for task in tasks]
        for future in as_completed(futures):
            print(future.result())

    print(f"🎉 当前文件夹 【{final_title}】 处理完成！累计耗时: {time.time() - start_time:.2f} 秒。")
    return True

# ==============================================================================
# 主程序
# ==============================================================================
def main():
    print("=========================================================")
    print(" 🎬 Bangumi 漫画刮削器 (纯命令行·极简重构版) ")
    print("=========================================================")
    print("请粘贴漫画文件夹路径（每行一个，可带双引号，支持右键直接粘贴）")
    print("输入完成后，按【回车】输入空行结束输入！\n" + "-"*50)

    chosen_directories = []
    while True:
        try:
            line = input().strip()
        except EOFError:
            break
        if not line: break
        
        path = Path(line.strip('"\'').strip())
        if path.is_dir():
            chosen_directories.append(path)
        else:
            print(f"⚠️  无效路径已跳过: {line}")

    if not chosen_directories:
        print("\n👋 未输入有效路径，程序退出")
        return

    print(f"\n📋 成功识别到 {len(chosen_directories)} 个有效文件夹：")
    for index, folder_path in enumerate(chosen_directories, 1):
        print(f"{index}. {folder_path}")
    input("\n按回车键开始批量处理所有文件夹...")

    total_dirs = len(chosen_directories)
    global_start_time = time.time()
    
    for i, directory in enumerate(chosen_directories, 1):
        print(f"\n====================== 进度: {i}/{total_dirs} ======================")
        process_single_directory(str(directory))

    print(f"\n🏁 全部处理完成！总耗时: {time.time() - global_start_time:.2f} 秒")
    
    # 清理缓存
    search_bangumi_subject.cache_clear()
    get_bangumi_comic_info.cache_clear()

if __name__ == '__main__':
    main()
```