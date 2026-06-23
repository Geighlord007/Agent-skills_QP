#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""压缩大图片 - 只压缩 MVIMG/IMG 开头的文件，其他不动"""
import os, sys
from PIL import Image

MAX_DIM = 1024  # 最大边 1024px
QUALITY = 60    # JPEG 质量 60

def compress_image(src_path):
    """压缩单张图片，保持宽高比"""
    try:
        img = Image.open(src_path)
        
        # 检查是否需要压缩
        w, h = img.size
        max_dim = max(w, h)
        if max_dim <= MAX_DIM and img.format != 'JPEG':
            # 不需要压缩且不是 JPEG，直接返回
            return False
        
        # 计算新尺寸
        if w >= h:
            new_w = MAX_DIM
            new_h = int(h * MAX_DIM / w)
        else:
            new_h = MAX_DIM
            new_w = int(w * MAX_DIM / h)
        
        # 缩放
        if img.size != (new_w, new_h):
            img = img.resize((new_w, new_h), Image.LANCZOS)
        
        # 保存为 JPEG
        img = img.convert('RGB')
        img.save(src_path, 'JPEG', quality=QUALITY, optimize=True)
        return True
    except Exception as e:
        print(f"  [error] {src_path}: {e}")
        return False

def process_folder(folder):
    """处理一个文件夹，只压缩 MVIMG/IMG 开头的大文件"""
    if not os.path.isdir(folder):
        return
    
    files = sorted(os.listdir(folder))
    compressed = 0
    skipped = 0
    
    for f in files:
        fpath = os.path.join(folder, f)
        if not os.path.isfile(fpath):
            continue
        
        # 只处理 MVIMG/IMG 开头的大文件
        if f.startswith(('MVIMG', 'IMG')) and os.path.getsize(fpath) > 500 * 1024:  # > 500KB
            orig_size = os.path.getsize(fpath)
            if compress_image(fpath):
                new_size = os.path.getsize(fpath)
                ratio = new_size / orig_size * 100
                print(f"  {f}: {orig_size//1024}KB → {new_size//1024}KB ({ratio:.0f}%)")
                compressed += 1
            else:
                skipped += 1
        else:
            skipped += 1
    
    return compressed, skipped

def process_all(base_folder):
    """处理所有子文件夹"""
    if not os.path.isdir(base_folder):
        print(f"文件夹不存在: {base_folder}")
        return
    
    subfolders = sorted([d for d in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, d))])
    
    total_compressed = 0
    for subfolder in subfolders:
        subpath = os.path.join(base_folder, subfolder)
        print(f"\n处理: {subfolder}")
        c, s = process_folder(subpath)
        if c:
            total_compressed += c
    
    print(f"\n完成！共压缩 {total_compressed} 个文件")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        base = sys.argv[1]
    else:
        base = input("输入图片文件夹路径: ").strip().strip('"')
    
    process_all(base)
