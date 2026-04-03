# Jvision Mentor Problems

Jvision Lab 멘토가 출제하는 코딩 문제와 학생 답안을 관리하는 저장소입니다.

## 구조

```text
problems/
  problem001.md
  problem002.md

answer/
  problem001/
    github-id.py
  problem002/
    github-id.py
```
aa

- `problems/`: 문제 설명 파일 모음
- `answer/problem{번호}/`: 해당 문제의 학생 답안 모음
a
## 브랜치 규칙

- 학생 브랜치: `student/{github-id}/problem-{번호}`
- 멘토 브랜치: `mentor/{github-id}/problem-{번호}`

예시:

- `student/minsu/problem-001`
- `mentor/hyung/problem-001`

## 제출 방식

1. 학생은 자신의 브랜치에서만 작업합니다.
2. 문제 설명은 `problems/problem{번호}.md` 에서 확인합니다.
3. 답안은 `answer/problem{번호}/{github-id}.py` 형식으로 추가합니다.
4. 작업 후 `master` 대상으로 Pull Request를 생성합니다.

## 리뷰 규칙

- 학생끼리 리뷰는 가능합니다.
- 머지는 멘토 승인 2회가 필요합니다.
- `master` 직접 푸시는 금지합니다.
- 관리자는 예외적으로 전체 작업을 처리할 수 있습니다.

자세한 운영 규칙은 [CONTRIBUTING.md](./CONTRIBUTING.md)에서 확인합니다.

1312333122312
