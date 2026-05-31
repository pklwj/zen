import fitz  # PyMuPDF
import zipfile
import time
import os
import shutil
import platform
import subprocess
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial

# ==============================================================================
# 提取配置区
# ==============================================================================
# 面积过滤阈值：只提取面积占当前页面总面积 60% 以上的图片（自动过滤小图标、水印）
AREA_THRESHOLD = 0.6 

def get_available_memory_mb():
    """自动识别系统当前可用内存 (MB)"""
    try:
        system = platform.system()
        if system == "Windows":
            # Windows: 使用 wmic 获取可用内存 (字节)
            output = subprocess.check_output("wmic OS get FreePhysicalMemory", shell=True).decode()
            return int(output.strip().split('\n')[-1].strip()) // 1024
        elif system == "Linux":
            # Linux: 读取 /proc/meminfo
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if 'MemAvailable' in line:
                        return int(line.split()[1]) // 1024
        elif system == "Darwin":
            # macOS: 使用 vm_stat (粗略估算)
            output = subprocess.check_output("vm_stat", shell=True).decode()
            for line in output.split('\n'):
                if "Pages free" in line or "Pages inactive" in line:
                    pass # macOS 内存管理较复杂，这里给个保守默认值
            return 2048 
    except Exception:
        pass
    return 2048  # 如果识别失败，保守假设有 2GB 可用内存

def get_optimal_workers(total_files):
    """
    🧠 智能识别系统环境，自动计算最优进程数
    """
    # 1. 自动识别 CPU 核心数
    logical_cores = os.cpu_count() or 4
    # 限制最大 CPU 占用，防止电脑卡死（最多使用 80% 的核心，且上限为 12）
    max_cpu_workers = max(1, min(int(logical_cores * 0.8), 12))
    
    # 2. 自动识别可用内存 (防止内存撑爆)
    available_mb = get_available_memory_mb()
    # 提取 PDF 和打包 ZIP 比较吃内存，保守估计每个进程需要 500MB 内存
    max_memory_workers = max(1, int(available_mb / 500))
    
    # 3. 自动识别文件数量 (只有3个文件就只开3个进程)
    file_workers = total_files
    
    # 4. 取三者的最小值，得出最完美的并发数
    optimal = min(file_workers, max_cpu_workers, max_memory_workers)
    
    return optimal, logical_cores, available_mb

def process_comic_pdf(pdf_path, output_dir, area_threshold):
    """处理单个漫画 PDF：直接提取内嵌的原始图片"""
    cbz_path = output_dir / f"{pdf_path.stem}.cbz"
    
    if cbz_path.exists():
        return f"⏭️ 跳过 (已存在): {pdf_path.name}"

    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        extracted_count = 0
        
        with zipfile.ZipFile(cbz_path, 'w', zipfile.ZIP_STORED) as cbz:
            for page_num in range(total_pages):
                page = doc[page_num]
                page_area = page.rect.width * page.rect.height
                image_list = page.get_images(full=True)
                
                best_img_info = None
                max_img_area = 0
                
                for img_info in image_list:
                    xref = img_info[0]
                    try:
                        img_rects = page.get_image_rects(xref)
                        if not img_rects:
                            continue
                        img_area = sum(rect.width * rect.height for rect in img_rects)
                        if img_area > max_img_area:
                            max_img_area = img_area
                            best_img_info = img_info
                    except Exception:
                        continue
                
                if best_img_info and (max_img_area / page_area) >= area_threshold:
                    xref = best_img_info[0]
                    try:
                        base_image = doc.extract_image(xref)
                        if base_image:
                            image_bytes = base_image["image"]
                            image_ext = base_image["ext"]
                            if image_ext.lower() == "jpeg":
                                image_ext = "jpg"
                            
                            arcname = f"{page_num + 1:04d}.{image_ext}"
                            cbz.writestr(arcname, image_bytes)
                            extracted_count += 1
                    except Exception:
                        continue
        
        doc.close()
        
        if extracted_count < total_pages * 0.5 and total_pages > 2:
            return f"⚠️ 提取较少: {pdf_path.name} ({extracted_count}/{total_pages}页) 可能是碎图PDF"
            
        return f"✅ 成功: {pdf_path.name} -> {cbz_path.name} (原始画质，{extracted_count}页)"
        
    except Exception as e:
        if cbz_path.exists():
            cbz_path.unlink()
        return f"❌ 失败: {pdf_path.name} | {e}"

def batch_convert_comics(input_dir, output_dir):
    """批量处理目录中的所有漫画 PDF"""
    pdfs = list(input_dir.glob("*.pdf"))
    if not pdfs:
        print("💡 未找到 PDF 文件")
        return
    
    # 🧠 自动识别环境并计算最优进程数
    workers, cpu_cores, mem_mb = get_optimal_workers(len(pdfs))
    
    print(f"\n🔍 环境识别: CPU {cpu_cores}核 | 可用内存 {mem_mb}MB | 待处理 {len(pdfs)} 个文件")
    print(f"⚙️ 智能分配: 自动开启 {workers} 个并发进程 (防卡顿·防内存溢出)")
    print(f"⚙️ 过滤阈值: {AREA_THRESHOLD * 100:.0f}% (自动丢弃小图标)")
    start_time = time.time()
    
    process_func = partial(process_comic_pdf, output_dir=output_dir, area_threshold=AREA_THRESHOLD)
    
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(process_func, pdf) for pdf in pdfs]
        for future in as_completed(futures):
            print(future.result())
    
    elapsed = time.time() - start_time
    print(f"\n🎉 全部完成！共处理 {len(pdfs)} 本漫画 | 总耗时: {elapsed:.2f}秒")

if __name__ == "__main__":
    print("="*55)
    print(" 📚 漫画 PDF 转 CBZ 极速工具 (智能自适应·原始画质版)")
    print("="*55)
    
    input_str = input("📂 请输入漫画 PDF 所在目录 (回车默认为当前目录): ").strip()
    input_dir = Path(input_str or ".").resolve()
    
    if not input_dir.is_dir():
        print(f"❌ 错误: 目录不存在 -> {input_dir}")
        exit(1)
        
    output_dir = input_dir / "CBZ_Output"
    output_dir.mkdir(exist_ok=True)
    
    batch_convert_comics(input_dir, output_dir)
    
    print(f"\n📂 CBZ 文件已输出至: {output_dir.resolve()}")