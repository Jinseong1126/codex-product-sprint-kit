# 브라우저는 별도 실행 능력입니다
이 스킬의 설치가 Playwright/Chromium/agent-browser를 자동 설치하지는 않습니다.
제공된 브라우저 도구가 있으면 우선 사용하십시오. Node Playwright, Python Playwright, agent-browser 중 하나면 충분합니다.
개인 연습에서 새 도구 설치가 필요하면 내용·크기·목적을 확인한 뒤 허가받아 설치하십시오.
시험에서는 실제 허용 범위가 우선이며 새 바이너리/캡처/DOM 조회/다운로드가 모두 자동 허용되는 것이 아닙니다.

포함된 Python smoke는 이미 설치된 Playwright와 허용된 Chromium으로 로컬 합성 페이지를 테스트합니다.
```bash
python skills/product-sprint/scripts/browser_smoke.py
# 시스템 Chromium을 사용해야 하는 경우에만:
python skills/product-sprint/scripts/browser_smoke.py --executable /absolute/path/to/chromium
```
카메라·스크린샷·영상·trace·인증상태 저장이나 외부 사이트 접속을 하지 않습니다.
브라우저 OS 샌드박스를 켜고 실행하며, 실패하면 비활성화해 우회하지 않습니다.
이 테스트 통과는 제품 UI 품질·시험 허용·인간 사용성 입증이 아닙니다.

공식 참고:
- https://playwright.dev/python/docs/intro
- https://playwright.dev/docs/intro
- https://agent-browser.dev/installation
- https://github.com/vercel-labs/agent-browser

원본 dogfood에는 캡처·영상 절차가 있습니다. 이 묶음은 해당 스킬을 설치하지 않고,
references/BLIND_REVIEW.md의 규정 우선·독립 목표 검사만 사용합니다.
