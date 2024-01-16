import os
import shutil
import re
import json
from PyPDF2 import PdfReader
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTAnno


def process_title(paper_title):
    # 在这里对标题进行处理，去除特殊字符
    rstr = r'[/\\:*?"<>|\s“”,，]'  # '/ \ : * ? " < > | \s “ ” , ，'
    double_underscore = '__'
    res_title = re.sub(rstr, "_", paper_title)  # 替换为下划线
    res_title = re.sub(double_underscore, "_", res_title)  # 将两个下划线替换为一个下划线
    res_title = res_title.strip("_")  # 去除首尾下划线
    return res_title


def get_title_pdfminer(pdf_path):
    paper_title = ""

    # 标题通常在第一页，故只取第一页
    page_layout = next(extract_pages(pdf_path, page_numbers=[0]))
    for element in page_layout:
        if isinstance(element, LTTextContainer):
            for text_line in element:
                try:
                    text_line_width = text_line.width
                except AttributeError as e:
                    # print("AttributeError: {}".format(e))
                    continue
                if text_line_width < 30:
                    continue
                text_line_str = ""
                is_title = False
                for character in text_line:
                    if isinstance(character, LTChar):
                        text = character.get_text()
                        font_size = character.size
                        # 经验值
                        if font_size > 14.3:
                            is_title = True
                        text_line_str += text
                    elif isinstance(character, LTAnno):
                        text = character.get_text()
                        text_line_str += text
                if is_title:
                    if len(paper_title) == 0:
                        paper_title = text_line_str.strip("\n")
                    else:
                        paper_title = "{} {}".format(paper_title, text_line_str).strip("\n")

    if len(paper_title) == 0:
        return None
    else:
        paper_title = paper_title.strip()  # 去除首尾空格
        return paper_title


def rename_pdfs(src_dir, des_dir):
    name_counter = {}  # 用于保存文件名及其对应的计数器
    error_files = {}  # 用于保存无法处理的文件

    if src_dir.endswith("/"):
        src_folder = src_dir.replace("\\", "/").split("/")[-2]
    else:
        src_folder = src_dir.replace("\\", "/").split("/")[-1]

    for root, _, files in os.walk(src_dir):
        # 排除 EndNote 文件夹
        if root.lower().find("endnote") != -1:
            continue

        root = root.replace("\\", "/")
        if root not in error_files:
            error_files[root] = {}

        try:
            index = root.index(src_folder)
        except ValueError as e:
            print("ValueError: {}".format(e))
            continue
        # 好像并不会出现索引越界，会直接返回空字符串，所以这里不需要处理 IndexError
        # try:
        #     sub_root = root[index + len(src_folder) + 1:]
        # except IndexError as e:
        #     sub_root = ""
        sub_root = root[index + len(src_folder) + 1:]
        sub_des_dir = os.path.join(des_dir, sub_root).replace("\\", "/")

        if not os.path.exists(sub_des_dir):
            os.makedirs(sub_des_dir)

        for file in files:
            if file.endswith(".pdf"):
                pdf_path = os.path.join(root, file).replace("\\", "/")
                try:
                    with open(pdf_path, "rb") as pdf_file:
                        pdf_reader = PdfReader(pdf_file)
                        meta = pdf_reader.metadata
                    paper_title = meta.title
                    # 如果 PDF 文件中没有标题信息，则使用 pdfminer 获取标题
                    if not paper_title or paper_title == "NONE":
                        paper_title = get_title_pdfminer(pdf_path)
                        # 如果 pdfminer 也无法获取标题，则抛出异常
                        if not paper_title:
                            raise Exception("Cannot get title from PDF file")

                    # 处理标题并构建新的文件名
                    processed_title = process_title(paper_title)
                    new_pdf_name = f"{processed_title}.pdf"

                    # 如果文件名已经出现过，则加上计数器后缀
                    if new_pdf_name in name_counter:
                        name_counter[new_pdf_name] += 1
                        new_pdf_name = f"{processed_title}_{name_counter[new_pdf_name]}.pdf"
                    else:
                        name_counter[new_pdf_name] = 1

                    # 将文件名编码为 UTF-8
                    new_pdf_name = new_pdf_name.encode("utf-8", "ignore").decode("utf-8")
                    # 构建新的 PDF 文件路径
                    new_pdf_path = os.path.join(sub_des_dir, new_pdf_name).replace("\\", "/")

                    # 复制 PDF 文件到目标目录，并打印提示信息
                    shutil.copy2(pdf_path, new_pdf_path)
                    print(f"Copied '{file}' to '{new_pdf_name}'")
                except Exception as e:
                    # 处理异常情况，如无法打开 PDF 文件等
                    print("Error processing '{}': {}".format(file, e))
                    if root not in error_files:
                        error_files[root] = {}
                    error_files[root].update({file: {"path": pdf_path, "error": str(e)}})

    return error_files


if __name__ == "__main__":
    src_dir = r"./source"
    src_dir = src_dir.replace("\\", "/")
    des_dir = "./result"
    des_dir = des_dir.replace("\\", "/")

    # 执行复制 PDF 文件并处理标题的函数
    skip_files = rename_pdfs(src_dir, des_dir)
    for key, value in skip_files.items():
        print(key, value, sep=":\n")
    with open("./skip_files.json", "w", encoding="utf-8") as f:
        json.dump(skip_files, f, ensure_ascii=False, indent=4)
