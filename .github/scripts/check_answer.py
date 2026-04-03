import os
import re
import json
import urllib.request
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

changed_files_raw = os.environ.get("CHANGED_FILES", "").strip()
changed_files = [f for f in changed_files_raw.split("\n") if f.strip()]

if not changed_files:
    print("변경된 답안 파일 없음. 종료.")
    exit(0)

comments = []

for filepath in changed_files:
    # answer/problem001/github-id.py 형태에서 문제번호와 학생 ID 추출
    match = re.match(r'answer/(problem\d+)/(.+)', filepath)
    if not match:
        print(f"경로 형식 불일치, 건너뜀: {filepath}")
        continue

    problem_name = match.group(1)       # e.g. problem001
    student_filename = match.group(2)   # e.g. minsu.py
    student_id = os.path.splitext(student_filename)[0]

    problem_path = f"problems/{problem_name}.md"

    if not os.path.exists(problem_path):
        comments.append(
            f"### `{filepath}`\n"
            f"⚠️ **{student_id}** — 문제 파일을 찾을 수 없어요: `{problem_path}`"
        )
        continue

    if not os.path.exists(filepath):
        print(f"답안 파일 없음, 건너뜀: {filepath}")
        continue

    with open(problem_path, encoding="utf-8") as f:
        problem_content = f.read()

    with open(filepath, encoding="utf-8") as f:
        answer_content = f.read()

    print(f"검토 중: {filepath}")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": (
                    f"아래는 코딩 문제와 학생의 답안입니다.\n"
                    f"답안이 문제 요구사항을 올바르게 충족하는지 검토해주세요.\n\n"
                    f"## 문제 ({problem_name})\n{problem_content}\n\n"
                    f"## 학생 답안 (`{student_id}`)\n```\n{answer_content}\n```\n\n"
                    f"아래 형식으로만 답해주세요:\n"
                    f"- **결과**: 정답 ✅ 또는 오답 ❌\n"
                    f"- **이유**: 2~3줄 설명\n"
                    f"- **피드백**: 개선할 점 (없으면 생략)"
                ),
            }
        ],
    )

    ai_response = response.choices[0].message.content
    comments.append(f"### `{filepath}`\n\n{ai_response}")

if not comments:
    print("검토할 파일 없음. 종료.")
    exit(0)

# PR에 코멘트 작성
body = "## 🤖 AI 답안 검토 결과\n\n" + "\n\n---\n\n".join(comments)

pr_number = os.environ["PR_NUMBER"]
repo = os.environ["REPO"]
token = os.environ["GH_TOKEN"]

url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
data = json.dumps({"body": body}).encode()

req = urllib.request.Request(url, data=data, method="POST")
req.add_header("Authorization", f"Bearer {token}")
req.add_header("Content-Type", "application/json")
req.add_header("Accept", "application/vnd.github+json")

urllib.request.urlopen(req)
print("PR 코멘트 작성 완료!")
