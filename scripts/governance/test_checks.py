import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from checks import classify, aggregate, diff, migrations, ROOT, MIGRATION_OVERRIDES
from migration_preflight import assess


class PolicyTests(unittest.TestCase):
    def test_migration_preflight(self):
        self.assertEqual(assess("1138237749", "1", "MISSING", "0", "0")[0], "READY_UPGRADE")
        self.assertEqual(assess("1138237749", "1", "MISSING", "1", "1")[0], "READY_UPGRADE")
        self.assertEqual(assess("1138237749", "1", "1", "1", "1")[0], "READY_CURRENT")
        self.assertEqual(assess("-1994966056", "1", "MISSING", "1", "1")[0], "BLOCK_CANDIDATE_CHECKSUM")
        self.assertEqual(assess("42", "1", "MISSING", "0", "0")[0], "BLOCK_UNKNOWN_CHECKSUM")
        self.assertEqual(assess("1138237749", "0", "MISSING", "0", "0")[0], "BLOCK_FAILED_HISTORY")
        self.assertEqual(assess("1138237749", "1", "MISSING", "1", "0")[0], "BLOCK_INDEX_CONFLICT")
        self.assertEqual(assess("1138237749", "1", "0", "1", "1")[0], "BLOCK_FAILED_COMPENSATION")
        self.assertEqual(assess("1138237749", "1", "1", "0", "0")[0], "BLOCK_MISSING_INDEX")

    def test_classification(self):
        self.assertEqual(classify(["docs/readme.md"]), dict(backend=False, web=False, mobile=False))
        self.assertEqual(classify(["frontend/packages/web/src/a.vue"]), dict(backend=False, web=True, mobile=False))
        self.assertEqual(classify(["frontend/packages/lib-shared/a.ts"]), dict(backend=False, web=True, mobile=True))
        self.assertTrue(all(classify(["scripts/governance/checks.py"]).values()))
        self.assertTrue(all(classify(["docs/readme.md"], full=True).values()))
        self.assertTrue(classify(["backend/crm/X.java"])["backend"])

    def test_aggregate(self):
        flags = dict(backend=False, web=True, mobile=False)
        results = dict(policy="success", classify="success", backend="skipped", web="success", mobile="skipped")
        aggregate(flags, results)
        for job, outcome in [("classify", "failure"), ("web", "skipped"), ("web", "cancelled"), ("policy", "failure")]:
            with self.assertRaises(ValueError):
                aggregate(flags, dict(results, **{job: outcome}))

    def test_migration_scopes(self):
        original = os.getcwd()
        with tempfile.TemporaryDirectory() as directory:
            os.chdir(directory)
            try:
                def git(*args):
                    return subprocess.check_output(["git", *args], text=True).strip()
                git("init", "-q")
                git("config", "user.email", "test@example.invalid")
                git("config", "user.name", "Test")
                first = Path(ROOT + "1.9.1/ddl/V1.9.1_2__init.sql")
                first.parent.mkdir(parents=True)
                first.write_text("SELECT 1;")
                git("add", ".")
                git("commit", "-qm", "baseline")
                base = git("rev-parse", "HEAD")
                first.write_text("SELECT 2;")
                migrations(base, "committed")
                with self.assertRaises(ValueError):
                    migrations(base, "worktree")
                git("add", ".")
                with self.assertRaises(ValueError):
                    migrations(base, "staged")
                first.write_text("SELECT 1;")
                git("add", ".")
                new = first.with_name("V1.9.1_3__addition.sql")
                new.write_text("SELECT 3;")
                migrations(base, "worktree")
                self.assertIn(("A", str(new)), diff(base, "worktree", ROOT))
                duplicate = new.with_name("V1.9.1_3_0__duplicate.sql")
                duplicate.write_text("SELECT 3;")
                with self.assertRaises(ValueError):
                    migrations(base, "worktree")
                duplicate.unlink()
                new.rename(new.with_name("V1.9.1_1__out_of_order.sql"))
                with self.assertRaises(ValueError):
                    migrations(base, "worktree")
                Path(ROOT + "1.9.1/ddl/V1.9.1_1__out_of_order.sql").unlink()

                compatible = first.with_name("V1.9.1_9000__compatible.sql")
                compatible.write_text("SELECT 9000;")
                first.write_text("SELECT 2;")
                manifest = Path(MIGRATION_OVERRIDES)
                manifest.parent.mkdir(parents=True)
                entry = {
                    "path": str(first),
                    "baseline_sha256": hashlib.sha256(b"SELECT 1;").hexdigest(),
                    "restored_sha256": hashlib.sha256(b"SELECT 2;").hexdigest(),
                    "reason": "test-only compatibility restoration",
                }
                manifest.write_text(json.dumps({"overrides": [entry]}))
                migrations(base, "worktree")

                manifest.unlink()
                with self.assertRaises(ValueError):
                    migrations(base, "worktree")
                manifest.write_text(json.dumps({"overrides": [dict(entry, baseline_sha256="0" * 64)]}))
                with self.assertRaises(ValueError):
                    migrations(base, "worktree")
                manifest.write_text(json.dumps({"overrides": [dict(entry, restored_sha256="0" * 64)]}))
                with self.assertRaises(ValueError):
                    migrations(base, "worktree")
                manifest.write_text(json.dumps({"overrides": [entry]}))
                first.write_text("SELECT 3;")
                with self.assertRaises(ValueError):
                    migrations(base, "worktree")
                with self.assertRaises(subprocess.CalledProcessError):
                    diff("missing-reference", "committed")
            finally:
                os.chdir(original)
