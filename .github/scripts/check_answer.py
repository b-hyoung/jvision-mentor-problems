import os
import re
import json
import subprocess
import urllib.request
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def run_code(filepath, input_data, timeout=5):
    """학생 코드를 실행하고 출력 반환. 실패 시 에러 메시지 반환."""
    try:
        result = subprocess.run(
            ["python", filepath],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout.strip(), None
    except subprocess.TimeoutExpired:
        return None, "시간 초과 (5초)"
    except Exception as e:
        return None, str(e)


def send_discord(webhook_url, message):
    """Discord 웹훅으로 메시지 전송."""
    import http.client, ssl
    from urllib.parse import urlparse
    parsed = urlparse(webhook_url)
    body = json.dumps({"content": message}).encode("utf-8")
    conn = http.client.HTTPSConnection(parsed.netloc, context=ssl.create_default_context())
    try:
        conn.request("POST", parsed.path, body=body, headers={"Content-Type": "application/json"})
        resp = conn.getresponse()
        print(f"Discord 전송 결과: {resp.status} {resp.reason}")
    except Exception as e:
        print(f"Discord 전송 실패: {e}")
    finally:
        conn.close()


def load_config(problem_name):
    """문제별 AI 전용 설정 로드. 없으면 빈 dict 반환."""
    config_path = f".github/problem-configs/{problem_name}.json"
    if os.path.exists(config_path):
        with open(config_path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def generate_edge_cases(problem_content, basic_cases, config):
    """GPT로 엣지케이스 생성."""
    edge_strategy = config.get("edge_case_strategy", "경계값, 예외 상황 위주로 3개 이내 생성.")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=512,
        messages=[
            {
                "role": "user",
                "content": (
                    f"아래 문제와 기본 테스트케이스를 보고, 학생 코드를 검증할 추가 엣지케이스를 생성해주세요.\n\n"
                    f"## 문제\n{problem_content}\n\n"
                    f"## 기본 테스트케이스\n{json.dumps(basic_cases, ensure_ascii=False)}\n\n"
                    f"## 엣지케이스 전략\n{edge_strategy}\n\n"
                    f"아래 JSON 형식으로만 답하세요. 다른 설명 없이 JSON만:\n"
                    f'[{{"input": "값", "output": "기대출력"}}]'
                ),
            }
        ],
    )
    raw = response.choices[0].message.content.strip()
    # 코드블록 제거
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)


def generate_hint(problem_content, failed_cases, config):
    """실패한 테스트케이스 기반으로 힌트 생성."""
    hint_guide = config.get("hint_guide", "답을 직접 알려주지 말고 방향만 제시할 것.")
    failed_summary = "\n".join(
        [f"- 입력: {c['input']} → 기대: {c['expected']} / 실제: {c['actual']}" for c in failed_cases]
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=512,
        messages=[
            {
                "role": "user",
                "content": (
                    f"아래 문제에서 학생 코드가 일부 테스트를 통과하지 못했습니다.\n\n"
                    f"## 문제\n{problem_content}\n\n"
                    f"## 실패한 테스트\n{failed_summary}\n\n"
                    f"## 힌트 가이드\n{hint_guide}\n\n"
                    f"2~3줄로 간결하게 힌트만 작성하세요."
                ),
            }
        ],
    )
    return response.choices[0].message.content.strip()


# ── 메인 ──────────────────────────────────────────────

changed_files_raw = os.environ.get("CHANGED_FILES", "").strip()
changed_files = [f for f in changed_files_raw.split("\n") if f.strip()]

if not changed_files:
    print("변경된 답안 파일 없음. 종료.")
    exit(0)

pr_number = os.environ["PR_NUMBER"]
pr_author = os.environ.get("PR_AUTHOR", "알 수 없음")
pr_url = os.environ.get("PR_URL", "")
discord_webhook = os.environ.get("DISCORD_WEBHOOK_URL", "")
all_comments = []

for filepath in changed_files:
    match = re.match(r'answer/(problem\d+)/(.+)', filepath)
    if not match:
        print(f"경로 형식 불일치, 건너뜀: {filepath}")
        continue

    problem_name = match.group(1)
    student_id = os.path.splitext(match.group(2))[0]
    problem_path = f"problems/{problem_name}.md"

    if not os.path.exists(problem_path):
        all_comments.append(f"### `{filepath}`\n⚠️ 문제 파일을 찾을 수 없어요: `{problem_path}`")
        continue

    if not os.path.exists(filepath):
        continue

    with open(problem_path, encoding="utf-8") as f:
        problem_content = f.read()

    config = load_config(problem_name)

    # 테스트케이스 파싱
    tc_match = re.search(r'```json\s*(\[.*?\])\s*```', problem_content, re.DOTALL)
    if not tc_match:
        all_comments.append(f"### `{filepath}`\n⚠️ 문제 파일에 테스트 케이스가 없어요.")
        continue

    basic_cases = json.loads(tc_match.group(1))

    print(f"검토 중: {filepath}")

    # ── 1단계: 기본 테스트 ──
    basic_rows = []
    basic_failed = []

    for tc in basic_cases:
        actual, err = run_code(filepath, tc["input"])
        if err:
            actual = f"오류: {err}"
            passed = False
        else:
            passed = actual == tc["output"].strip()

        icon = "✅" if passed else "❌"
        basic_rows.append(f"| `{tc['input']}` | `{tc['output']}` | `{actual}` | {icon} |")
        if not passed:
            basic_failed.append({"input": tc["input"], "expected": tc["output"], "actual": actual})

    basic_table = (
        "| 입력 | 기대 출력 | 실제 출력 | 결과 |\n"
        "|------|-----------|-----------|------|\n"
        + "\n".join(basic_rows)
    )

    # ── 2단계: AI 심화 테스트 (기본 통과한 경우만) ──
    edge_section = ""
    all_failed = basic_failed[:]

    if not basic_failed:
        try:
            edge_cases = generate_edge_cases(problem_content, basic_cases, config)
            edge_rows = []
            edge_failed = []

            for tc in edge_cases:
                actual, err = run_code(filepath, tc["input"])
                if err:
                    actual = f"오류: {err}"
                    passed = False
                else:
                    passed = actual == tc["output"].strip()

                icon = "✅" if passed else "❌"
                # 심화 테스트는 입력값과 결과만 공개 (기대 출력 숨김)
                edge_rows.append(f"| `{tc['input']}` | {icon} |")
                if not passed:
                    edge_failed.append({"input": tc["input"], "expected": tc["output"], "actual": actual})
                    all_failed.append({"input": tc["input"], "expected": tc["output"], "actual": actual})

            edge_table = (
                "| 입력 | 결과 |\n"
                "|------|------|\n"
                + "\n".join(edge_rows)
            )
            edge_section = f"\n\n### AI 심화 테스트\n{edge_table}"
        except Exception as e:
            edge_section = f"\n\n### AI 심화 테스트\n⚠️ 생성 실패: {e}"

    # ── 3단계: 힌트 생성 ──
    hint_section = ""
    if all_failed:
        try:
            hint = generate_hint(problem_content, all_failed, config)
            hint_section = f"\n\n**💡 힌트**\n{hint}"
        except Exception as e:
            hint_section = f"\n\n**💡 힌트** 생성 실패: {e}"
    else:
        hint_section = "\n\n**🎉 모든 테스트 통과!** 잘 했어요."
        if discord_webhook:
            send_discord(
                discord_webhook,
                f"✅ **AI 검토 통과!**\n"
                f"> 제출자: `{pr_author}`\n"
                f"> 문제: `{problem_name}`\n"
                f"> PR: {pr_url}"
            )

    comment = (
        f"### `{filepath}` — **{student_id}**\n\n"
        f"#### 기본 테스트\n{basic_table}"
        f"{edge_section}"
        f"{hint_section}"
    )
    all_comments.append(comment)

if not all_comments:
    print("검토할 파일 없음. 종료.")
    exit(0)

body = "## 🤖 AI 답안 검토 결과\n\n" + "\n\n---\n\n".join(all_comments)

subprocess.run(
    ["gh", "pr", "comment", pr_number, "--body", body],
    check=True
)
print("PR 코멘트 작성 완료!")
