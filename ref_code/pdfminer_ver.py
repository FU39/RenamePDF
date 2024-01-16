from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTAnno


def get_paper_title(file_name):
    pdf_title = ""

    # 标题通常在第一页，故只取第一页
    # page_layout = next(extract_pages(file_name))
    page_layout = next(extract_pages(file_name, page_numbers=[0]))
    for element in page_layout:
        if isinstance(element, LTTextContainer):
            for text_line in element:
                try:
                    text_line_width = text_line.width
                except AttributeError as e:
                    print("AttributeError: {}".format(e))
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
                    if len(pdf_title) == 0:
                        pdf_title = text_line_str.strip("\n")
                    else:
                        pdf_title = "{} {}".format(pdf_title, text_line_str).strip("\n")

    return pdf_title.strip()


if __name__ == '__main__':
    pdf_path = "./source/1710.08005.pdf"
    title = get_paper_title(pdf_path)
    print("title:\n{}".format(title))
