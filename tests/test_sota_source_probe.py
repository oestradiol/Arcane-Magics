from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class FakeHeaders(dict):
    def get(self,key,default=None): return super().get(key,default)

class FakeResponse:
    status=200
    headers=FakeHeaders({'ETag':'etag-1','Last-Modified':'Thu, 24 Sep 2026 12:00:00 GMT','Content-Type':'text/plain'})
    def __init__(self,body=b'hello',url='https://example.test/final'): self.body=body; self.url=url
    def __enter__(self): return self
    def __exit__(self,*args): return False
    def read(self,n=-1): return self.body if n<0 else self.body[:n]
    def geturl(self): return self.url

class SOTASourceProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec=importlib.util.spec_from_file_location('probe',ROOT/'scripts'/'probe_sota_sources.py')
        cls.mod=importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(cls.mod)

    def test_probe_hashes_observation_without_authority(self):
        opener=lambda req,timeout=20: FakeResponse()
        state={'entries':[{'id':'x','area':'test','last_checked':'2026-09-24','status':'WATCH','sources':['https://example.test']}]}
        report=self.mod.build_report(state,opener=opener,observed_at='2026-09-24T12:00:00+00:00')
        src=report['entries'][0]['sources'][0]
        self.assertTrue(src['ok'])
        self.assertEqual(len(src['body_sha256']),64)
        self.assertFalse(report['authority'])

    def test_probe_records_failure_without_promoting_interpretation(self):
        def opener(req,timeout=20): raise OSError('offline')
        state={'entries':[{'id':'x','sources':['https://example.test']}]}
        report=self.mod.build_report(state,opener=opener)
        self.assertFalse(report['entries'][0]['all_reachable'])
        self.assertEqual(report['entries'][0]['sources'][0]['error_type'],'OSError')
        self.assertFalse(report['authority'])

if __name__=='__main__': unittest.main()
