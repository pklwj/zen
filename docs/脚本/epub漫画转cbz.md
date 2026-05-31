```python
import zipfile
import time
import os
import platform
import subprocess
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial
from urllib.parse import unquote

# ==============================================================================
# 提取配置区
# ==============================================================================
# 支持的图片后缀
IMG_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}

def get_available_memory_mb():
    """自动识别系统当前可用内存 (MB)"""
    try:
        system = platform.system()
        if system == "Windows":
            output = subprocess.check_output("wmic OS get FreePhysicalMemory", shell=True).decode()
            return int(output.strip().split('\n')[-1].strip()) // 1024
        elif system == "Linux":
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if 'MemAvailable' in line:
                        return int(line.split()[1]) // 1024
        elif system == "Darwin":
            return 2048 
    except Exception:
        pass
    return 2048

def get_optimal_workers(total_files):
    """🧠 智能识别系统环境，自动计算最优进程数"""
    logical_cores = os.cpu_count() or 4
    max_cpu_workers = max(1, min(int(logical_cores * 0.8), 12))
    available_mb = get_available_memory_mb()
    max_memory_workers = max(1, int(available_mb / 500))
    optimal = min(total_files, max_cpu_workers, max_memory_workers)
    return optimal, logical_cores, available_mb

def get_epub_image_order(epub_zip):
    """
    📖 核心引擎：解析 EPUB 内部结构，获取严格正确的漫画图片顺序
    """
    # 1. 找到 container.xml 获取 OPF 文件路径
    opf_path = None
    if 'META-INF/container.xml' in epub_zip.namelist():
        container_xml = epub_zip.read('META-INF/container.xml').decode('utf-8', errors='ignore')
        match = re.search(r'full-path=["\']([^"\']+\.opf)["\']', container_xml)
        if match:
            opf_path = match.group(1)
    
    # 如果找不到，直接扫描根目录下的 .opf 文件
    if not opf_path:
        for name in epub_zip.namelist():
            if name.endswith('.opf'):
                opf_path = name
                break
                
    if not opf_path:
        return None # 无法解析目录，将启用保底方案

    # 2. 解析 OPF 文件
    opf_content = epub_zip.read(opf_path).decode('utf-8', errors='ignore')
    # 移除 XML 命名空间以简化解析
    opf_content = re.sub(r'\sxmlns="[^"]+"', '', opf_content, count=1)
    root = ET.fromstring(opf_content)
    
    # 建立 manifest 字典 (id -> href)
    manifest = {}
    for item in root.findall('.//manifest/item'):
        manifest[item.get('id')] = item.get('href')
        
    # 获取 OPF 文件所在的目录，用于拼接图片相对路径
    opf_dir = os.path.dirname(opf_path)
    
    # 3. 按照 spine (阅读顺序) 提取图片
    ordered_images = []
    for itemref in root.findall('.//spine/itemref'):
        idref = itemref.get('idref')
        href = manifest.get(idref)
        if not href:
            continue
            
        # 拼接完整路径
        file_path = os.path.join(opf_dir, href).replace('\\', '/')
        
        # 情况 A：spine 直接指向图片 (部分漫画 EPUB 的非标准做法)
        if Path(href).suffix.lower() in IMG_EXTS:
            ordered_images.append(file_path)
            
        # 情况 B：spine 指向 xhtml/html，需要解析里面的 <img> 标签
        elif href.endswith(('.xhtml', '.html', '.htm')):
            if file_path in epub_zip.namelist():
                html_content = epub_zip.read(file_path).decode('utf-8', errors='ignore')
                # 使用正则提取 img src
                img_tags = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
                for img_src in img_tags:
                    # 解码 URL 编码 (如 %20 转为空格)
                    img_src = unquote(img_src)
                    # 拼接图片的绝对路径
                    img_full_path = os.path.join(os.path.dirname(file_path), img_src).replace('\\', '/')
                    # 规范化路径 (处理 ../ 等相对路径)
                    img_full_path = os.path.normpath(img_full_path).replace('\\', '/')
                    ordered_images.append(img_full_path)
                    
    return ordered_images

def process_comic_epub(epub_path, output_dir):
    """处理单个漫画 EPUB：按正确顺序提取图片并打包为 CBZ"""
    cbz_path = output_dir / f"{epub_path.stem}.cbz"
    
    if cbz_path.exists():
        return f"⏭️ 跳过 (已存在): {epub_path.name}"

    try:
        with zipfile.ZipFile(epub_path, 'r') as epub_zip:
            # 获取正确的图片顺序
            ordered_images = get_epub_image_order(epub_zip)
            
            # 保底方案：如果 OPF 解析失败，直接按文件名自然排序提取所有图片
            if not ordered_images:
                all_files = epub_zip.namelist()
                ordered_images = sorted([
                    f for f in all_files 
                    if Path(f).suffix.lower() in IMG_EXTS and not f.startswith('MACOSX')
                ])
                parse_status = "⚠️ 目录解析失败，按文件名盲排"
            else:
                parse_status = "✅ 目录解析成功，严格顺序"
            
            if not ordered_images:
                return f"❌ 失败: {epub_path.name} | 原因: EPUB 内未找到任何图片"

            # 内存直写 CBZ
            with zipfile.ZipFile(cbz_path, 'w', zipfile.ZIP_STORED) as cbz:
                page_num = 1
                for img_path in ordered_images:
                    # 兼容路径大小写和斜杠问题
                    actual_path = next((f for f in epub_zip.namelist() if f.replace('\\', '/') == img_path.replace('\\', '/')), None)
                    
                    if actual_path:
                        ext = Path(actual_path).suffix.lower()
                        if ext == '.jpeg': ext = '.jpg'
                        
                        # 读取原始图片字节流
                        img_bytes = epub_zip.read(actual_path)
                        
                        # 按顺序重命名：0001.jpg, 0002.jpg
                        arcname = f"{page_num:04d}{ext}"
                        cbz.writestr(arcname, img_bytes)
                        page_num += 1
                        
        return f"✅ 成功: {epub_path.name} -> {cbz_path.name} ({parse_status}，共 {page_num - 1} 页)"
        
    except Exception as e:
        if cbz_path.exists():
            cbz_path.unlink()
        return f"❌ 失败: {epub_path.name} | 原因: {e}"

def batch_convert_comics(input_dir, output_dir):
    """批量处理目录中的所有漫画 EPUB"""
    epubs = list(input_dir.glob("*.epub"))
    if not epubs:
        print("💡 未找到 EPUB 文件")
        return
    
    workers, cpu_cores, mem_mb = get_optimal_workers(len(epubs))
    
    print(f"\n🔍 环境识别: CPU {cpu_cores}核 | 可用内存 {mem_mb}MB | 待处理 {len(epubs)} 个文件")
    print(f"⚙️ 智能分配: 自动开启 {workers} 个并发进程 (防卡顿·防内存溢出)")
    start_time = time.time()
    
    process_func = partial(process_comic_epub, output_dir=output_dir)
    
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(process_func, epub) for epub in epubs]
        for future in as_completed(futures):
            print(future.result())
    
    elapsed = time.time() - start_time
    print(f"\n🎉 全部完成！共处理 {len(epubs)} 本漫画 | 总耗时: {elapsed:.2f}秒")

if __name__ == "__main__":
    print("="*55)
    print(" 📚 漫画 EPUB 转 CBZ 极速工具 (智能顺序·内存直写版)")
    print("="*55)
    
    input_str = input("📂 请输入漫画 EPUB 所在目录 (回车默认为当前目录): ").strip()
    input_dir = Path(input_str or ".").resolve()
    
    if not input_dir.is_dir():
        print(f"❌ 错误: 目录不存在 -> {input_dir}")
        exit(1)
        
    output_dir = input_dir / "CBZ_Output"
    output_dir.mkdir(exist_ok=True)
    
    batch_convert_comics(input_dir, output_dir)
    
    print(f"\n📂 CBZ 文件已输出至: {output_dir.resolve()}")
```