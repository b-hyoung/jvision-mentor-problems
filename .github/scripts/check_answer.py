import html
import json
import os
import re
import subprocess
import tempfile
import urllib.request

from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def detect_language(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".py":
        return "Python"
    if ext == ".c":
        return "C"
    return None


def run_python(filepath, input_data, timeout=5):
    result = subprocess.run(
        ["python", filepath],
        input=input_data,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        error_text = (result.stderr or result.stdout or "실행 오류").strip()
        return None, f"실행 오류: {error_text}"
    return result.stdout.rstrip(), None


def run_c(filepath, input_data, timeout=5):
    with tempfile.TemporaryDirectory() as temp_dir:
        exe_path = os.path.join(temp_dir, "student.out")
        compile_result = subprocess.run(
            ["gcc", filepath, "-O2", "-std=c11", "-o", exe_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if compile_result.returncode != 0:
            error_text = (compile_result.stderr or compile_result.stdout or "컴파일 오류").strip()
            return None, f"컴파일 오류: {error_text}"

        result = subprocess.run(
            [exe_path],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            error_text = (result.stderr or result.stdout or "실행 오류").strip()
            return None, f"실행 오류: {error_text}"
        return result.stdout.rstrip(), None


def run_code(filepath, input_data, timeout=5):
    language = detect_language(filepath)
    try:
        if language == "Python":
            return run_python(filepath, input_data, timeout=timeout)
        if language == "C":
            return run_c(filepath, input_data, timeout=timeout)
        return None, f"지원하지 않는 파일 형식입니다: {os.path.splitext(filepath)[1]}"
    except FileNotFoundError:
        return None, "실행에 필요한 명령어를 찾을 수 없어요."
    except subprocess.TimeoutExpired:
        return None, "시간 초과 (5초)"
    except Exception as e:
        return None, str(e)


def format_table_cell(value):
    text = "" if value is None else str(value)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if text == "":
        return "&nbsp;"

    if "\n" in text:
        escaped = html.escape(text)
        return f"<pre>{escaped}</pre>"

    escaped = html.escape(text).replace("|", "&#124;")
    return f"`{escaped}`"


def load_discord_mentions():
    mapping_path = ".github/discord-mentions.json"
    if os.path.exists(mapping_path):
        with open(mapping_path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def build_discord_mention(pr_author):
    mentions = load_discord_mentions()
    discord_user_id = mentions.get(pr_author)
    if discord_user_id:
        return f"<@{discord_user_id}>"
    return ""


def send_discord(webhook_url, pr_author, problem_name, pr_url):
    import http.client
    import ssl
    from urllib.parse import urlparse

    parsed = urlparse(webhook_url)
    mention = build_discord_mention(pr_author)
    payload = {
        "content": mention,
        "embeds": [
            {
                "title": "✅ AI 검토 통과!",
                "color": 0x57F287,
                "fields": [
                    {"name": "제출자", "value": f"`{pr_author}`", "inline": True},
                    {"name": "문제", "value": f"`{problem_name}`", "inline": True},
                    {"name": "PR", "value": f"[바로가기]({pr_url})", "inline": True},
                ],
                "footer": {"text": "Jvision Mentor Problems"},
            }
        ],
    }
    body = json.dumps(payload).encode("utf-8")
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
    config_path = f".github/problem-configs/{problem_name}.json"
    if os.path.exists(config_path):
        with open(config_path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def generate_edge_cases(problem_content, basic_cases, config, language):
    static_edge_cases = config.get("edge_cases")
    if static_edge_cases:
        return static_edge_cases

    edge_strategy = config.get("edge_case_strategy", "경계값, 예외 상황 위주로 3개 이내 생성.")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=512,
        messages=[
            {
                "role": "user",
                "content": (
                    f"아래 문제와 기본 테스트케이스를 보고, 학생의 {language} 답안을 검증할 추가 엣지케이스를 생성해주세요.\n\n"
                    f"## 문제\n{problem_content}\n\n"
                    f"## 기본 테스트케이스\n{json.dumps(basic_cases, ensure_ascii=False)}\n\n"
                    f"## 엣지케이스 전략\n{edge_strategy}\n\n"
                    f"출력에 줄바꿈이 있으면 반드시 \\n 으로 표기하세요.\n"
                    f"아래 JSON 형식으로만 답하세요. 다른 설명 없이 JSON만:\n"
                    f'[{{"input": "값", "output": "기대출력"}}]'
                ),
            }
        ],
    )
    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)


def generate_hint(problem_content, failed_cases, config, language):
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
                    f"아래 문제에서 학생의 {language} 코드가 일부 테스트를 통과하지 못했습니다.\n\n"
                    f"## 문제\n{problem_content}\n\n"
                    f"## 실패한 테스트\n{failed_summary}\n\n"
                    f"## 힌트 가이드\n{hint_guide}\n\n"
                    f"{language} 문법과 실행 방식을 기준으로만 2~3줄의 간결한 힌트를 작성하세요. "
                    f"다른 언어의 함수명이나 문법은 언급하지 마세요."
                ),
            }
        ],
    )
    return response.choices[0].message.content.strip()


changed_files_raw = os.environ.get("CHANGED_FILES", "").strip()
changed_files = [f for f in changed_files_raw.split("\n") if f.strip()]

if not changed_files:
    print("변경된 답안 파일 없음. 종료.")
    raise SystemExit(0)

pr_number = os.environ["PR_NUMBER"]
pr_author = os.environ.get("PR_AUTHOR", "알 수 없음")
pr_url = os.environ.get("PR_URL", "")
discord_webhook = os.environ.get("DISCORD_WEBHOOK_URL", "")
all_comments = []

for filepath in changed_files:
    match = re.match(r"answer/(problem\d+)/(.+)", filepath)
    if not match:
        print(f"경로 형식 불일치, 건너뜀: {filepath}")
        continue

    problem_name = match.group(1)
    student_id = os.path.splitext(match.group(2))[0]
    problem_path = f"problems/{problem_name}.md"
    language = detect_language(filepath)

    if not os.path.exists(problem_path):
        all_comments.append(f"### `{filepath}`\n⚠️ 문제 파일을 찾을 수 없어요: `{problem_path}`")
        continue

    if not os.path.exists(filepath):
        continue

    if not language:
        all_comments.append(f"### `{filepath}`\n⚠️ 지원하지 않는 파일 형식이에요.")
        continue

    with open(problem_path, encoding="utf-8") as f:
        problem_content = f.read()

    config = load_config(problem_name)

    tc_match = re.search(r"```json\s*(\[.*?\])\s*```", problem_content, re.DOTALL)
    if not tc_match:
        all_comments.append(f"### `{filepath}`\n⚠️ 문제 파일에 테스트 케이스가 없어요.")
        continue

    basic_cases = json.loads(tc_match.group(1))

    print(f"검토 중: {filepath}")

    basic_rows = []
    basic_failed = []

    for tc in basic_cases:
        actual, err = run_code(filepath, tc["input"])
        expected = tc["output"].strip()
        if err:
            actual = err
            passed = False
        else:
            passed = actual == expected

        icon = "✅" if passed else "❌"
        basic_rows.append(
            f"| {format_table_cell(tc['input'])} | {format_table_cell(expected)} | "
            f"{format_table_cell(actual)} | {icon} |"
        )
        if not passed:
            basic_failed.append({"input": tc["input"], "expected": expected, "actual": actual})

    basic_table = (
        "| 입력 | 기대 출력 | 실제 출력 | 결과 |\n"
        "|------|-----------|-----------|------|\n"
        + "\n".join(basic_rows)
    )

    edge_section = ""
    all_failed = basic_failed[:]

    if not basic_failed:
        try:
            edge_cases = generate_edge_cases(problem_content, basic_cases, config, language)
            edge_rows = []

            for tc in edge_cases:
                actual, err = run_code(filepath, tc["input"])
                expected = tc["output"].strip()
                if err:
                    actual = err
                    passed = False
                else:
                    passed = actual == expected

                icon = "✅" if passed else "❌"
                edge_rows.append(f"| {format_table_cell(tc['input'])} | {icon} |")
                if not passed:
                    all_failed.append({"input": tc["input"], "expected": expected, "actual": actual})

            edge_table = "| 입력 | 결과 |\n|------|------|\n" + "\n".join(edge_rows)
            edge_section = f"\n\n### AI 심화 테스트\n{edge_table}"
        except Exception as e:
            edge_section = f"\n\n### AI 심화 테스트\n⚠️ 생성 실패: {e}"

    if all_failed:
        try:
            hint = generate_hint(problem_content, all_failed, config, language)
            hint_section = f"\n\n**💡 힌트**\n{hint}"
        except Exception as e:
            hint_section = f"\n\n**💡 힌트** 생성 실패: {e}"
    else:
        hint_section = "\n\n**🎉 모든 테스트 통과!** 잘 했어요."
        if discord_webhook:
            send_discord(discord_webhook, pr_author, problem_name, pr_url)

    comment = (
        f"### `{filepath}` — **{student_id}** ({language})\n\n"
        f"#### 기본 테스트\n{basic_table}"
        f"{edge_section}"
        f"{hint_section}"
    )
    all_comments.append(comment)

if not all_comments:
    print("검토할 파일 없음. 종료.")
    raise SystemExit(0)

body = "## 🤖 AI 답안 검토 결과\n\n" + "\n\n---\n\n".join(all_comments)

subprocess.run(["gh", "pr", "comment", pr_number, "--body", body], check=True)
print("PR 코멘트 작성 완료!")
