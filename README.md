# Product Sprint Kit

**한 번 설치하고 `$product-sprint`로 시작하는 Codex용 개발·이해·사용성 검수 세트입니다.**
기능 구현, 중요한 선택에 대한 사용자 이해, 실제 업무 수행 검수를 함께 진행합니다.
특정 시험의 문제·정답·데이터·회사 자산이나 완성된 앱을 포함하지 않습니다.
대회 공식 도구가 아니며, 성적·무결점·모든 Codex 버전 호환을 보장하지 않습니다.

## 지금 개인 PC에서 할 일
이 폴더를 VS Code로 열고 Codex에 다음 한 문장을 전달하십시오.

> START_HERE.md를 읽고 준비·검증을 진행한 뒤 공개 저장소에 게시하십시오. 기존 설정과 저장소는 덮어쓰지 마십시오.

GitHub 로그인은 개인 PC에서만 합니다. 이 대화의 GitHub 연결은 개인 PC의 gh 로그인이나 시험 Codex의 설치를 대신하지 않습니다.

## 게시 후 다른 Codex에서 사용하는 법
**공개 주소를 알려주는 것, 설치하는 것, 스킬을 실행하는 것은 서로 다른 단계입니다.**

Codex 대화창(일반 쉘이 아님)에서 다음을 하나의 메시지로 전달하십시오.

```text
$skill-installer https://github.com/Jinseong1126/codex-product-sprint-kit/tree/main/skills/product-sprint 의 스킬 하나를 설치하십시오. Codex 업데이트와 보안 설정 변경은 하지 마십시오. 설치 제한을 우회하지 말고 실제 인식을 확인하십시오.
```

위 주소는 **게시 성공 전에는 존재하지 않는 예정 주소**입니다. 게시 도구가 출력한 고정 커밋 주소를 쓰면 더 재현 가능합니다.
설치 후 `/skills` 또는 `$` 목록에서 `product-sprint`를 확인하십시오. 안 보이면 제공된 Codex를 재시작하십시오.
실제 과제 폴더에서 다음을 입력하십시오.

```text
$product-sprint 과제 안내를 먼저 읽고 시작하십시오. 중요한 선택은 제가 이해하도록 설명하고, 사소한 구현은 자율적으로 진행하십시오.
```

`$skill-installer`가 없으면 [INSTALL.md](INSTALL.md)의 다운로드·로컬 설치 경로를 사용하십시오.
도구나 다운로드가 규정상 금지되면 다른 방법으로 우회하지 마십시오.

## 무엇이 실제 들어 있습니까?
- **product-sprint** 하나의 설치 가능한 스킬. 내부에서 역할·단계에 맞는 참고문서만 읽습니다.
- 중요한 선택을 짧게 설명하고 사용자의 실제 판단을 구분하는 절차.
- 화면별 상태·중심 행동·회복 경로를 정의하는 제품 UI 지침.
- 소스를 읽지 않은 독립 검토자의 업무 수행 검사와 별도의 인간 검수.
- 파일 소유권, API 계약, 인계·재접속, 시간·리소스 관리.
- 실행·Docker·최종 요구사항 근거와 실제 이해를 확인하는 제출 점검.
- 공개 원문의 **Impeccable distill·clarify 참고문서**와 **Superpowers 완료 전 검증 문서**. 출처·커밋·라이선스를 함께 보존합니다.
- 비파괴 설치기, 준비물만 게시하는 도구, 합성 페이지의 실제 브라우저 동작 확인 스크립트와 테스트.

Impeccable 전체 CLI/플러그인, Superpowers 전체, 브라우저 실행기, Codex 모델은 포함하지 않습니다.
내장 참고문서를 쓰는 데 별도 npm 설치는 필요 없습니다. 브라우저 검사는 환경에 이미 있는 허용 도구를 우선 사용합니다.

## 설치 범위
기본 권장: 개인 PC에서는 사용자 범위, 시험에서는 규정이 허용하는 프로젝트 또는 사용자 범위.
프로젝트: `.agents/skills/product-sprint`; 최신 사용자 범위: `~/.agents/skills/product-sprint`.
구형 제공 버전용 선택지는 `$CODEX_HOME/skills`(기본 `~/.codex/skills`)입니다.
한 환경에 중복 설치하지 마십시오. 설치기는 Codex 버전이나 전역 AGENTS.md를 바꾸지 않습니다.
같은 머신/사용자 범위가 유지될 때만 재사용되며, 새 시험 컨테이너에는 별도 설치가 필요합니다.

## 안전과 공개 범위
시험 문제, 데이터, 화면, 계정, 쿠키, 개인 정보, 답안, 작업 이력, 제출 앱은 이 저장소에 넣거나 push하지 마십시오.
공개 준비물과 비공개 작업 폴더를 분리하십시오. 자동 캡처·영상·외부 브라우저·텔레메트리는 사용하지 않습니다.
실제 시험에서는 당일 설치·자료·자동화 규정을 우선하며, 독립 답변 단계에서는 AI를 중단하십시오.
자료를 공개 유지해야 하는 기간도 운영 지침을 따르십시오.

## 검증
```bash
python -m unittest discover -s tests -v
python tools/install.py --scope project --project /path/to/practice       # 미리보기
python tools/install.py --scope project --project /path/to/practice --apply
python skills/product-sprint/scripts/browser_smoke.py                    # 선택: 실행 가능한 Playwright 필요
```
[검증 결과와 한계](TEST_REPORT.md) · [설치 상세](INSTALL.md) · [외부 출처](THIRD_PARTY.md)
