import os
import json

if __name__ == "__main__":
    des_dir = "./result"

    with open("skip_files.json", "r", encoding="utf-8") as f:
        skip_files = json.load(f)

    root_dirs = list(skip_files.keys())

    for root_dir in root_dirs:
        sub_skip_files = list(skip_files[root_dir].keys())
        root, _, files = next(os.walk(root_dir))
        for file in files:
            if file.endswith(".pdf"):
                if file not in sub_skip_files:
                    pdf_path = os.path.join(root, file).replace("\\", "/")
                    # 删除执行成功的文件
                    try:
                        os.remove(pdf_path)
                        print(f"已删除文件: {pdf_path}")
                    except OSError as e:
                        print(f"无法删除文件: {e}")
