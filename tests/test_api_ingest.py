import io
from starlette.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_ready():
    res = client.get('/api/ready')
    assert res.status_code == 200

# Basic ingest test (mocked storage requires emulator running)
def test_ingest_no_file():
    res = client.post('/api/ingest/')
    assert res.status_code == 400 or res.status_code == 422
