# Jvision Mentor Problems

Jvision Lab 멘토가 출제하는 코딩 문제와 1학년 학생 답안을 관리하는 저장소입니다.  
PR 기반으로 문제 출제 및 답안 제출이 이루어지며, AI 자동 검토와 Cartel_Lab 연동이 포함되어 있습니다.

---

## 디렉토리 구조

```
problems/
  problem001.md       ← 학생 공개용 문제 (출제일, 설명, 테스트 케이스 포함)

answer/
  problem001/
    {github-id}.py    ← 학생 답안

.github/
  workflows/
    check-answer.yml            ← 답안 PR 시 AI 검토 + 머지 시 정답 처리
    generate-problem-config.yml ← 문제 MD 머지 시 config 자동 생성 + Cartel_Lab 등록
  scripts/
    check_answer.py      ← AI 답안 검토 스크립트
    generate_config.py   ← GPT로 문제 config 자동 생성
    register_quiz.py     ← Cartel_Lab에 퀴즈 등록
    mark_correct.py      ← Cartel_Lab 정답 처리
  problem-configs/
    problem001.json     ← AI 전용 설정 (hint_guide, edge_case_strategy, cartel_quiz_id)
```

---

## 브랜치 규칙

| 역할 | 브랜치 형식 | 예시 |
|------|------------|------|
| 1학년 (답안 제출) | `student/{github-id}/problem-{번호}` | `student/minsu/problem-001` |
| 2학년 (문제 출제) | `mentor/{github-id}/problem-{번호}` | `mentor/hyung/problem-001` |

- `master` 직접 푸시 금지
- 모든 작업은 PR을 통해 진행

---

## 워크플로우

### 2학년 문제 출제 흐름

```
1. mentor/{github-id}/problem-{번호} 브랜치 생성
2. problems/problem{번호}.md 작성 (출제일, 문제 설명, 테스트 케이스 포함)
3. master 대상으로 PR 생성
4. 다른 2학년 멘토가 리뷰 후 승인 → 머지
        ↓ (자동)
5. GPT가 문제를 읽고 .github/problem-configs/problem{번호}.json 생성
6. Cartel_Lab에 퀴즈 자동 등록 (출제일 기준, 날짜 충돌 시 자동 +1일)
7. config에 cartel_quiz_id 자동 기록
```

### 1학년 답안 제출 흐름

```
1. student/{github-id}/problem-{번호} 브랜치 생성
2. answer/problem{번호}/{github-id}.py 작성
3. master 대상으로 PR 생성
        ↓ (자동)
4. AI가 기본 테스트케이스 실행 후 결과 코멘트
5. AI가 심화 엣지케이스 생성 후 추가 테스트
6. 통과/실패 여부 + 힌트 PR 코멘트로 전달
7. 2학년 멘토가 코드 리뷰 후 승인 → 머지
        ↓ (자동)
8. Cartel_Lab에 해당 학생 정답 처리
```

---

## 문제 파일 형식

`problems/problem{번호}.md` 파일 작성 가이드는 [PROBLEM_GUIDE.md](./PROBLEM_GUIDE.md)를 참고하세요.

---

## 리뷰 규칙

- 학생끼리 리뷰는 가능하지만 **머지는 2학년 멘토만** 가능
- `master` 직접 푸시 금지
- PR 제목 형식: `[problem-001] minsu 제출`

---

자세한 기여 방법은 [CONTRIBUTING.md](./CONTRIBUTING.md)를 참고하세요.
