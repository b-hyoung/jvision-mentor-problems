# Contributing Guide

## 기본 원칙

- 모든 작업은 브랜치에서 진행합니다.
- `master` 브랜치 직접 수정은 금지합니다.
- 학생은 자신의 브랜치만 사용합니다.
- 다른 학생의 답안 파일은 수정하지 않습니다.

## 브랜치 네이밍

- 학생: `student/{github-id}/problem-{번호}`
- 멘토: `mentor/{github-id}/problem-{번호}`

예시:

- `student/jiwoo/problem-002`
- `mentor/hyung/problem-010`

## 문제 파일 규칙

- 문제 설명 파일 위치: `problems/problem{번호}.md`
- 예시: `problems/problem001.md`

## 답안 파일 규칙

- 답안 위치: `answer/{번호}/`
- 파일명: `{github-id}.py`
- 예시: `answer/001/minsu.py`

여러 언어를 허용할 경우 확장자만 언어에 맞게 변경합니다.

## Pull Request 규칙

- 제목 예시: `[problem-001] minsu 제출`
- 대상 브랜치: `master`
- PR 설명에는 문제 번호와 제출 파일 경로를 적습니다.

## 리뷰 규칙

- 학생 간 리뷰 허용
- 머지 조건: 멘토 승인 2회
- 관리자는 운영상 필요한 경우 직접 처리 가능
