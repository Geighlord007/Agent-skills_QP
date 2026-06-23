#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 V2.3 会议纪要 docx"""
import os, sys, re
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from PIL import Image

def normalize_image(path):
    """用 PIL 重新保存图片，避免 python-docx 的 JPEG 嵌入 bug"""
    try:
        img = Image.open(path)
        img = img.convert('RGB')
        img.save(path, 'JPEG', quality=85)
    except Exception as e:
        print(f"    [warn] normalize失败: {path} - {e}")

def add_heading_bold(doc, text, level=1):
    """添加加粗标题"""
    h = doc.add_heading(level=level)
    h.clear()
    run = h.add_run(text)
    run.bold = True
    if level == 1:
        run.font.size = Pt(14)
    return h

def add_key_point(doc, text):
    """添加加粗要点"""
    p = doc.add_paragraph(style='List Bullet')
    run = p.add_run(text)
    run.bold = True
    return p

def add_summary_paragraph(doc, text):
    """添加普通总结段落"""
    return doc.add_paragraph(text)

def add_image(doc, folder, img_file):
    """添加图片到文档"""
    img_path = os.path.join(folder, img_file)
    if not os.path.exists(img_path):
        return
    normalize_image(img_path)
    try:
        doc.add_picture(img_path, width=Inches(5.5))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    except Exception as e:
        doc.add_paragraph(f"[图片无法嵌入: {img_file}]")

def parse_v3_file(filepath):
    """解析 V3 txt 文件，提取会议总结和公司内容"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 会议总结：## 会议总结 之后，到第一个公司名之前
    meeting_summary = ''
    companies = {}
    
    # 简单分割：找到所有公司名开头的段落
    lines = content.split('\n')
    current_company = None
    current_content = []
    
    for line in lines:
        # 公司名识别（简短，无标点或只有简短描述）
        # 排除会议总结部分
        if '## 会议总结' in line:
            # 之前的是会议总结内容
            meeting_summary = '\n'.join(current_content)
            current_content = []
            continue
        
        # 检查是否是公司标题行（后面跟着演讲人）
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and not stripped.startswith('http') and len(stripped) < 30:
            # 可能是公司名
            if '演讲人' not in stripped and '公司' in stripped or any(x in stripped for x in ['科技', '生物', '大学', '研究院', '平台', '服务']):
                if current_company and current_content:
                    companies[current_company] = '\n'.join(current_content)
                current_company = stripped
                current_content = []
                continue
        
        current_content.append(line)
    
    if current_company and current_content:
        companies[current_company] = '\n'.join(current_content)
    
    return meeting_summary, companies

def create_v23_docx(v3_txt_path, photo_base, output_path):
    """创建 V2.3 docx"""
    doc = Document()
    
    # 标题
    title = doc.add_heading('会议纪要', level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 读取内容
    with open(v3_txt_path, 'r', encoding='utf-8') as f:
        full_content = f.read()
    
    # 分割会议总结和公司内容
    if '## 会议总结' in full_content:
        parts = full_content.split('## 会议总结', 1)
        pre_summary = parts[0]
        after_summary = '## 会议总结' + parts[1]
    else:
        pre_summary = ''
        after_summary = full_content
    
    # 添加会议总结
    if after_summary:
        # 找到第一个公司名之前的部分
        company_markers = ['上海分子之心', '印迹安合', '天鹜科技', '恩和科技', '智峪生科', '杭州瑞欧', '江南大学', '江西富祥', '百开盛', '广发证券', '张江合成生物']
        summary_end = len(after_summary)
        for marker in company_markers:
            idx = after_summary.find(f'\n{marker}')
            if idx > 0 and idx < summary_end:
                summary_end = idx
        
        summary_text = after_summary[:summary_end].strip()
        if summary_text:
            h = doc.add_heading(level=1)
            h.clear()
            h.add_run('会议总结').bold = True
            doc.add_paragraph(summary_text)
    
    # 分割各公司内容
    lines = after_summary.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # 检测公司名
        is_company = False
        company_name = ''
        for marker in company_markers:
            if marker in line and len(line) < 40:
                is_company = True
                company_name = marker
                break
        
        if is_company:
            # 公司标题
            h = doc.add_heading(level=2)
            h.clear()
            run = h.add_run(company_name)
            run.bold = True
            run.font.size = Pt(12)
            
            # 接下来几行是演讲人和内容
            j = i + 1
            while j < len(lines) and j < i + 20:
                next_line = lines[j].strip()
                if not next_line:
                    break
                
                # 检查是否是下一个公司
                next_is_company = False
                for marker in company_markers:
                    if marker in next_line and len(next_line) < 40:
                        next_is_company = True
                        break
                
                if next_is_company:
                    break
                
                # 演讲人行
                if '演讲人' in next_line or '总' in next_line or '教授' in next_line or '总监' in next_line or '经理' in next_line or '副总' in next_line or '负责人' in next_line or 'VP' in next_line:
                    p = doc.add_paragraph()
                    run = p.add_run(next_line)
                    run.italic = True
                elif next_line.startswith('##'):
                    # 子标题
                    h2 = doc.add_heading(level=3)
                    h2.clear()
                    h2.add_run(next_line.replace('##', '').strip()).bold = True
                elif any(x in next_line for x in ['核心亮点', '关键', '要点']):
                    p = doc.add_paragraph()
                    run = p.add_run(next_line)
                    run.bold = True
                elif len(next_line) > 5:
                    doc.add_paragraph(next_line)
                
                j += 1
            
            i = j - 1
        
        i += 1
    
    # 在对应公司下嵌入图片
    # 图片文件夹映射
    photo_map = {
        '上海分子之心': '分子之心',
        '印迹安合': '印迹安合',
        '恩和科技': '恩和科技',
        '天鹜科技': '天鹜科技',
        '智峪生科': '智裕生科',
        '杭州瑞欧': '瑞欧科技',
        '江南大学': '江南大学',
        '江西富祥': '富祥蛋白',
        '百开盛': '百开盛',
        '广发证券': '合成生物学',
        '张江合成生物': '生合万物'
    }
    
    for company, folder_name in photo_map.items():
        folder_path = os.path.join(photo_base, folder_name)
        if os.path.exists(folder_path):
            photos = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            if photos:
                doc.add_paragraph()  # 空行
                for photo in photos[:5]:  # 最多5张
                    add_image(doc, folder_path, photo)
    
    doc.save(output_path)
    print(f'文档已保存: {output_path}')
    return output_path

if __name__ == '__main__':
    v3_txt = r'C:\Users\18294\.openclaw\workspace\v2_all_content_v3.txt'
    photo_base = r'D:\WPS Software\工作文件夹\Claw\会议记录_2026-03-31'
    output = r'D:\WPS Software\工作文件夹\Claw\会议记录_2026-03-31\会议记录_2026-03-31_整理纪要V2.3.docx'
    create_v23_docx(v3_txt, photo_base, output)
