# 실제 GitHub 게시

이 도구는 **개인 PC에서 새 공개 준비물 저장소를 만드는 것만** 지원합니다.
이 ChatGPT 연결의 로그인과 개인 PC의 GitHub CLI 로그인은 별개입니다.

```bash
python tools/publish.py --owner Jinseong1126 --name codex-product-sprint-kit
python tools/publish.py --owner Jinseong1126 --name codex-product-sprint-kit --apply
```
첫 명령은 네트워크도 쓰지 않고 파일 목록만 보여줍니다. 두 번째는 실제 공개 게시입니다.
gh/git가 있어야 하며, 로그인한 개인 계정이 owner와 다르면 중단합니다.
새로 로그인해야 한다면 개인 PC에서 GitHub CLI의 정상 웹 로그인 절차를 사용하십시오.
인증 토큰을 채팅에 붙이거나 환경 변수 값을 출력하지 마십시오.

게시기는 임시 Git 저장소에 고정 MANIFEST 파일만 복사하고 새 저장소로 올립니다.
원래 폴더의 Git 이력·추가 앱 파일·시험 파일은 포함하지 않습니다.
기존 이름이 있으면 덮어쓰지 않고 중단하며 기존 저장소를 공개로 바꾸지 않습니다.
생성·push 후 공개 여부와 원격 파일 목록을 확인한 경우에만 성공이라고 출력합니다.
실패 시 저장소가 일부 생성됐을 수 있으므로 삭제·force push·재실행으로 덮지 말고 먼저 확인하십시오.

완료 출력에는 공개 URL, 커밋 SHA, 고정 커밋의 스킬 설치 문장이 있습니다.
그 문장을 개인 연습의 새 Codex 환경에서 시험하십시오. 문구를 외울 필요는 없습니다.
시험에서는 허용된 공개 자료로 가져오기만 하며 이 게시 스크립트를 실행하거나 결과물을 push하지 마십시오.

GitHub CLI 공식 근거: https://cli.github.com/manual/gh_repo_create
