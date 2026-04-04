"""
새 문제 md가 master에 머지되면 Cartel_Lab에 퀴즈 자동 등록
문제 md의 내용을 파싱해서 quiz 데이터로 변환
"""
import os
import re
import json
import urllib.request

CARTEL_API_URL = os.environ["CARTEL_API_URL"].rstrip("/")
WEBHOOK_SECRET = os.environ["GITHUB_WEBHOOK_SECRET"]
new_files_raw = os.environ.get("NEW_PROBLEM_FILES", "").strip()
new_files = [f for f in new_files_raw.split("\n") if f.strip()]

if not new_files:
    print("등록할 문제 없음. 종료.")
    exit(0)

for filepath in new_files:
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # 제목 파싱
    title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else os.path.splitext(os.path.basename(filepath))[0]

    # 문제 설명 파싱
    desc_match = re.search(r'## 문제 설명\s+(.*?)(?=##|\Z)', content, re.DOTALL)
    question = desc_match.group(1).strip() if desc_match else content.strip()

    payload = {
        "title": title,
        "code_snippet": "",
        "question": question,
        "answer": "[GitHub PR]",   # 실제 정답은 PR 머지로 처리
        "ai_trap_code": "",
        "ai_trap_answer": "",
        "scheduled_date": "",      # 빈 값이면 오늘 날짜로 설정됨
    }

    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{CARTEL_API_URL}/api/quiz/github/register-quiz/",
        data=data,
        method="POST",
    )
    req.add_header("Content-Type", "application/json")
    req.add_header("X-GitHub-Token", WEBHOOK_SECRET)

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            print(f"✅ 퀴즈 등록 완료: {title} → quiz id={result['quiz']['id']}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"❌ 퀴즈 등록 실패 ({filepath}): {e.code} {body}")
