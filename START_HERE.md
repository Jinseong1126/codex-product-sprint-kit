# 개인 PC에서 준비·게시하십시오
이 파일은 **시험 전 개인 환경 전용**입니다. 시험 안에서는 INSTALL.md만 사용하고 게시하지 마십시오.
사용자는 이 준비물을 새 공개 저장소로 게시하도록 요청했습니다. 범용 파일의 공개만 허용되며 현재 개발 프로젝트나 시험 자료의 공개는 허용되지 않습니다.

1. 현재 폴더가 이 준비물 저장소인지 확인하고 README.md, MANIFEST.json을 읽으십시오. 시험/기존 앱 폴더에서는 중단하십시오.
2. `python tools/verify.py`와 `python -m unittest discover -s tests -v`를 실행하십시오.
3. `python tools/doctor.py`로 Codex·Python·브라우저·GitHub CLI 가용성을 확인하십시오. 비밀값을 읽거나 출력하지 마십시오.
4. 현재 Codex의 실제 스킬 경로를 확인하십시오. 최신 사용자 범위라면 `python tools/install.py --scope user`로 미리 본 뒤 `--apply`로 설치하십시오. 구형 Codex가 공식/실제 환경에서 legacy 경로를 쓰는 것이 확인될 때만 `--layout legacy`를 지정하십시오. 글로벌 AGENTS.md·config.toml·버전을 변경하지 마십시오.
5. 스킬 목록에서 product-sprint의 인식을 확인하십시오. 필요하면 사용자가 현재 작업을 저장한 후 새 세션을 시작하도록 안내하십시오. 파일 존재와 모델 인식은 별도로 보고하십시오.
6. 허용된 기존 브라우저 도구를 사용하십시오. Python Playwright가 이미 동작하면 합성 페이지 `skills/product-sprint/scripts/browser_smoke.py`를 실행하십시오. 없으면 docs/BROWSER.md의 대안을 확인하십시오. 새 설치는 내용·용량·목적을 설명하고 허가를 얻은 경우에만 수행하십시오. 보안 우회 옵션은 사용하지 마십시오.
7. 작은 합성 과제로 references/REHEARSAL.md의 행동 검증을 하십시오. 파일 설치 성공을 제품 품질 검증이라고 보고하지 마십시오.
8. `python tools/publish.py --owner Jinseong1126 --name codex-product-sprint-kit`의 미리보기를 확인한 뒤 `--apply`로 게시하십시오. 게시 전 완성 앱이나 실제 문제 자료를 추가하지 마십시오. 게시기는 MANIFEST.json에 고정된 준비물만 새 임시 Git 트리에 복사하므로 주변 폴더나 기존 이력을 올리지 않습니다.
9. gh가 없거나 개인 GitHub 인증이 없으면 자동 설치·자격 증명 요구를 하지 말고, 필요한 한 단계만 사용자에게 알리십시오. 기존 이름의 저장소가 있으면 덮어쓰지 말고 중단하십시오.
10. 성공 시 공개 URL, 커밋 SHA, 고정 커밋 스킬 설치 문장, 실제 인식/브라우저 결과와 미검증 사항을 짧게 보고하십시오. 가능하면 새 연습 폴더에서 다시 받아 설치하고 재확인하십시오.

진행 보고는 '완료 / 남은 한 단계 / 제가 확인할 항목'으로 짧게 작성하십시오.
설정 파일을 바꾸고도 바꾸지 않았다고 말하거나, 로컬 파일을 GitHub에 올렸다고 혼동하지 마십시오.
