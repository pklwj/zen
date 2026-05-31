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
# 💡 优化：解除 CPU 压缩瓶颈后，IO 成为主导。SSD 用户建议设为 4~8，机械硬盘建议 2~4
MAX_WORKERS = 4 
# 优先从系统环境变量获取 Token，若没有则使用默认
BGM_TOKEN = os.getenv("BANGUMI_TOKEN", "eQBFKrLUr8g0RqLrukNmfVC6QLSR0gCzQxlqtUxw")
API_REQUEST_DELAY = 0.8  # 请求间隔，防IP/Token封禁

# 全局请求会话 + 重试策略 (自动处理网络波动，无需手写 while 循环)
session = requests.Session()
retry_strategy = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

# 预编译正则表达式 (提升批量处理性能，避免重复编译)
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
@functools.lru_cache(maxsize=None)
def search_bangumi_subject(keywords, token=None):
    url = "https://api.bgm.tv/v0/search/subjects"
    headers = {"User-Agent": "ComicScraper/1.0 (Windows)", "Accept": "application/json"}
    if token: headers["Authorization"] = f"Bearer {token}"

    payload = {"keyword": keywords, "filter": {"type": [1]}, "limit": 5}

    try:
        time.sleep(API_REQUEST_DELAY)  # 限流保护
        response = session.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        res_data = response.json().get("data", [])
        print(f"🌐 搜索成功: {keywords} (找到 {len(res_data)} 条)")
        return tuple(res_data)
    except (requests.exceptions.RequestException, Exception) as e:
        print(f"❌ 搜索请求失败或网络超时: {str(e)[:60]}")
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
    except (requests.exceptions.RequestException, Exception) as e:
        print(f"❌ 获取条目详情失败(ID:{subject_id}): {str(e)[:60]}")
        return {}

# ==============================================================================
# XML 生成与文件名清洗模块
# ==============================================================================
def generate_comic_info_xml(data, volume_number, item_title=""):
    root = ET.Element("ComicInfo", {
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xmlns:xsd": "http://www.w3.org/2001/XMLSchema"
    })

    def add_node(tag, text):
        if text not in (None, ""):
            ET.SubElement(root, tag).text = str(text)

    add_node("Series", data.get("name_cn") or data.get("name"))
    add_node("Number", volume_number)
    add_node("Volume", volume_number)
    add_node("Title", item_title or f"第 {volume_number} 卷")
    add_node("Summary", data.get("summary"))

    # 日期处理
    if date_str := data.get("date"):
        parts = date_str.split("-")
        if len(parts) >= 1: add_node("Year", parts[0])
        if len(parts) >= 2 and parts[1]: add_node("Month", int(parts[1]))
        if len(parts) >= 3 and parts[2]: add_node("Day", int(parts[2]))

    # 解析 Infobox
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
# 核心工作流 (极速追加 + 零重压缩流式搬运)
# ==============================================================================
def inject_xml_into_zip_worker(file_info):
    file_path, bgm_data, filename = file_info
    vol_num = extract_volume_number(filename)
    temp_zip = file_path + ".temp"
    
    try:
        # 1. 预生成 XML 内容
        xml_content = generate_comic_info_xml(bgm_data, vol_num)
        
        # 2. 快速检测是否已存在 ComicInfo.xml
        has_comic_info = False
        with zipfile.ZipFile(file_path, 'r') as zin:
            for name in zin.namelist():
                check_name = name
                try:
                    # 兼容中文文件名 cp437 乱码问题
                    check_name = name.encode('cp437').decode('utf-8')
                except Exception:
                    pass
                if check_name.lower() == 'comicinfo.xml':
                    has_comic_info = True
                    break

        # 🚀 极速路径：如果没有旧 XML，直接追加！(耗时 < 10ms，不触碰原图片)
        if not has_comic_info:
            with zipfile.ZipFile(file_path, 'a', zipfile.ZIP_STORED) as zout:
                zout.writestr('ComicInfo.xml', xml_content)
            return f"⚡ [秒追加] 成功注入 XML (第 {vol_num} 卷) -> {filename}"

        # 🛠️ 重写路径：必须抹除旧 XML 时，使用 ZIP_STORED 避免 CPU 密集重压缩
        with zipfile.ZipFile(file_path, 'r') as zin, \
             zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_STORED) as zout:
            
            for item in zin.infolist():
                actual_filename = item.filename
                try:
                    actual_filename = item.filename.encode('cp437').decode('utf-8')
                except Exception:
                    pass

                # 抹除旧的元数据
                if actual_filename.lower() == 'comicinfo.xml':
                    continue
                
                # 💡 核心优化：强制将压缩方式改为 ZIP_STORED (仅存储)
                # 漫画图片已是压缩格式，重新 DEFLATE 极度耗时且无收益
                item.compress_type = zipfile.ZIP_STORED
                
                # 读取并写入 (因为是 STORED 模式，速度极快，相当于直接拷贝字节)
                zout.writestr(item, zin.read(item.filename))

            # 注入新的 XML
            zout.writestr('ComicInfo.xml', xml_content)

        # 原子替换
        os.replace(temp_zip, file_path)
        return f"🔄 [重写] 成功安全注入 XML (第 {vol_num} 卷) -> {filename}"

    except Exception as e:
        # 异常垃圾清理
        if os.path.exists(temp_zip):
            try: os.remove(temp_zip)
            except Exception: pass

        # 降级兜底追加
        try:
            with zipfile.ZipFile(file_path, 'a', compression=zipfile.ZIP_STORED) as zout:
                zout.writestr('ComicInfo.xml', generate_comic_info_xml(bgm_data, vol_num))
            return f"⚠️ [强制写入] 压缩包异常，已成功追加元数据 XML -> {filename}"
        except Exception as final_e:
            return f"❌ 无法处理 -> {filename} (原因: {final_e})"

# ==============================================================================
# 核心业务逻辑封装
# ==============================================================================
def process_single_directory(target_dir):
    print(f"\n📂 -----------------------------------------------------")
    print(f"📂 正在处理目录: {target_dir}")
    print(f"📂 -----------------------------------------------------")

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
    print(f"🚀 元数据已就绪！并发数: {MAX_WORKERS}，正在安全搬运处理: 《{final_title}》...")

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
    print(" 🎬 Bangumi 漫画刮削器 (安全流式搬运·极速追加版) ")
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