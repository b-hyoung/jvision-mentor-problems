import os
import re
import json
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

new_files_raw = os.environ.get("NEW_PROBLEM_FILES", "").strip()
new_files = [f for f in new_files_raw.split("\n") if f.strip()]

if not new_files:
    print("새 문제 파일 없음. 종료.")
    exit(0)

os.makedirs(".github/problem-configs", exist_ok=True)

for filepath in new_files:
    problem_name = os.path.splitext(os.path.basename(filepath))[0]
    config_path = f".github/problem-configs/{problem_name}.json"

    if os.path.exists(config_path):
        print(f"이미 존재함, 건너뜀: {config_path}")
        continue

    with open(filepath, encoding="utf-8") as f:
        problem_content = f.read()

    print(f"config 생성 중: {problem_name}")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=512,
        messages=[
            {
                "role": "user",
                "content": (
                    f"아래는 코딩 교육용 문제입니다.\n"
                    f"이 문제의 자동 채점 시스템에 사용할 AI 설정을 생성해주세요.\n\n"
                    f"## 문제\n{problem_content}\n\n"
                    f"아래 JSON 형식으로만 답하세요. 다른 설명 없이 JSON만:\n"
                    f"{{\n"
                    f'  "hint_guide": "오답 시 학생에게 줄 힌트 방향 (답 직접 제시 금지, 2학년 멘토가 사용)",\n'
                    f'  "edge_case_strategy": "이 문제에서 학생 코드를 검증할 엣지케이스 생성 전략 (3개 이내)"\n'
                    f"}}"
                ),
            }
        ],
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"```json|```", "", raw).strip()

    config = json.loads(raw)

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"생성 완료: {config_path}")
    print(json.dumps(config, ensure_ascii=False, indent=2))
