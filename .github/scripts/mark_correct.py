"""
학생 PR이 master에 머지되면 Cartel_Lab에 정답 처리 요청
answer/problem001/github-id.py → github_username으로 유저 조회 후 정답 처리
"""
import os
import re
import json
import urllib.request

CARTEL_API_URL = os.environ["CARTEL_API_URL"].rstrip("/")
WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]
merged_files_raw = os.environ.get("MERGED_FILES", "").strip()
merged_files = [f for f in merged_files_raw.split("\n") if f.strip()]

if not merged_files:
    print("처리할 파일 없음. 종료.")
    exit(0)

# 문제번호 → quiz_id 조회 헬퍼
def fetch_quiz_id_by_problem(problem_name):
    """Cartel_Lab에서 quiz 목록 조회해서 문제 이름으로 매칭"""
    req = urllib.request.Request(
        f"{CARTEL_API_URL}/api/quiz/github/register-quiz/",
        method="GET",
    )
    req.add_header("X-GitHub-Token", WEBHOOK_SECRET)
    try:
        with urllib.request.urlopen(req) as resp:
            quizzes = json.loads(resp.read())
            for quiz in quizzes:
                if problem_name.lower() in quiz.get("title", "").lower():
                    return quiz["id"]
    except Exception:
        pass
    return None

for filepath in merged_files:
    match = re.match(r'answer/(problem\d+)/(.+)', filepath)
    if not match:
        print(f"경로 형식 불일치, 건너뜀: {filepath}")
        continue

    problem_name = match.group(1)
    github_username = os.path.splitext(match.group(2))[0]

    # quiz_id는 문제 config에서 읽기 (register_quiz가 저장해두면 좋지만 지금은 이름으로 매칭)
    config_path = f".github/problem-configs/{problem_name}.json"
    quiz_id = None
    if os.path.exists(config_path):
        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)
            quiz_id = config.get("cartel_quiz_id")

    if not quiz_id:
        print(f"⚠️ {problem_name}의 quiz_id를 찾을 수 없어요. register_quiz 후 config에 cartel_quiz_id를 추가하세요.")
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
