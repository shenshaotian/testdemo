import os
import threading
from typing import Optional

import requests
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from common.tools import get_project_path
from test_platform.runner import run_tests
from test_platform.storage import (
    create_run,
    get_run,
    get_stats,
    init_db,
    list_runs,
    now_str,
    update_run,
)

app = FastAPI(title="接口自动化测试平台", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_run_lock = threading.Lock()
_is_running = False

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
REPORT_HISTORY_DIR = os.path.join(get_project_path(), "report", "history")
os.makedirs(REPORT_HISTORY_DIR, exist_ok=True)


class RunRequest(BaseModel):
    target: str = Field(default="testcases", description="pytest 目标路径")
    markers: Optional[str] = Field(default=None, description="pytest -m 标记")
    keyword: Optional[str] = Field(default=None, description="pytest -k 关键字")
    notify: bool = Field(default=False, description="是否发送飞书通知")


def _report_url(run_id: str) -> str:
    host = os.environ.get("PLATFORM_HOST", "http://127.0.0.1:8088")
    return f"{host}/reports/{run_id}/html/index.html"


def _send_feishu(webhook_url: str, run: dict, report_url: str):
    if not webhook_url:
        return
    status_text = "通过" if run["status"] == "success" else "失败"
    content = (
        f"**任务 ID：** {run['id']}\n"
        f"**状态：** {status_text}\n"
        f"**结果：** {run['passed']}/{run['total']} 通过\n"
        f"**报告：** {report_url}"
    )
    payload = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"content": "接口自动化测试报告", "tag": "plain_text"},
                "template": "green" if run["status"] == "success" else "red",
            },
            "elements": [
                {"tag": "div", "text": {"content": content, "tag": "lark_md"}},
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {"content": "查看报告", "tag": "plain_text"},
                            "type": "primary",
                            "url": report_url,
                        }
                    ],
                },
            ],
        },
    }
    try:
        requests.post(webhook_url, json=payload, timeout=10)
    except requests.RequestException:
        pass


def _execute_run(
    run_id: str,
    target: str,
    markers: Optional[str],
    keyword: Optional[str],
    notify: bool,
):
    global _is_running
    try:
        update_run(run_id, status="running")
        result = run_tests(run_id, target=target, markers=markers, keyword=keyword)

        status = "success" if result.exit_code == 0 else "failed"
        update_run(
            run_id,
            status=status,
            total=result.total,
            passed=result.passed,
            failed=result.failed,
            broken=result.broken,
            skipped=result.skipped,
            exit_code=result.exit_code,
            finished_at=now_str(),
        )

        if notify:
            webhook = os.environ.get("FEISHU_WEBHOOK_URL", "")
            run = get_run(run_id)
            if run:
                _send_feishu(webhook, run, _report_url(run_id))
    except Exception as exc:
        update_run(
            run_id,
            status="error",
            error_message=str(exc),
            finished_at=now_str(),
        )
    finally:
        _is_running = False


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
async def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/reports/{run_id}")
def redirect_report(run_id: str):
    return RedirectResponse(url=f"/reports/{run_id}/html/index.html")


@app.get("/api/stats")
def api_stats():
    return get_stats()


@app.get("/api/runs")
def api_list_runs(limit: int = 50):
    return {"runs": list_runs(limit=limit)}


@app.get("/api/runs/{run_id}")
def api_get_run(run_id: str):
    run = get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="任务不存在")
    return run


@app.post("/api/runs")
def api_create_run(body: RunRequest, background_tasks: BackgroundTasks):
    global _is_running

    if not _run_lock.acquire(blocking=False):
        raise HTTPException(status_code=409, detail="已有任务正在执行，请稍后再试")

    if _is_running:
        _run_lock.release()
        raise HTTPException(status_code=409, detail="已有任务正在执行，请稍后再试")

    _is_running = True
    run_id = create_run(target=body.target, markers=body.markers, keyword=body.keyword)

    def task():
        try:
            _execute_run(run_id, body.target, body.markers, body.keyword, body.notify)
        finally:
            _run_lock.release()

    background_tasks.add_task(task)
    return {"run_id": run_id, "status": "pending", "message": "任务已提交"}


@app.get("/api/status")
def api_status():
    return {"is_running": _is_running}


app.mount("/reports", StaticFiles(directory=REPORT_HISTORY_DIR), name="reports")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
