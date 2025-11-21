"""
Local test harness to run the worker and processor for CI or local testing.
Run with: python tests/local/worker_harness.py
"""
import threading
import time
from src.pipelines.worker import run_worker
from src.api.main import app
import uvicorn


def start_api():
    uvicorn.run(app, host='0.0.0.0', port=8000)


def start_worker():
    run_worker()


if __name__ == '__main__':
    # start API in a thread and worker in main thread
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()
    print('API started in thread')
    try:
        start_worker()
    except KeyboardInterrupt:
        print('Stopping harness')
