import glob
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from typing import Optional

from common.tools import get_project_path


@dataclass
class RunResult:
    exit_code: int
    total: int
    passed: int
    failed: int
    broken: int
    skipped: int
    tmp_dir: str
    html_dir: str


def get_history_dir(run_id: str) -> str:
    return os.path.join(get_project_path(), "report", "history", run_id)


def parse_allure_results(tmp_dir: str) -> dict:
    counts = {"total": 0, "passed": 0, "failed": 0, "broken": 0, "skipped": 0}
    if not os.path.isdir(tmp_dir):
        return counts

    for path in glob.glob(os.path.join(tmp_dir, "*-result.json")):
        try:
            with open(path, encoding="utf-8") as fp:
                data = json.load(fp)
        except (json.JSONDecodeError, OSError):
            continue

        status = data.get("status", "unknown")
        counts["total"] += 1
        if status in counts:
            counts[status] += 1

    return counts


def generate_allure_report(tmp_dir: str, html_dir: str) -> int:
    os.makedirs(html_dir, exist_ok=True)
    cmd = f'allure generate "{tmp_dir}" -o "{html_dir}" --clean'
    return os.system(cmd)


def run_tests(
    run_id: str,
    target: str = "testcases",
    markers: Optional[str] = None,
    keyword: Optional[str] = None,
) -> RunResult:
    """执行 pytest 并生成 Allure 报告。"""
    base_dir = get_history_dir(run_id)
    tmp_dir = os.path.join(base_dir, "tmp")
    html_dir = os.path.join(base_dir, "html")
    os.makedirs(tmp_dir, exist_ok=True)

    args = [
        sys.executable,
        "-m",
        "pytest",
        target,
        "-v",
        "--alluredir",
        tmp_dir,
    ]
    if markers:
        args.extend(["-m", markers])
    if keyword:
        args.extend(["-k", keyword])

    proc = subprocess.run(
        args,
        cwd=get_project_path(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    counts = parse_allure_results(tmp_dir)
    generate_allure_report(tmp_dir, html_dir)

    return RunResult(
        exit_code=proc.returncode,
        total=counts["total"],
        passed=counts["passed"],
        failed=counts["failed"],
        broken=counts["broken"],
        skipped=counts["skipped"],
        tmp_dir=tmp_dir,
        html_dir=html_dir,
    )


def run_tests_local(clean: bool = True) -> RunResult:
    """本地 run.py 使用的单次执行（report/tmp + report/html）。"""
    import shutil

    project_root = get_project_path()
    report_dir = os.path.join(project_root, "report")
    tmp_dir = os.path.join(report_dir, "tmp")
    html_dir = os.path.join(report_dir, "html")

    if clean:
        for dir_path in [tmp_dir, html_dir]:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
            os.makedirs(dir_path, exist_ok=True)

    args = [sys.executable, "-m", "pytest", "-v", "--alluredir", tmp_dir]
    proc = subprocess.run(
        args,
        cwd=project_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    counts = parse_allure_results(tmp_dir)
    generate_allure_report(tmp_dir, html_dir)

    return RunResult(
        exit_code=proc.returncode,
        total=counts["total"],
        passed=counts["passed"],
        failed=counts["failed"],
        broken=counts["broken"],
        skipped=counts["skipped"],
        tmp_dir=tmp_dir,
        html_dir=html_dir,
    )
