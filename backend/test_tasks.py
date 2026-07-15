import sys
sys.path.insert(0, '/app')
from pathlib import Path
from app.tasks.merge import merge_pdfs
from app.tasks.split import split_pdf
from app.tasks.rotate import rotate_pdf
from app.tasks.compress import compress_pdf
from app.tasks.convert import pdf_to_jpg, jpg_to_pdf
from app.tasks.security import protect_pdf, unlock_pdf
from app.config import get_settings
import traceback

settings = get_settings()
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.RESULT_DIR).mkdir(parents=True, exist_ok=True)

dummy_pdf = Path(settings.UPLOAD_DIR) / "dummy.pdf"
with open(dummy_pdf, "wb") as f:
    f.write(b'%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF')

dummy_jpg = Path(settings.UPLOAD_DIR) / "dummy.jpg"
with open(dummy_jpg, "wb") as f:
    f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\xff\xd9')

tests = [
    ("merge", merge_pdfs, [[str(dummy_pdf), str(dummy_pdf)]]),
    ("split", split_pdf, [str(dummy_pdf), "all"]),
    ("rotate", rotate_pdf, [str(dummy_pdf), 90]),
    ("compress", compress_pdf, [str(dummy_pdf), "recommended"]),
    ("pdf_to_jpg", pdf_to_jpg, [str(dummy_pdf), 150]),
    ("jpg_to_pdf", jpg_to_pdf, [[str(dummy_jpg)]]),
    ("protect", protect_pdf, [str(dummy_pdf), "password123"]),
    ("unlock", unlock_pdf, [str(dummy_pdf), "password123"])
]

for name, task, args in tests:
    print(f"Testing {name}...")
    try:
        res = task.apply(args=args)
        if res.failed():
            print(f"[{name}] FAILED: {res.traceback}")
        else:
            print(f"[{name}] OK: {res.result}")
    except Exception as e:
        print(f"[{name}] CRASH: {traceback.format_exc()}")
