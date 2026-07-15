import os
import time
import requests

API_URL = "http://localhost:8000/api"

def wait_for_job(job_id):
    while True:
        resp = requests.get(f"{API_URL}/jobs/{job_id}")
        data = resp.json()
        status = data.get("status")
        if status == "done":
            print(f"Job {job_id} done!")
            return data.get("download_url")
        elif status == "error":
            raise Exception(f"Job failed: {data.get('error')}")
        time.sleep(0.5)

def test_merge():
    print("Testing Merge...")
    files = [
        ('files', ('test1.pdf', b'%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF', 'application/pdf')),
        ('files', ('test2.pdf', b'%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF', 'application/pdf'))
    ]
    resp = requests.post(f"{API_URL}/tools/merge", files=files)
    if not resp.ok: raise Exception(resp.text)
    wait_for_job(resp.json()["job_id"])

def test_split():
    print("Testing Split...")
    files = {'file': ('test1.pdf', b'%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF', 'application/pdf')}
    resp = requests.post(f"{API_URL}/tools/split", files=files, data={'ranges': 'all'})
    if not resp.ok: raise Exception(resp.text)
    wait_for_job(resp.json()["job_id"])

def test_rotate():
    print("Testing Rotate...")
    files = {'file': ('test1.pdf', b'%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF', 'application/pdf')}
    resp = requests.post(f"{API_URL}/tools/rotate", files=files, data={'angle': 90})
    if not resp.ok: raise Exception(resp.text)
    wait_for_job(resp.json()["job_id"])

def test_compress():
    print("Testing Compress...")
    files = {'file': ('test1.pdf', b'%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF', 'application/pdf')}
    resp = requests.post(f"{API_URL}/tools/compress", files=files, data={'level': 'recommended'})
    if not resp.ok: raise Exception(resp.text)
    wait_for_job(resp.json()["job_id"])

def test_pdf_to_jpg():
    print("Testing PDF to JPG...")
    files = {'file': ('test1.pdf', b'%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF', 'application/pdf')}
    resp = requests.post(f"{API_URL}/tools/pdf-to-jpg", files=files, data={'dpi': 150})
    if not resp.ok: raise Exception(resp.text)
    wait_for_job(resp.json()["job_id"])

def test_jpg_to_pdf():
    print("Testing JPG to PDF...")
    files = [('files', ('test1.jpg', b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\xff\xd9', 'image/jpeg'))]
    resp = requests.post(f"{API_URL}/tools/jpg-to-pdf", files=files)
    if not resp.ok: raise Exception(resp.text)
    wait_for_job(resp.json()["job_id"])

if __name__ == "__main__":
    try:
        test_merge()
        test_split()
        test_rotate()
        test_compress()
        test_pdf_to_jpg()
        test_jpg_to_pdf()
        print("All tests passed!")
    except Exception as e:
        print(f"Error: {e}")
