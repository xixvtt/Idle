<div align="center">

🌐 [English](README.md) | [中文](README.zh.md) | [Español](README.es.md) | **한국어** | [Português](README.pt-BR.md)

# Idle — Claude Code 토큰 모니터

**macOS에서 동작하는 [Claude Code](https://claude.com/claude-code) 전용 실시간 토큰 사용량 및 세션 모니터.**
화면 구석에 떠 있는 작은 반투명 캡슐이 모든 Claude Code 세션의 토큰 사용량을 실시간으로 보여줍니다.

<img src="docs/images/hero.png" alt="Idle Claude Code 토큰 모니터가 macOS 위젯 옆에 떠 있는 모습" width="720" />

[![Last commit](https://img.shields.io/github/last-commit/xixvtt/Idle)](https://github.com/xixvtt/Idle/commits/main)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

</div>

---

## Idle이란?

Idle은 무료 오픈소스 **Claude Code 토큰 사용량 모니터**입니다. macOS 위에 반투명 플로팅 오버레이로 동작하며 다음을 추적합니다:

- **오늘 누적 Claude Code 토큰 사용량** — 모든 세션·모든 프로젝트 합산을 실시간 표시
- **활성 세션 추적** — 어떤 Claude Code workspace가 실행 중·대기 중·유휴 상태인지 한눈에 확인
- **다중 세션 모니터링** — 열려 있는 모든 Claude Code 세션을 한 줄씩 스택 뷰로 표시
- **완료 알림** — Claude Code 작업이 끝나는 즉시 알림

YOLO 모드로 Claude Code를 쓰다가 자신도 모르게 일일 토큰 한도를 다 써버린 적이 있다면, Idle이 해답입니다. 브라우저 탭도, 대시보드도, API key도 필요 없습니다 — 데스크톱 위에서 바로 확인하세요.

<div align="center">
  <img src="docs/images/solo.png" alt="유휴 모드에서 오늘의 Claude Code 토큰 누적을 보여주는 Idle" width="380" />
</div>

## Claude Code에 Idle이 필요한 이유

| 문제 | Idle의 해결 |
|---|---|
| Anthropic은 일별 토큰 사용량을 노출하지 않음 | Idle이 로컬 Claude Code transcript를 읽어 오늘 총합을 실시간 계산 |
| 여러 `claude` 세션을 동시에 띄우면 사용량 추적 불가능 | Idle이 활성 세션 전부를 한 창에 스택으로 표시 |
| 한도 도달은 Claude가 응답을 멈춰야만 알 수 있음 | Idle이 실시간 토큰 수를 항상 표시 |
| 다른 모니터링 도구는 API key나 클라우드 전송을 요구 | Idle은 100% 로컬 — 외부 네트워크·API key 모두 불필요 |

## 설치 (제로 셋업)

최신 버전 다운로드: **[Releases 페이지 →](https://github.com/xixvtt/Idle/releases)**

| Mac | 파일 |
|---|---|
| Apple Silicon (M1/M2/M3/M4) | `Idle-x.x.x-arm64.zip` |
| Intel | `Idle-x.x.x-x64.zip` |

1. zip을 더블클릭해 `Idle.app` 압축 해제
2. **`Idle.app` 우클릭 → 열기 → 열기** (서명되지 않은 앱이므로 Gatekeeper가 한 번 묻습니다)
3. 첫 실행 시 테마 선택
4. Claude Code를 평소처럼 사용 — 토큰 추적이 즉시 시작됨

Python도, 터미널도, JSON 편집도 필요 없습니다. 내장 daemon과 Claude Code hooks가 자동 설치됩니다.

### "Apple이 Idle에 악성코드가 없음을 확인할 수 없습니다" 오류

macOS Gatekeeper가 서명되지 않은 앱을 차단해서 나오는 메시지입니다. 터미널에서 다음 명령을 실행해 quarantine 플래그를 제거하세요:

```bash
xattr -cr /Applications/Idle.app
# 다른 위치에 압축 해제했다면:
xattr -cr ~/Downloads/Idle.app
```

이후 `Idle.app`을 더블클릭하면 정상 실행됩니다.

여전히 차단된다면 **시스템 설정 → 개인 정보 보호 및 보안**으로 이동, 맨 아래로 스크롤하면 "Idle이(가) 차단되었습니다…" 옆에 **확인 없이 열기** 버튼이 있습니다. 한 번 클릭하면 됩니다.

> 추후 정식 Apple 코드 서명 및 공증을 적용할 예정입니다. 현재는 Apple Developer 멤버십 비용($99/년) 때문에 미서명 상태로 배포 중이며, 사용자가 충분히 늘면 비용을 부담하고 위 단계가 사라집니다.

## 요구 사항

- macOS 12 이상
- [Claude Code](https://claude.com/claude-code) 설치 완료

## Idle은 Claude Code를 어떻게 모니터링하는가 (기술 설명)

Idle은 두 가지 로컬 데이터 소스만 사용합니다:

1. **Claude Code hooks** — Claude Code는 tool 사용·권한 요청·작업 완료 시 shell hook을 실행합니다. Idle의 내장 daemon이 `127.0.0.1:7777`에서 이를 수신해 세션 상태를 실시간 업데이트합니다.
2. **Transcript JSONL 파일** — Claude Code는 전체 세션 transcript를 `~/.claude/projects/`에 기록합니다. Idle은 각 assistant 메시지의 `usage` 필드(input + output + cache_creation 토큰)만 파싱하며, 로컬 타임존 기준 오늘 날짜만 필터링합니다.

이 파일들에서 실행 시 한 번, 이후 30초마다 토큰 총합을 재계산하므로 daemon이나 Idle을 재시작해도 정확합니다.

## 개인정보 보호

- **외부 네트워크 송신 0건.** Daemon은 `127.0.0.1`에만 바인딩.
- **API key 불필요.** Idle은 Anthropic API를 호출하지 않습니다.
- **prompt나 응답 본문은 절대 읽지 않음.** 토큰 카운트 필드만 읽으며 AST 단위 테스트로 강제 보장.
- **오픈소스 (MIT).** 직접 감사할 수 있습니다.

## 이 repo에 ⭐ 한 번

Idle이 Claude Code의 시간이나 비용을 절약해줬다면 repo에 star를 눌러주세요 — 더 많은 Claude Code 사용자가 이 프로젝트를 발견하는 가장 큰 신호입니다. 이슈, PR, 피드백 환영합니다.

---

**키워드:** Claude Code, Claude Code 토큰 모니터, Claude Code 사용량 트래커, Anthropic 토큰 사용량, Claude Code dashboard, Claude Code 모니터링, Claude Code 세션 관리, Claude Code 한도 트래커, Claude Code macOS, Claude Code 오버레이.
