"""Smoke test: sends every image in ./sample_images to the running server.
Usage:  python app.py   (in one terminal)   then   python test_api.py
"""
import glob, json, os, sys, urllib.request, uuid

URL = os.environ.get("API", "http://localhost:8000") + "/api/predict"

def post(path):
    boundary = uuid.uuid4().hex
    with open(path, "rb") as fh:
        payload = fh.read()
    body = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; "
        f"filename=\"{os.path.basename(path)}\"\r\nContent-Type: image/jpeg\r\n\r\n"
    ).encode() + payload + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    return json.load(urllib.request.urlopen(req, timeout=60))

ok = 0
files = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "sample_images", "*")))
for f in files:
    r = post(f)
    expected = os.path.basename(f).rsplit("_", 1)[0]
    hit = r["prediction"] == expected
    ok += hit
    print(f"{'PASS' if hit else 'FAIL'}  {os.path.basename(f):42s} -> {r['prediction']:28s} {r['confidence']:6.2f}%")
print(f"\n{ok}/{len(files)} correct")
sys.exit(0 if ok == len(files) else 1)
