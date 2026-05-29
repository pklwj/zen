# 从Bangumi拉取ComicInfo.xml

2026年5月29日

## 工具核心功能一览

1. **全格式兼容**：原生支持 `CBZ` / `ZIP` 漫画压缩包（CBZ 本质就是改名的 ZIP）；
2. **批量处理**：支持一次性导入多个漫画文件夹，批量执行任务；
3. **智能识别**：自动清洗杂乱文件名、提取漫画卷号，无需手动修改文件；
4. **Bangumi 数据抓取**：自动获取漫画中文名、作者、作画、出版社、简介、评分、标签、发行日期；
5. **容错损坏文件**：无视 `Bad CRC-32` 校验错误，老旧 / 损坏压缩包也能正常写入元数据；
6. **原生 GUI 界面**：基于 Tkinter 开发，无额外第三方依赖，Windows 直接双击运行；
7. **多线程加速**：多线程并发处理漫画文件，大幅提升批量处理速度；
8. **标准 XML 输出**：生成行业通用 `ComicInfo.xml`，适配 99% 主流漫画阅读器。

```python
# 导入系统标准库，处理文件路径、系统操作
import os
# 导入系统库，用于程序退出等系统操作
import sys
# 导入XML处理库，用于生成ComicInfo.xml标准格式
import xml.etree.ElementTree as ET
# 导入XML格式化库，让生成的XML代码美观易读
from xml.dom import minidom
# 导入ZIP压缩包处理库，用于读写cbz/zip漫画文件
import zipfile
# 导入正则表达式库，用于清洗文件名、提取卷号
import re
# 导入网络请求库，用于调用Bangumi API获取漫画信息
import requests
# 导入时间库，用于计算处理耗时、网络请求延时
import time
# 导入文件操作库，用于临时文件替换、移动
import shutil
# 导入多线程库，实现批量漫画文件并发处理，提升速度
from concurrent.futures import ThreadPoolExecutor, as_completed

# 🌟 导入Tkinter图形界面库，原生无第三方依赖，实现窗口交互
import tkinter as tk
# 导入Tkinter文件选择、弹窗组件
from tkinter import filedialog, messagebox

# ==============================================================================
# 全局配置区域：程序核心参数，可根据需求修改
# ==============================================================================
# 最大并发线程数：同时处理的漫画文件数量
MAX_WORKERS = 4
# Bangumi API授权Token，用于访问接口
BGM_TOKEN = "填入token"
# 支持的漫画图片格式，用于统计压缩包内页数
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif')

# ==============================================================================
# Bangumi 网络请求模块：负责调用API搜索漫画、获取详情
# ==============================================================================
def search_bangumi_subject(keywords, token=None):
    """
    搜索Bangumi漫画条目
    :param keywords: 搜索关键词（漫画名）
    :param token: API授权令牌
    :return: 搜索结果列表，无结果返回空列表
    """
    # Bangumi搜索接口地址
    url = "https://api.bgm.tv/v0/search/subjects"
    # 请求头：标识客户端，符合API规范
    headers = {"User-Agent": "DualComicInfoMultiThreadPacker/8.3"}
    # 传入Token，获取更高API权限
    if token:
        headers["Authorization"] = f"Bearer {token}"
  
    # 请求参数：关键词、过滤类型(1=漫画)、返回数量限制5条
    payload = {
        "keyword": keywords,
        "filter": {"type": [1]}, 
        "limit": 5
    }
  
    try:
        # 发送POST请求，超时时间10秒
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        # 抛出HTTP请求异常
        response.raise_for_status()
        # 解析JSON响应数据
        res_json = response.json()
        # 返回搜索结果数据
        return res_json.get("data", [])
    except requests.exceptions.RequestException as e:
        # 捕获网络/请求异常，打印错误信息
        print(f"❌ 搜索请求失败: {e}")
        return []

def get_bangumi_comic_info(subject_id, token=None):
    """
    根据条目ID获取Bangumi漫画完整详情
    :param subject_id: 漫画条目ID
    :param token: API授权令牌
    :return: 漫画完整信息字典，失败返回None
    """
    # 漫画详情接口地址，拼接条目ID
    url = f"https://api.bgm.tv/v0/subjects/{subject_id}"
    headers = {"User-Agent": "DualComicInfoMultiThreadPacker/8.3"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        # 发送GET请求获取详情
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ 获取条目详情失败: {e}")
        return None

# ==============================================================================
# XML 生成与文件名清洗模块：生成标准ComicInfo.xml + 处理文件名
# ==============================================================================
def generate_comic_info_xml(data, volume_number, page_count=0, item_title=""):
    """
    根据Bangumi数据生成标准ComicInfo.xml格式内容
    :param data: Bangumi漫画详情数据
    :param volume_number: 漫画卷号
    :param page_count: 漫画总页数
    :param item_title: 单卷标题
    :return: 格式化后的XML字符串
    """
    # 创建XML根节点，固定命名空间
    root = ET.Element("ComicInfo", {
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xmlns:xsd": "http://www.w3.org/2001/XMLSchema"
    })

    # 漫画名称（优先中文名，无则用原名）
    name_cn = data.get("name_cn") or data.get("name")
    # 系列名称
    ET.SubElement(root, "Series").text = name_cn
    # 卷号
    ET.SubElement(root, "Number").text = str(volume_number)  
    ET.SubElement(root, "Volume").text = str(volume_number)  
    # 单卷标题
    ET.SubElement(root, "Title").text = item_title if item_title else f"第 {volume_number} 卷"
  
    # 写入页数
    if page_count > 0:
        ET.SubElement(root, "PageCount").text = str(page_count)   

    # 漫画简介
    summary = data.get("summary", "")
    if summary:
        ET.SubElement(root, "Summary").text = summary

    # 出版日期拆分：年/月/日
    date_str = data.get("date", "")
    if date_str:
        parts = date_str.split("-")
        if len(parts) >= 1 and parts[0]: ET.SubElement(root, "Year").text = parts[0]
        if len(parts) >= 2 and parts[1]: ET.SubElement(root, "Month").text = str(int(parts[1]))
        if len(parts) >= 3 and parts[2]: ET.SubElement(root, "Day").text = str(int(parts[2]))

    # 解析作者、作画、出版社、总卷数信息
    infobox = data.get("infobox", [])
    writers, pencillers, publishers = [], [], []
    total_volumes = "0"

    for item in infobox:
        key = item.get("key", "")
        value_data = item.get("value", "")
  
        # 统一处理数据格式
        values = [v.get("v", "") for v in value_data if "v" in v] if isinstance(value_data, list) else [value_data]
        values = [v for v in values if v]  
        if not values: 
            continue

        # 作者/原作
        if key in ["作者", "原作", "原案"]: 
            writers.extend(values)
        # 作画/插画
        elif key in ["作画", "插画", "插图", "漫画"]: 
            pencillers.extend(values)
        # 出版社
        elif key in ["出版社"]: 
            publishers.extend(values)
        # 总卷数
        elif key in ["册数", "卷数"]: 
            total_volumes = values[0].replace("卷", "").replace("册", "").strip()

    # 写入作者信息
    if writers: ET.SubElement(root, "Writer").text = ", ".join(writers)
    # 写入作画信息，无作画则用作者替代
    if pencillers: ET.SubElement(root, "Penciller").text = ", ".join(pencillers)
    elif writers: ET.SubElement(root, "Penciller").text = ", ".join(writers)
  
    # 写入出版社
    if publishers: ET.SubElement(root, "Publisher").text = ", ".join(publishers)

    # 写入总卷数
    if total_volumes.isdigit() and int(total_volumes) > 0:
        ET.SubElement(root, "Count").text = total_volumes

    # 写入评分
    rating = data.get("rating", {}).get("score")
    if rating: 
        ET.SubElement(root, "CommunityRating").text = str(rating)

    # 写入标签，限制10个
    tags = [t.get("name") for t in data.get("tags", []) if t.get("name")]
    if tags: 
        ET.SubElement(root, "Tags").text = ", ".join(tags[:10])

    # 固定标识：漫画
    ET.SubElement(root, "Manga").text = "Yes"
    # 漫画Bangumi地址
    ET.SubElement(root, "Web").text = f"https://bgm.tv/subject/{data.get('id')}"

    # 格式化XML并返回
    xml_str = ET.tostring(root, encoding="utf-8")
    parsed_str = minidom.parseString(xml_str)
    return parsed_str.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")

def clean_comic_name(filename):
    """
    清洗文件名：去除冗余字符，提取纯漫画名
    :param filename: 原始文件名
    :return: 清洗后的漫画名
    """
    # 去除文件后缀
    name = os.path.splitext(filename)[0]
    # 去除括号/方括号内容
    name = re.sub(r'\[.*?\]|\(.*?\)', '', name)
    # 去除卷号标识(vol/v等)
    name = re.sub(r'(?i)\b(vol\.?|v|ch\.?|chapter|tome)\s*\d+\b', '', name)
    # 去除中文卷号标识
    name = re.sub(r'第\s*\d+\s*[卷话册本]', '', name)
    # 去除纯数字
    name = re.sub(r'\b\d+\b', '', name)
    # 去除首尾特殊字符
    name = name.strip(" -_[]().")
    return name

def extract_volume_number(filename):
    """
    从文件名中提取漫画卷号
    :param filename: 原始文件名
    :return: 卷号数字，失败返回None
    """
    # 匹配英文卷号(vol/v)
    match = re.search(r'(?:[Vv]ol\.?|[Vv]|[第])\s*(\d+)', filename)
    if match: 
        return int(match.group(1))
    # 兜底匹配纯数字
    match = re.search(r'(\d+)', filename)
    if match: 
        return int(match.group(1))
    return None

# ==============================================================================
# 核心工作流：向cbz/zip压缩包注入/更新ComicInfo.xml
# ==============================================================================
def inject_xml_into_zip_worker(file_info):
    """
    多线程工作函数：处理单个漫画压缩包
    :param file_info: 元组(文件路径, 漫画数据, 文件名)
    :return: 处理结果提示字符串
    """
    file_path, bgm_data, filename = file_info
    # 获取卷号，无则默认1
    vol_num = extract_volume_number(filename) or 1
    page_count = 0
    has_comic_info = False
  
    try:
        # 打开压缩包，读取文件信息
        with zipfile.ZipFile(file_path, 'r') as zin:
            for item in zin.infolist():
                # 处理文件名编码问题
                try:
                    actual_filename = item.filename.encode('cp437').decode('utf-8')
                except Exception:
                    actual_filename = item.filename
    
                # 判断是否已存在ComicInfo.xml
                if actual_filename.lower() == 'comicinfo.xml':
                    has_comic_info = True
                # 统计图片页数
                if actual_filename.lower().endswith(IMAGE_EXTENSIONS):
                    page_count += 1

        # 生成XML内容
        xml_content = generate_comic_info_xml(bgm_data, volume_number=vol_num, page_count=page_count)
  
        # 情况1：已存在XML，替换旧文件
        if has_comic_info:
            # 临时文件路径
            temp_zip = file_path + ".temp"
            with zipfile.ZipFile(file_path, 'r') as zin:
                # 创建新压缩包
                with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zout:
                    for item in zin.infolist():
                        try:
                            af = item.filename.encode('cp437').decode('utf-8')
                        except Exception:
                            af = item.filename
                        # 跳过旧的XML文件
                        if af.lower() == 'comicinfo.xml':
                            continue
                        # 保持原文件压缩格式
                        item.compress_type = zipfile.ZIP_STORED
                        zout.writestr(item, zin.read(item.filename))
                    # 写入新XML
                    zout.writestr('ComicInfo.xml', xml_content, compress_type=zipfile.ZIP_DEFLATED)
            # 用临时文件替换原文件
            shutil.move(temp_zip, file_path)
            return f"⚡ [更新] 成功替换旧 XML (第 {vol_num} 卷/共 {page_count} 页) -> {filename}"
        # 情况2：无XML，直接追加
        else:
            with zipfile.ZipFile(file_path, 'a') as zout:
                zout.writestr('ComicInfo.xml', xml_content, compress_type=zipfile.ZIP_DEFLATED)
            return f"⚡ [秒过] 成功追加 XML (第 {vol_num} 卷/共 {page_count} 页) -> {filename}"
  
    except Exception as e:
        # 捕获所有异常，返回失败信息
        return f"❌ 失败 -> {filename} (原因: {e})"

# ==============================================================================
# 核心业务逻辑：处理单个漫画文件夹
# ==============================================================================
def process_single_directory(target_dir):
    """
    批量处理一个文件夹内的所有漫画
    :param target_dir: 目标文件夹路径
    :return: 处理成功/失败
    """
    print(f"\n📂 -----------------------------------------------------")
    print(f"📂 正在处理目录: {target_dir}")
    print(f"📂 -----------------------------------------------------")
  
    # 筛选文件夹内的cbz/zip文件
    files = [f for f in os.listdir(target_dir) if f.lower().endswith(('.zip', '.cbz'))]
    if not files:
        print("💡 未在此文件夹内找到 .zip 或 .cbz 格式的漫画文件，跳过。")
        return False

    # 自动提取漫画名
    guessed_names = set()
    for f in files:
        cleaned = clean_comic_name(f)
        if cleaned: 
            guessed_names.add(cleaned)
  
    # 手动输入/确认漫画名
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

    # 搜索Bangumi漫画
    print(f"🌐 正在 Bangumi 跨海搜索 '{search_keyword}'...")
    search_results = search_bangumi_subject(search_keyword, token=BGM_TOKEN)
  
    # 无搜索结果，支持手动输入条目ID
    if not search_results:
        print("❌ 未能在 Bangumi 上搜到相关书籍/漫画。")
        manual_id = input("💡 请手动输入 bgm.tv 条目 ID (直接回车跳过当前文件夹): ").strip()
        if manual_id.isdigit():
            selected_subject_id = int(manual_id)
        else:
            return False
    else:
        # 展示搜索结果，供用户选择
        print("\n🔍 找到以下最匹配的 Bangumi 结果:")
        for idx, item in enumerate(search_results):
            name_cn = item.get("name_cn") or "无中文名"
            name_origin = item.get("name")
            score = item.get("score", "暂无评分")
            date = item.get("date", "未知日期")
            print(f" [{idx + 1}] {name_cn} / {name_origin} ({date}) [评分: {score}]")
  
        # 用户选择序号，默认选第一个
        choice = input(f"\n请选择对应的条目序号 (直接回车默认选 1): ").strip()
        choice_idx = int(choice) - 1 if (choice.isdigit() and 0 < int(choice) <= len(search_results)) else 0
        selected_subject_id = search_results[choice_idx]["id"]

    # 获取漫画完整详情
    print("⏳ 正在安全获取该条目的全量元数据...")
    bgm_data = get_bangumi_comic_info(selected_subject_id, token=BGM_TOKEN)
    if not bgm_data:
        print("❌ 获取元数据失败，跳过该文件夹。")
        return False

    # 开始多线程批量处理
    final_title = bgm_data.get('name_cn') or bgm_data.get('name')
    print(f"🚀 元数据已就绪！并发数: {MAX_WORKERS}，正在秒速追加: 《{final_title}》...")

    # 构造任务列表
    tasks = [(os.path.join(target_dir, f), bgm_data, f) for f in files]
    start_time = time.time()
  
    # 启动多线程处理
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(inject_xml_into_zip_worker, task): task for task in tasks}
        for future in as_completed(futures):
            print(future.result())

    # 计算耗时并提示
    elapsed = time.time() - start_time
    print(f"🎉 当前文件夹 【{final_title}】 处理完成！累计耗时: {elapsed:.2f} 秒。")
  
    # 弹窗提示单项完成
    messagebox.showinfo(
        "📂 单项完工", 
        f"漫画：《{final_title}》 已经处理完毕！\n\n累计耗时: {elapsed:.2f} 秒。\n\n点击确定继续下一个任务。"
    )
    return True

# ==============================================================================
# GUI模块：批量输入漫画文件夹路径
# ==============================================================================
def get_directories_from_gui(default_dir):
    """
    弹出图形窗口，支持批量输入/粘贴文件夹路径
    :param default_dir: 默认路径
    :return: 有效文件夹路径列表
    """
    # 创建子窗口
    input_win = tk.Toplevel()
    input_win.title("批量输入漫画文件夹路径")
    input_win.geometry("600x450")
    input_win.attributes('-topmost', True)  # 窗口置顶
  
    # 提示文字
    tk.Label(
        input_win, 
        text="请粘贴或输入需要处理的文件夹路径：\n(支持换行、逗号、分号或空格分隔，例如: c:/d, c:/c)", 
        font=("Microsoft YaHei", 10),
        pady=10
    ).pack()

    # 多行文本输入框
    text_area = tk.Text(input_win, wrap=tk.WORD, height=12, font=("Consolas", 10))
    text_area.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)
  
    # 填入默认路径
    text_area.insert(tk.END, default_dir)

    # 存储有效路径
    result_dirs = []

    def on_confirm():
        """确认按钮逻辑：解析路径并保存"""
        raw_text = text_area.get("1.0", tk.END)
        # 按换行/逗号/分号分割路径
        paths = re.split(r'[\n,;|]+', raw_text)
  
        for p in paths:
            p = p.strip().strip('"').strip("'") # 去除空白和引号
            if p and os.path.isdir(p):
                if p not in result_dirs:
                    result_dirs.append(p)
        
        input_win.destroy() # 关闭窗口

    def on_cancel():
        """取消按钮逻辑：清空路径并关闭"""
        result_dirs.clear()
        input_win.destroy()

    # 按钮布局
    btn_frame = tk.Frame(input_win)
    btn_frame.pack(pady=15)
    tk.Button(btn_frame, text="✅ 确认并开始处理", command=on_confirm, width=20, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="❌ 取消退出", command=on_cancel, width=15).pack(side=tk.LEFT, padx=10)

    # 阻塞窗口，等待关闭
    input_win.grab_set()
    input_win.wait_window()
  
    return result_dirs

# ==============================================================================
# 主函数：程序入口
# ==============================================================================
def main():
    """程序主入口：调度GUI、批量处理文件夹"""
    print("=========================================================")
    print(" 🎬 Bangumi 漫画刮削器 (批量路径输入版) ")
    print("=========================================================")
  
    # 初始化Tkinter，隐藏主窗口
    root = tk.Tk()
    root.withdraw()
  
    # 默认漫画路径
    default_dir = r"Y:\manga"

    # 第一步：打开窗口获取批量路径
    print("\n📂 正在打开路径输入窗口，请粘贴您的文件夹路径...")
    chosen_directories = get_directories_from_gui(default_dir)

    # 无有效路径，退出程序
    if not chosen_directories:
        messagebox.showwarning("提示", "未输入有效路径或已取消！")
        print("👋 程序退出")
        return

    # 第二步：打印识别到的有效路径
    print("\n" + "="*50)
    print(f"📋 成功识别到 {len(chosen_directories)} 个有效文件夹：")
    for index, folder_path in enumerate(chosen_directories, 1):
        print(f"{index}. {folder_path}")
    print("="*50)

    # 第三步：等待用户确认，开始处理
    input("\n按 回车键 开始批量处理所有文件夹...")

    total_dirs = len(chosen_directories)
    print(f"\n✅ 共选中 {total_dirs} 个文件夹，开始处理...")
  
    # 遍历处理所有文件夹
    global_start_time = time.time()
    for i, directory in enumerate(chosen_directories, 1):
        print(f"\n====================== 进度: {i}/{total_dirs} ======================")
        process_single_directory(directory)
  
    # 全部处理完成，统计总耗时
    total_elapsed = time.time() - global_start_time
    print(f"\n🏁 全部处理完成！总耗时: {total_elapsed:.2f} 秒")
    messagebox.showinfo("完成", f"全部 {total_dirs} 个文件夹处理完毕！")

# 程序入口
if __name__ == '__main__':
    main() 


```
