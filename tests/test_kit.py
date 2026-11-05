from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import kitlib
import publish

PAYLOAD = {'SKILL.md': b'---\nname: product-sprint\ndescription: test\n---\n',
           'references/test.md': b'example'}

def fixture(base: Path) -> dict[str, bytes]:
    files = {'skills/product-sprint/' + k: v for k, v in PAYLOAD.items()}
    files['README.md'] = b'generic preparation only'
    for rel, value in files.items():
        p = base / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(value)
    (base/'MANIFEST.json').write_text(json.dumps({'schema': 1, 'files': {k:kitlib.digest(v) for k,v in files.items()}}))
    return kitlib.verified_files(base)

class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
    def tearDown(self):
        self.tmp.cleanup()
    def test_path_traversal_rejected(self):
        for value in ('../secret', '/etc/x', 'a/../b', 'a\\b', 'C:/x', './x', 'a//b'):
            with self.subTest(value=value), self.assertRaises(kitlib.KitError):
                kitlib.validate_rel(value)
    def test_dry_run_no_directories(self):
        target = self.root/'new'/'product-sprint'
        self.assertEqual(kitlib.install_payload(PAYLOAD,target),'would-install')
        self.assertFalse(target.parent.exists())
    def test_install_all_files(self):
        target = self.root/'skills'/'product-sprint'
        self.assertEqual(kitlib.install_payload(PAYLOAD,target,True),'installed')
        for rel, data in PAYLOAD.items():
            self.assertEqual((target/rel).read_bytes(),data)
    def test_identical_install_is_idempotent(self):
        target = self.root/'skill'
        kitlib.install_payload(PAYLOAD,target,True)
        before=(target/'SKILL.md').stat().st_mtime_ns
        self.assertEqual(kitlib.install_payload(PAYLOAD,target,True),'already-identical')
        self.assertEqual(before,(target/'SKILL.md').stat().st_mtime_ns)
    def test_conflict_never_overwrites(self):
        target=self.root/'skill';kitlib.install_payload(PAYLOAD,target,True)
        (target/'SKILL.md').write_bytes(b'existing user instruction')
        with self.assertRaises(kitlib.KitError):kitlib.install_payload(PAYLOAD,target,True)
        self.assertEqual((target/'SKILL.md').read_bytes(),b'existing user instruction')
    def test_extra_files_are_conflict(self):
        target=self.root/'skill';kitlib.install_payload(PAYLOAD,target,True)
        (target/'custom.md').write_text('keep me')
        with self.assertRaises(kitlib.KitError):kitlib.install_payload(PAYLOAD,target,True)
        self.assertEqual((target/'custom.md').read_text(),'keep me')
    @unittest.skipIf(os.name=='nt','symlink creation may need elevated privileges on Windows')
    def test_symlink_destination_rejected(self):
        outside=self.root/'outside';outside.mkdir();target=self.root/'skill';target.symlink_to(outside,target_is_directory=True)
        with self.assertRaises(kitlib.KitError):kitlib.install_payload(PAYLOAD,target,True)
        self.assertEqual(list(outside.iterdir()),[])
    @unittest.skipIf(os.name=='nt','symlink creation may need elevated privileges on Windows')
    def test_symlink_ancestor_rejected(self):
        outside=self.root/'outside';outside.mkdir();link=self.root/'link';link.symlink_to(outside,target_is_directory=True)
        with self.assertRaises(kitlib.KitError):kitlib.install_payload(PAYLOAD,link/'skill',True)
    def test_failed_staging_does_not_partially_install(self):
        target=self.root/'skills'/'product-sprint';original=Path.write_bytes
        def fail(p,data):
            if p.name=='test.md':raise OSError('synthetic disk error')
            return original(p,data)
        with patch.object(Path,'write_bytes',fail),self.assertRaises(OSError):
            kitlib.install_payload(PAYLOAD,target,True)
        self.assertFalse(target.exists())
        self.assertEqual(list(target.parent.iterdir()),[])
    def test_project_scope_path(self):
        self.assertEqual(kitlib.destination('project','modern',str(self.root)),self.root/'.agents/skills/product-sprint')
    def test_modern_user_scope(self):
        self.assertEqual(kitlib.destination('user','modern',None,home=self.root),self.root/'.agents/skills/product-sprint')
    def test_legacy_codex_home(self):
        self.assertEqual(kitlib.destination('user','legacy',None,home=self.root,codex_home=str(self.root/'custom')),
                         self.root/'custom/skills/product-sprint')
    def test_missing_project_rejected(self):
        with self.assertRaises(kitlib.KitError):kitlib.destination('project','modern',str(self.root/'absent'))
    def test_existing_agent_and_config_unchanged(self):
        (self.root/'AGENTS.md').write_text('platform rules')
        (self.root/'AGENTS.override.md').write_text('higher priority')
        (self.root/'config.toml').write_text('model = "provided"')
        kitlib.install_payload(PAYLOAD,self.root/'.agents/skills/product-sprint',True)
        self.assertEqual((self.root/'AGENTS.md').read_text(),'platform rules')
        self.assertEqual((self.root/'AGENTS.override.md').read_text(),'higher priority')
        self.assertEqual((self.root/'config.toml').read_text(),'model = "provided"')
    def test_manifest_detects_edit(self):
        fixture(self.root);(self.root/'README.md').write_text('edited')
        with self.assertRaises(kitlib.KitError):kitlib.verified_files(self.root)
    def test_unlisted_secret_not_in_payload(self):
        fixture(self.root);(self.root/'.env').write_text('SYNTHETIC_SECRET=not-real')
        files=kitlib.verified_files(self.root)
        self.assertNotIn('.env',files)
    def test_snapshot_only_allowlisted_files(self):
        source=self.root/'source';source.mkdir();files=fixture(source)
        (source/'exam_data.csv').write_text('synthetic unlisted file')
        dest=self.root/'snapshot';publish.make_snapshot(files,dest)
        self.assertFalse((dest/'exam_data.csv').exists())
        self.assertEqual({p.relative_to(dest).as_posix() for p in dest.rglob('*') if p.is_file()},set(files))

class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.files=fixture(self.root)
    def tearDown(self):self.tmp.cleanup()
    def test_preview_never_calls_network_or_git(self):
        with patch.object(publish,'run',side_effect=AssertionError('should not run')):
            result=publish.publish('example-user','new-kit',False,self.root)
        self.assertEqual(result['status'],'preview')
    def test_owner_validation(self):
        for owner,name in [('a/b','test'),('a','../test'),('a','x;rm'),('--bad','okay')]:
            with self.subTest(owner=owner,name=name), self.assertRaises(kitlib.KitError):
                publish.checked_identity(owner,name)
    def test_wrong_authenticated_account_stops(self):
        with patch.object(publish.shutil,'which',return_value='/mock/tool'),patch.object(publish,'run',return_value=subprocess.CompletedProcess([],0,'someone-else\n','')) as r:
            with self.assertRaises(kitlib.KitError):publish.publish('example-user','new-kit',True,self.root)
            self.assertEqual(r.call_count,1)
    def test_existing_repository_stops(self):
        results=[subprocess.CompletedProcess([],0,'example-user',''),subprocess.CompletedProcess([],0,'HTTP 200','')]
        with patch.object(publish.shutil,'which',return_value='/mock/tool'),patch.object(publish,'run',side_effect=results) as r:
            with self.assertRaises(kitlib.KitError):publish.publish('example-user','new-kit',True,self.root)
            self.assertEqual(r.call_count,2)
    def test_unknown_http_error_stops(self):
        results=[subprocess.CompletedProcess([],0,'example-user',''),subprocess.CompletedProcess([],1,'','HTTP 403')]
        with patch.object(publish.shutil,'which',return_value='/mock/tool'),patch.object(publish,'run',side_effect=results):
            with self.assertRaises(kitlib.KitError):publish.publish('example-user','new-kit',True,self.root)
    @unittest.skipUnless(shutil.which('git'),'Git required for local integration test')
    def test_publish_flow_uses_clean_snapshot_with_mocked_github(self):
        actual_run=publish.run;calls=[]
        def fake(args,cwd=None,check=True):
            calls.append(args)
            if args[0]=='git':return actual_run(args,cwd,check)
            if args[:3]==['gh','api','user']:return subprocess.CompletedProcess(args,0,'example-user','')
            if '--include' in args:return subprocess.CompletedProcess(args,1,'HTTP/2 404','')
            if args[:3]==['gh','repo','create']:
                source=Path(args[args.index('--source')+1])
                self.assertFalse((source/'exam_data.csv').exists())
                self.assertTrue((source/'MANIFEST.json').is_file())
                return subprocess.CompletedProcess(args,0,'created','')
            if '/git/trees/' in args[2]:
                data={'truncated':False,'tree':[{'type':'blob','path':p} for p in self.files]}
            else:data={'private':False}
            return subprocess.CompletedProcess(args,0,json.dumps(data),'')
        (self.root/'exam_data.csv').write_text('synthetic unlisted data')
        with patch.object(publish.shutil,'which',return_value='/mock/tool'),patch.object(publish,'run',side_effect=fake):
            result=publish.publish('example-user','new-kit',True,self.root)
        self.assertEqual(result['status'],'published-and-verified')
        self.assertEqual(len(result['commit']),40)
        self.assertIn('/tree/'+result['commit']+'/',result['codex_message'])
        self.assertFalse(any('--force' in c for c in calls))

class ContentTests(unittest.TestCase):
    def test_release_manifest_matches(self):
        self.assertIn('README.md',kitlib.verified_files(ROOT))
    def test_external_files_match_original_git_blobs(self):
        doc=json.loads((ROOT/'skills/product-sprint/UPSTREAM.json').read_text())
        for source in doc['sources']:
            for item in source['local_entries']:
                with self.subTest(path=item['local_path']):
                    b=(ROOT/item['local_path']).read_bytes()
                    sha=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
                    self.assertEqual(sha,item['expected_upstream_git_blob'])
    def test_self_contained_skill_reference_paths(self):
        import re
        text=(ROOT/'skills/product-sprint/SKILL.md').read_text()
        for rel in re.findall(r'`(references/[A-Za-z0-9_./-]+\.md)`',text):
            with self.subTest(path=rel):self.assertTrue((ROOT/'skills/product-sprint'/rel).is_file())
    def test_skill_frontmatter_and_explicit_invocation(self):
        s=(ROOT/'skills/product-sprint/SKILL.md').read_text()
        self.assertTrue(s.startswith('---\nname: product-sprint\ndescription:'))
        self.assertIn('allow_implicit_invocation: false',(ROOT/'skills/product-sprint/agents/openai.yaml').read_text())
    def test_browser_smoke_no_capture_or_sandbox_bypass(self):
        s=(ROOT/'skills/product-sprint/scripts/browser_smoke.py').read_text()
        self.assertIn("'chromium_sandbox': True",s)
        for forbidden in ('.screenshot(', 'record_video_dir=', '.tracing.start(', 'storage_state=', '--no-sandbox'):
            self.assertNotIn(forbidden,s)

if __name__=='__main__':unittest.main()
