import fitz  # PyMuPDF
import zipfile
import time
import os
import io  # 👈 核心：引入 Python 内存流组件
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
            output = subprocess.check_output("wmic OS get FreePhysicalMemory", shell=True).decode()
            return int(output.strip().split('\n')[-1].strip()) // 1024
        elif system == "Linux":
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if 'MemAvailable' in line:
                        return int(line.split()[1]) // 1024
        elif system == "Darwin":
            return 4096  # macOS 默认分配一个较为宽松的保守值
    except Exception:
        pass
    return 2048

def get_optimal_workers(total_files):
    """
    🧠 智能识别系统环境，自动计算最优进程数
    """
    logical_cores = os.cpu_count() or 4
    max_cpu_workers = max(1, min(int(logical_cores * 0.8), 12))
    
    # 💡 优化：由于引入了纯内存提取，单个进程需要同时在内存中容纳原 PDF 和新 CBZ
    # 保守估计每个进程需要 800MB 内存，防止高并发时内存溢出
    available_mb = get_available_memory_mb()
    max_memory_workers = max(1, int(available_mb / 800))
    
    file_workers = total_files
    optimal = min(file_workers, max_cpu_workers, max_memory_workers)
    
    return optimal, logical_cores, available_mb

def process_comic_pdf(pdf_path, output_dir, area_threshold):
    """处理单个漫画 PDF：全内存提取与打包，最后一次性落盘"""
    cbz_path = output_dir / f"{pdf_path.stem}.cbz"
    
    if cbz_path.exists():
        return f"⏭️ 跳过 (已存在): {pdf_path.name}"

    try:
        # 1. ⚡ 磁盘 I/O (读)：一次性将整个 PDF 读入内存
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
            
        # 将内存字节流喂给 PyMuPDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        total_pages = len(doc)
        extracted_count = 0
        
        # 2. 🧠 纯内存操作：开辟内存缓冲区充当虚拟 ZIP 硬盘
        memory_zip_stream = io.BytesIO()
        
        # 在内存流中直接构建 ZIP/CBZ 包
        with zipfile.ZipFile(memory_zip_stream, 'w', zipfile.ZIP_STORED) as cbz:
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
                
                # 提取符合阈值的大图
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
                            # 写入内存中的加密/打包区，没有任何磁盘读写延迟
                            cbz.writestr(arcname, image_bytes)
                            extracted_count += 1
                    except Exception:
                        continue
        
        doc.close()
        
        # 3. ⚡ 磁盘 I/O (写)：一卷漫画全部打包完成后，一次性将内存里的 CBZ 倾倒进磁盘
        if extracted_count > 0:
            final_cbz_bytes = memory_zip_stream.getvalue()
            with open(cbz_path, 'wb') as f:
                f.write(final_cbz_bytes)
        
        if extracted_count < total_pages * 0.5 and total_pages > 2:
            return f"⚠️ 提取较少: {pdf_path.name} ({extracted_count}/{total_pages}页) 可能是碎图PDF"
            
        return f"✅ 成功 (纯内存重构): {pdf_path.name} -> {cbz_path.name} ({extracted_count}页)"
        
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
    
    workers, cpu_cores, mem_mb = get_optimal_workers(len(pdfs))
    
    print(f"\n🔍 环境识别: CPU {cpu_cores}核 | 可用内存 {mem_mb}MB | 待处理 {len(pdfs)} 个文件")
    print(f"⚙️ 智能分配: 自动开启 {workers} 个并发进程 (内存自适应防卡顿)")
    print(f"⚙️ 过滤阈值: {AREA_THRESHOLD * 100:.0f}%")
    start_time = time.time()
    
    process_func = partial(process_comic_pdf, output_dir=output_dir, area_threshold=AREA_THRESHOLD)
    
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(process_func, pdf) for pdf in pdfs]
        for future in as_completed(futures):
            print(future.result())
    
    elapsed = time.time() - start_time
    print(f"\n🎉 全部完成！共处理 {len(pdfs)} 本漫画 | 总耗时: {elapsed:.2f}秒")

if __name__ == "__main__":
    print("=========================================================")
    print(" 📚 漫画 PDF 转 CBZ 极速工具 (纯内存流加速版)")
    print("=========================================================")
    
    input_str = input("📂 请输入漫画 PDF 所在目录 (回车默认为当前目录): ").strip()
    input_dir = Path(input_str or ".").resolve()
    
    if not input_dir.is_dir():
        print(f"❌ 错误: 目录不存在 -> {input_dir}")
        exit(1)
        
    output_dir = input_dir / "CBZ_Output"
    output_dir.mkdir(exist_ok=True)
    
    batch_convert_comics(input_dir, output_dir)
    
    print(f"\n📂 CBZ 文件已输出至: {output_dir.resolve()}")