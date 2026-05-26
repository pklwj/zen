# 多线程
```python
import fitz
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time
import zipfile
import shutil
import os
from functools import partial
import threading

def process_pdf(pdf_path, output_dir):
    """处理单个PDF文件，提取所有图片"""
    output_dir = output_dir / pdf_path.stem
    output_dir.mkdir(exist_ok=True)
    
    try:
        doc = fitz.open(pdf_path)
        write_tasks = []
        
        for page_num, page in enumerate(doc):
            image_list = page.get_images(full=True)
            for img_index, img_info in enumerate(image_list, 1):
                xref = img_info[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                img_path = output_dir / f"{page_num+1}_{img_index}.{image_ext}"
                write_tasks.append((img_path, image_bytes))
        
        # 批量写入
        for path, data in write_tasks:
            path.write_bytes(data)
            
        doc.close()
        return True
        
    except Exception as e:
        print(f"✗ 错误处理 {pdf_path.name}: {e}")
        return False

def batch_extract(input_dir, output_dir, workers=None):
    """批量处理目录中的所有PDF文件"""
    pdfs = list(input_dir.glob("*.pdf"))
    if not pdfs:
        print("未找到PDF文件")
        return
    
    if workers is None:
        workers = min(len(pdfs), max(1, os.cpu_count() - 1))
    
    print(f"⚙️ 使用 {workers} 个进程处理 {len(pdfs)} 个PDF文件")
    start_time = time.time()
    
    with ProcessPoolExecutor(max_workers=workers) as executor:
        process_func = partial(process_pdf, output_dir=output_dir)
        results = list(executor.map(process_func, pdfs))
    
    success_count = sum(results)
    elapsed = time.time() - start_time
    
    print(f"\n✅ 完成: {success_count}/{len(pdfs)} 成功 | 耗时: {elapsed:.2f}秒")
    print(f"📂 输出目录: {output_dir.resolve()}")
    
    return success_count > 0

def zip_folder(folder_path, compression=zipfile.ZIP_STORED):
    """将单个文件夹压缩为ZIP文件并删除原始文件夹（针对图片优化）"""
    parent_dir = folder_path.parent
    zip_path = parent_dir / f"{folder_path.name}.zip"
    
    try:
        print(f"开始压缩: {folder_path.name}")
        start_time = time.time()
        
        # 针对图片文件的特殊处理
        # 使用STORED模式（不压缩），因为图片本身已是压缩格式
        with zipfile.ZipFile(zip_path, 'w', compression) as zipf:
            for file in folder_path.rglob("*"):
                arcname = file.relative_to(parent_dir)
                # 对于图片文件，使用存储模式
                if file.suffix.lower() in ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'):
                    zipf.write(file, arcname, compress_type=zipfile.ZIP_STORED)
                # 其他文件仍使用默认压缩
                else:
                    zipf.write(file, arcname)
        
        elapsed = time.time() - start_time
        print(f"✅ 压缩完成: {zip_path} | 耗时: {elapsed:.2f}秒")
        
        # 删除原始文件夹
        shutil.rmtree(folder_path)
        print(f"🗑️ 已删除原始文件夹: {folder_path}")
        
        return True
    except Exception as e:
        print(f"✗ 压缩 {folder_path.name} 时出错: {e}")
        return False

def batch_zip_folders(folders, workers=None):
    """并行压缩多个文件夹（针对图片优化）"""
    if not folders:
        print("没有找到需要压缩的子文件夹")
        return
    
    if workers is None:
        # 图片压缩主要受I/O限制，使用线程池更合适
        workers = max(1, os.cpu_count() * 2)
    
    print(f"⚙️ 使用 {workers} 个线程并行压缩 {len(folders)} 个文件夹")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(zip_folder, folders))
    
    success_count = sum(results)
    elapsed = time.time() - start_time
    
    print(f"\n✅ 压缩完成: {success_count}/{len(folders)} 成功 | 耗时: {elapsed:.2f}秒")
    return success_count > 0

if __name__ == "__main__":
    print("PDF图片批量提取工具")
    input_dir = Path(input("源目录: ").strip() or ".").resolve()
    output_dir = Path(input("输出目录: ").strip() or input_dir / "images").resolve()
    output_dir.mkdir(exist_ok=True)
    
    success = batch_extract(input_dir, output_dir)
    
    if success:
        print("\n开始并行压缩子文件夹...")
        subfolders = [f for f in output_dir.iterdir() if f.is_dir()]
        
        if batch_zip_folders(subfolders):
            print("\n🎉 所有文件夹已压缩并清理完毕!")
```
