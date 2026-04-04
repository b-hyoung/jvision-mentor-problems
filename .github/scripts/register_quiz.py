"""
새 문제 md가 master에 머지되면 Cartel_Lab에 퀴즈 자동 등록
- MD의 ## 출제일 섹션이 있으면 해당 날짜 사용
- 없으면 오늘부터 탐색
- 해당 날짜에 이미 문제가 있으면 빈 날짜 찾을 때까지 +1일
"""
import os
import re
import json
import urllib.request
import urllib.parse
from datetime import date

CARTEL_API_URL = os.environ["CARTEL_API_URL"].rstrip("/")
WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]
new_files_raw = os.environ.get("NEW_PROBLEM_FILES", "").strip()
new_files = [f for f in new_files_raw.split("\n") if f.strip()]

if not new_files:
    print("등록할 문제 없음. 종료.")
    exit(0)


def fetch_next_available_date(from_date: str) -> str:
    """Cartel_Lab에서 빈 날짜 조회"""
    params = urllib.parse.urlencode({"from": from_date})
    req = urllib.request.Request(
        f"{CARTEL_API_URL}/api/quiz/github/next-available-date/?{params}",
        method="GET",
    )
    req.add_header("X-GitHub-Token", WEBHOOK_SECRET)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["available_date"]


for filepath in new_files:
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # 제목 파싱
    title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else os.path.splitext(os.path.basename(filepath))[0]

    # 문제 설명 파싱
    desc_match = re.search(r'## 문제 설명\s+(.*?)(?=##|\Z)', content, re.DOTALL)
    question = desc_match.group(1).strip() if desc_match else content.strip()

    # 출제일 파싱 (없으면 오늘)
    date_match = re.search(r'## 출제일\s+(\d{4}-\d{2}-\d{2})', content)
    from_date = date_match.group(1) if date_match else date.today().isoformat()

    # 빈 날짜 탐색
    try:
        scheduled_date = fetch_next_available_date(from_date)
        if scheduled_date != from_date:
            print(f"⚠️ {from_date} 에 이미 문제 있음 → {scheduled_date} 로 조정")
    except Exception as e:
        print(f"⚠️ 날짜 조회 실패, 오늘 날짜 사용: {e}")
        scheduled_date = from_date

    payload = {
        "title": title,
        "code_snippet": "",
        "question": question,
        "answer": "[GitHub PR]",
        "ai_trap_code": "",
        "ai_trap_answer": "",
        "scheduled_date": scheduled_date,
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
            quiz_id = result["quiz"]["id"]
            print(f"✅ 퀴즈 등록 완료: {title} → quiz_id={quiz_id}, 날짜={scheduled_date}")

            # config 파일에 cartel_quiz_id 자동 기록
            problem_name = os.path.splitext(os.path.basename(filepath))[0]
            config_path = f".github/problem-configs/{problem_name}.json"
            if os.path.exists(config_path):
                with open(config_path, encoding="utf-8") as f:
                    config = json.load(f)
                config["cartel_quiz_id"] = quiz_id
                config["scheduled_date"] = scheduled_date
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                print(f"✅ {config_path} 에 cartel_quiz_id={quiz_id} 기록 완료")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"❌ 퀴즈 등록 실패 ({filepath}): {e.code} {body}")
