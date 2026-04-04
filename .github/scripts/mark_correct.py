"""
학생 PR이 master에 머지되면 Cartel_Lab에 정답 처리 요청
PR 작성자의 GitHub 아이디로 유저 조회 후 정답 처리
"""
import os
import re
import json
import urllib.request

CARTEL_API_URL = os.environ["CARTEL_API_URL"].rstrip("/")
WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]
github_username = os.environ["PR_AUTHOR"]
merged_files_raw = os.environ.get("MERGED_FILES", "").strip()
merged_files = [f for f in merged_files_raw.split("\n") if f.strip()]

if not merged_files:
    print("처리할 파일 없음. 종료.")
    exit(0)

# 머지된 파일에서 문제 번호 추출 (중복 제거)
problem_names = list({
    re.match(r'answer/(problem\d+)/', f).group(1)
    for f in merged_files
    if re.match(r'answer/(problem\d+)/', f)
})

for problem_name in problem_names:
    config_path = f".github/problem-configs/{problem_name}.json"
    quiz_id = None
    if os.path.exists(config_path):
        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)
            quiz_id = config.get("cartel_quiz_id")

    if not quiz_id:
        print(f"⚠️ {problem_name}의 cartel_quiz_id를 찾을 수 없어요.")
        continue

    payload = json.dumps({
        "github_username": github_username,
        "quiz_id": quiz_id,
    }).encode()

    req = urllib.request.Request(
        f"{CARTEL_API_URL}/api/quiz/github/mark-correct/",
        data=payload,
        method="POST",
    )
    req.add_header("Content-Type", "application/json")
    req.add_header("X-GitHub-Token", WEBHOOK_SECRET)

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            print(f"✅ 정답 처리 완료: {github_username} / {problem_name}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"❌ 정답 처리 실패 ({github_username}/{problem_name}): {e.code} {body}")
