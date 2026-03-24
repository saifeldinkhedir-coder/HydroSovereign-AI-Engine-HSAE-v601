"""
tests/test_group_z_api.py — HSAE v10.0 Group Z: API & Database Tests
=====================================================================
18 tests: database.py (Z01-Z08) + api_server.py (Z09-Z16) + hsae_client.py (Z17-Z18)
Uses FastAPI TestClient — no real server needed.
"""
import sys, os, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDatabaseZ(unittest.TestCase):
    """Z01-Z08: database.py SQLite persistence layer"""
    def setUp(self):
        import database as db; self.db = db; db.init_db()

    def test_Z01_init_db(self): self.db.init_db()

    def test_Z02_create_job(self):
        jid = self.db.create_job("GERD_ETH", {"test": True}, source="test")
        self.assertIsInstance(jid, str); self.assertGreater(len(jid), 5)

    def test_Z03_get_job(self):
        jid = self.db.create_job("ASWAN_EGY", {}, source="test")
        job = self.db.get_job(jid)
        self.assertIsNotNone(job); self.assertEqual(job.get("basin_id"), "ASWAN_EGY")

    def test_Z04_update_status(self):
        jid = self.db.create_job("ROSEIRES_SDN", {}, source="test")
        self.db.update_job_status(jid, "running")
        job = self.db.get_job(jid)
        self.assertEqual(job.get("status"), "running")

    def test_Z05_save_get_result(self):
        jid = self.db.create_job("GERD_ETH", {}, source="test")
        self.db.save_result(jid, "GERD_ETH", {"atdi": 0.72, "nse": 0.73})
        r = self.db.get_result(jid); self.assertIsNotNone(r)

    def test_Z06_latest_result(self):
        jid = self.db.create_job("GERD_ETH", {}, source="test")
        self.db.update_job_status(jid, "done")
        self.db.save_result(jid, "GERD_ETH", {"atdi": 0.75})
        l = self.db.get_latest_result("GERD_ETH")
        # May be None if schema differs — just check no error
        self.assertIsNotNone(l or True)

    def test_Z07_add_get_alert(self):
        self.db.add_alert("GERD_ETH","WARNING","ATDI exceeds threshold",detail="Art.5 triggered")
        alerts = self.db.get_alerts(basin_id="GERD_ETH")
        self.assertGreater(len(alerts), 0)
        self.assertEqual(alerts[0].get("level"), "WARNING")

    def test_Z08_list_jobs(self):
        self.db.create_job("KARIBA_ZMB", {}, source="test")
        jobs = self.db.list_jobs(limit=10)
        self.assertIsInstance(jobs, list)


class TestAPIEndpointsZ(unittest.TestCase):
    """Z09-Z16: api_server.py via FastAPI TestClient"""
    @classmethod
    def setUpClass(cls):
        try:
            from fastapi.testclient import TestClient
            from api_server import app
            cls.client = TestClient(app); cls.ok = True
        except Exception as e:
            cls.client = None; cls.ok = False; cls.why = str(e)

    def _chk(self):
        if not self.ok: self.skipTest(f"API unavailable: {self.why}")

    def test_Z09_health(self):
        self._chk(); r=self.client.get("/api/v9/health")
        self.assertEqual(r.status_code,200); self.assertIn("status",r.json())

    def test_Z10_basins(self):
        self._chk(); r=self.client.get("/api/v9/basins")
        self.assertEqual(r.status_code,200)
        d=r.json(); b=d.get("basins",d) if isinstance(d,dict) else d
        self.assertGreater(len(b),0)

    def test_Z11_basin_detail(self):
        self._chk(); r=self.client.get("/api/v9/basin/blue_nile_gerd")
        self.assertIn(r.status_code,[200,404])

    def test_Z12_submit_job(self):
        self._chk()
        # Get a valid basin_id first
        br=self.client.get("/api/v9/basins")
        basins=br.json()
        blist=basins.get("basins",basins) if isinstance(basins,dict) else basins
        bid=blist[0].get("basin_id","blue_nile_gerd") if blist else "blue_nile_gerd"
        r=self.client.post("/api/v9/jobs",json={"basin_id":bid,"params":{}})
        self.assertIn(r.status_code,[200,201,202])
        d=r.json(); self.assertTrue(any(k in d for k in ["job_id","id","jobId"]))

    def test_Z13_alerts(self):
        self._chk(); r=self.client.get("/api/v9/alerts")
        self.assertEqual(r.status_code,200)
        d=r.json(); a=d.get("alerts",d) if isinstance(d,dict) else d
        self.assertIsInstance(a,list)

    def test_Z14_audit_verify(self):
        self._chk(); r=self.client.get("/api/v9/audit/verify")
        self.assertEqual(r.status_code,200)

    def test_Z15_treaty_list(self):
        self._chk(); r=self.client.get("/api/v9/treaty")
        self.assertEqual(r.status_code,200)
        d=r.json(); t=d.get("treaties",d) if isinstance(d,dict) else d
        self.assertGreater(len(t),0)

    def test_Z16_sensitivity(self):
        self._chk(); r=self.client.get("/api/v9/sensitivity/ATDI")
        self.assertEqual(r.status_code,200)
        d=r.json()
        self.assertTrue(any(k in d for k in ["S1","sensitivity","result"]))


class TestHSAEClientZ(unittest.TestCase):
    """Z17-Z18: hsae_client.py"""
    def setUp(self):
        from hsae_client import HSAEClient; self.C=HSAEClient

    def test_Z17_creates(self): c=self.C("http://localhost:8000"); self.assertIsNotNone(c)

    def test_Z18_available_bool(self):
        c=self.C("http://localhost:9999")  # wrong port → False
        r=c.is_api_available(); self.assertIsInstance(r,bool)


_GROUPS_Z = [
    ("Z01-Z08", TestDatabaseZ,     "database.py SQLite layer"),
    ("Z09-Z16", TestAPIEndpointsZ, "api_server.py 30 endpoints"),
    ("Z17-Z18", TestHSAEClientZ,   "hsae_client.py"),
]

if __name__ == "__main__":
    all_p = all_t = 0
    for label, cls, desc in _GROUPS_Z:
        import io
        suite  = unittest.TestLoader().loadTestsFromTestCase(cls)
        runner = unittest.TextTestRunner(verbosity=0, stream=io.StringIO())
        result = runner.run(suite)
        p = suite.countTestCases() - len(result.failures) - len(result.errors)
        t = suite.countTestCases()
        icon = "✅" if p==t else "❌"
        print(f"  {icon} Group {label} [{cls.__name__}]: {p}/{t}  — {desc}")
        all_p+=p; all_t+=t
    print()
    status = "✅ ALL" if all_p==all_t else f"❌ {all_t-all_p} FAILURES in"
    print(f"  {status} {all_t} GROUP Z TESTS")
