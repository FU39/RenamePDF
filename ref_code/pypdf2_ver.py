import os
import shutil
from PyPDF2 import PdfReader
import re


def process_pdf_title(paper_title):
    # 在这里对标题进行处理，去除特殊字符
    rstr = r'[\/\\\:\*\?\"\<\>\|\s]'  # '/ \ : * ? " < > | \s'
    double_underscore = '__'
    res_title = re.sub(rstr, "_", paper_title)  # 替换为下划线
    res_title = re.sub(double_underscore, "_", res_title)  # 将两个下划线替换为一个下划线
    return res_title


def copy_pdfs_with_processed_titles(src_dir, des_dir):
    if not os.path.exists(des_dir):
        os.makedirs(des_dir)

    name_counter = {}  # 用于保存文件名及其对应的计数器

    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".pdf"):
                pdf_path = os.path.join(root, file).replace("\\", "/")
                try:
                    with open(pdf_path, "rb") as pdf_file:
                        pdf_reader = PdfReader(pdf_file)
                        meta = pdf_reader.metadata
                    paper_title = meta.title
                    if not paper_title:
                        # paper_title = "none"
                        raise Exception

                    # 处理标题并构建新的文件名
                    processed_title = process_pdf_title(paper_title)
                    new_pdf_name = f"{processed_title}.pdf"

                    # 如果文件名已经出现过，则加上计数器后缀
                    if new_pdf_name in name_counter:
                        name_counter[new_pdf_name] += 1
                        new_pdf_name = f"{processed_title}_{name_counter[new_pdf_name]}.pdf"
                    else:
                        name_counter[new_pdf_name] = 1

                    # 将文件名编码为GBK，以避免编码问题，并构建新文件的完整路径
                    new_pdf_name = new_pdf_name.encode("gbk", "ignore").decode("gbk")
                    new_pdf_path = os.path.join(des_dir, new_pdf_name).replace("\\", "/")

                    # 复制PDF文件到目标目录，并打印提示信息
                    shutil.copy2(pdf_path, new_pdf_path)
                    print(f"Copied '{file}' to '{new_pdf_name}'")
                except Exception as e:
                    # 处理异常情况，如无法打开PDF文件等
                    print(f"Error processing '{file}': {e}")


if __name__ == "__main__":
    src_dir = "./source"
    src_dir = src_dir.replace("\\", "/")
    des_dir = "./result"

    # 执行复制PDF文件并处理标题的函数
    copy_pdfs_with_processed_titles(src_dir, des_dir)
