#!/usr/bin/env python3
"""Verify only release allowlisted files; does not upload anything."""
from __future__ import annotations
import hashlib
import json
import sys
from kitlib import verified_files, KitError

def main() -> int:
    try:
        files = verified_files()
        upstream = json.loads(files['skills/product-sprint/UPSTREAM.json'])
        count = 0
        for source in upstream['sources']:
            for item in source['local_entries']:
                data = files[item['local_path']]
                blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
                if blob != item['expected_upstream_git_blob']:
                    raise KitError('Upstream bytes mismatch: ' + item['local_path'])
                count += 1
        print(json.dumps({'integrity': 'pass', 'allowlisted_files': len(files),
                          'upstream_blobs_verified': count,
                          'note': 'Checksums detect accidental changes; this is not a security signature or Codex runtime validation.'}, indent=2))
        return 0
    except (KitError, OSError, KeyError, ValueError) as exc:
        print('STOP: ' + str(exc), file=sys.stderr)
        return 2
if __name__ == '__main__':
    raise SystemExit(main())
