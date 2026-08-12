curl_bash = """curl 'https://api.123278.com/b/api/file/upload_request?2736366041=1786498920-4290178-391605077' \
  -H 'app-version: 3' \
  -H 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3ODY0NDM4MjQsImlkIjoxODE3ODM1ODQwLCJ2IjowLCJtYWlsIjoiIiwidXNlcm5hbWUiOiIxODgxMzUzNzgwNiIsIm5pY2tuYW1lIjoi6Iq56I-c5LqRIiwic3VwcGVyIjpmYWxzZSwiaXNUb3VyaXN0IjpmYWxzZSwiaXNPYXV0aDJMb2dpbiI6ZmFsc2UsImFwcE5hbWUiOiIiLCJsb2dpbl90eXBlIjoxLCJwbGF0Zm9ybSI6MiwiZGV2aWNlSWQiOiJDaHJvbWUoOik4ZjIxYWUxN2Y0NGU5ODcxZDIzNWYzNWNkZDlmZTJhMDZjNDYyMDA5MmZlYzhmZGE5ODlmMTc1MWYzNzMyZjE2KDopV2luZG93cyAxMCIsImNsaWVudElQIjoiMTE2LjI0LjY3LjEzNiIsImRldmljZU5hbWUiOiIiLCJkZXZpY2VNb2RlbCI6IiIsImRldmljZVR5cGUiOiIiLCJyZW1lbWJlciI6MSwiZXhwIjoxNzk0MjE5ODI0fQ.bA4YbCy1rcOAS7H_Sc3af2dS8_0IeAy5rqSD44AaSJA' \
  -H 'content-type: application/json;charset=UTF-8' \
  -H 'loginuuid: 88d0d3909973f39e0e20395c29d84dd7c9cc254e7eacac1e3392367a017fcbfb' \
  -H 'platform: web' \
  --data-raw '{"driveId":0,"etag":"35d63ffb0f3fe7ece63c829a65ab3fab","fileName":"ThrottleStop_9.7.zip","parentFileId":0,"size":1790707,"type":0,"RequestSource":null,"duplicate":0}'"""

'''etag = "35d63ffb0f3fe7ece63c829a65ab3fab"
fileName = "ThrottleStop_9.7.zip"
size = "1790707"'''

import re
import json
import subprocess
import sys

parentFileId = 0
#parentFileId = 56090354

def upload(etag, fileName, size, parentFileId=parentFileId):
    curl_bash_prefix = re.sub("--data-raw *'{.*?}'","", curl_bash)
    payload = {
        "driveId": 0, "etag": etag, "fileName": fileName,
        "parentFileId": parentFileId, "size": int(size), "type": 0,
        "RequestSource": None, "duplicate": 0,
    }
    data_raw = f"--data-raw '{json.dumps(payload)}'"

    #command = (curl_bash_prefix + data_raw).replace(" '", "###").replace("'   ", "###").replace("'", "").split("###")
    command = re.sub(" *?' *","###", (curl_bash_prefix + data_raw)).strip('#').split("###")
    print(command)


    proc = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace",)
    if proc.returncode != 0:
        raise RuntimeError(f"curl 执行失败: {proc.stderr.strip()}")

    raw = proc.stdout.strip()
    try:
        response_json = json.loads(raw)
    except json.JSONDecodeError:
        response_json = {"_raw": raw}
    print(response_json)


# ───────────────────────── 主流程 ─────────────────────────
#123秒传脚本提取的 etag = 文件原始字节 MD5（16 字节）经 base62 编码（字符集 0-9a-zA-Z，小写在前）得到的 22 字符指纹
def main():
    manifest_path = sys.argv[1] if len(sys.argv) > 1 else "manifest.json"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    files = manifest.get("files", [])
    print(f"清单共 {len(files)} 个文件，总计 {manifest.get('totalSize', 0):,} bytes")

    for i, entry in enumerate(files, 1):
        # {'code': 5064, 'message': '文件名要小于256个字符且不能包含以下任何字符："\\/:*?|><', 'data': None}
        fileName = re.sub("[\"\\/:*?|><']", "-", entry["path"])
        etag = entry["etag"]
        size = entry["size"]

        print(f"[{i}/{len(files)}] {fileName}")
        print(f"  size={size}, etag={etag}")

        try:
            data = upload(etag, fileName, size)
            
        except Exception as e:
            print(f"e  -> 请求异常: {e}\n")


if __name__ == "__main__":
    main()