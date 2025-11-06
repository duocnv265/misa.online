import os
import fitz  # PyMuPDF
from pathlib import Path
from PIL import Image
import html

# ==== CẤU HÌNH ====
ROOT = Path(r"C:\Users\lenovo\OneDrive\Máy tính\misa\hoc-online-demo\misa.online")
PDF_DIR = ROOT / "pdf"
IMG_DIR = ROOT / "img"
AUDIO_DIR = ROOT / "audio"
OUTPUT_DIR = ROOT
NUM_BAI = 40
# ===================

IMG_DIR.mkdir(exist_ok=True)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bài {num} - Học Online</title>
<style>
body {{font-family: Arial,sans-serif;background:#f9f9f9;margin:0;padding:10px;color:#333;}}
.container {{max-width:900px;margin:auto;background:#fff;padding:20px;border-radius:10px;box-shadow:0 2px 5px rgba(0,0,0,0.1);}}
a.back {{display:inline-block;margin-bottom:15px;text-decoration:none;color:#007bff;}}
h1,h2 {{color:#222;}}
audio {{width:100%;margin:8px 0;}}
img.lesson {{width:100%;border-radius:10px;margin:10px 0;}}
.vocab {{background:#f1f3f5;padding:15px;border-radius:8px;white-space:pre-wrap;}}
.missing {{color:#888;font-style:italic;}}
</style>
</head>
<body>
<div class="container">
<a href="index.html" class="back">⬅ Quay lại danh sách</a>
<h1>Bài {num}</h1>

<h2>🔊 Nghe bài học</h2>
{audio_main}

<h2>🎧 Nghe từ mới</h2>
{audio_tumoi}

<h2>📖 Bài học chính</h2>
{lesson_image}

<h2>📘 Từ mới mở rộng</h2>
<div class="vocab">{vocab_text}</div>

</div>
</body>
</html>"""

def pdf_to_image(pdf_path, jpg_path):
    """Chuyển toàn bộ PDF thành 1 ảnh JPG (ghép dọc)."""
    doc = fitz.open(str(pdf_path))
    images = []
    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # zoom 2x
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    doc.close()

    if not images:
        return False

    if len(images) == 1:
        images[0].save(jpg_path, "JPEG", quality=90)
    else:
        # ghép dọc
        widths = [im.width for im in images]
        heights = [im.height for im in images]
        total_height = sum(heights)
        max_width = max(widths)
        combined = Image.new("RGB", (max_width, total_height), (255,255,255))
        y = 0
        for im in images:
            combined.paste(im, (0, y))
            y += im.height
        combined.save(jpg_path, "JPEG", quality=90)
    return True

def extract_text_from_pdf(pdf_path):
    """Trích toàn bộ text từ PDF (từ mới)."""
    try:
        doc = fitz.open(str(pdf_path))
    except Exception as e:
        print(f"Lỗi mở {pdf_path}: {e}")
        return "(Không đọc được file PDF)"
    text_parts = []
    for page in doc:
        txt = page.get_text("text").strip()
        if txt:
            text_parts.append(txt)
    doc.close()
    text = "\n\n".join(text_parts).strip()
    return html.escape(text) if text else "(Không có nội dung)"

def create_html(bai_num):
    print(f"→ Tạo bai{bai_num}.html")

    pdf_baihoc = PDF_DIR / f"bai{bai_num}.pdf"
    pdf_tumoi = PDF_DIR / f"bai{bai_num}_tumoi.pdf"
    jpg_path = IMG_DIR / f"bai{bai_num}.jpg"

    # tạo ảnh nếu chưa có
    if pdf_baihoc.exists():
        if not jpg_path.exists():
            pdf_to_image(pdf_baihoc, jpg_path)
            print(f"  ✔ Đã tạo {jpg_path.name}")
    else:
        print(f"⚠ Không tìm thấy {pdf_baihoc}")

    # phần từ mới
    vocab_text = extract_text_from_pdf(pdf_tumoi) if pdf_tumoi.exists() else "(Không tìm thấy PDF từ mới)"

    # phần audio
    audio_main = AUDIO_DIR / f"bai{bai_num}.mp3"
    audio_tumoi = AUDIO_DIR / f"bai{bai_num}_tumoi.mp3"
    audio_main_html = f'<audio controls><source src="audio/{audio_main.name}" type="audio/mpeg"></audio>' if audio_main.exists() else '<p class="missing">(Không có file audio bài học)</p>'
    audio_tumoi_html = f'<audio controls><source src="audio/{audio_tumoi.name}" type="audio/mpeg"></audio>' if audio_tumoi.exists() else '<p class="missing">(Không có file audio từ mới)</p>'

    lesson_image = f'<img class="lesson" src="img/{jpg_path.name}" alt="Bài {bai_num}">' if jpg_path.exists() else '<p class="missing">(Chưa có ảnh bài học)</p>'

    html_text = HTML_TEMPLATE.format(
        num=bai_num,
        audio_main=audio_main_html,
        audio_tumoi=audio_tumoi_html,
        lesson_image=lesson_image,
        vocab_text=vocab_text
    )

    (OUTPUT_DIR / f"bai{bai_num}.html").write_text(html_text, encoding="utf-8")
    print(f"  ✅ bai{bai_num}.html created")

def create_index():
    items = [f'<li><a href="bai{i}.html">Bài {i}</a></li>' for i in range(1, NUM_BAI+1)]
    html_index = f"""<!DOCTYPE html>
<html lang="vi"><head><meta charset="utf-8">
<title>Danh sách bài học</title>
<style>body{{font-family:Arial,sans-serif;background:#fafafa;padding:20px;}}
ol{{max-width:400px;margin:auto;}}li{{margin:10px 0;}}
a{{text-decoration:none;color:#007bff;font-weight:600;}}</style></head>
<body><h1>📘 Danh sách bài học</h1><ol>{''.join(items)}</ol></body></html>"""
    (OUTPUT_DIR / "index.html").write_text(html_index, encoding="utf-8")
    print("✔ index.html created")

def main():
    create_index()
    for i in range(1, NUM_BAI + 1):
        create_html(i)
    print("🏁 Hoàn tất!")

if __name__ == "__main__":
    main()
