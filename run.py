from test_platform.runner import run_tests_local

if __name__ == "__main__":
    result = run_tests_local(clean=True)
    print(f"执行完成: {result.passed}/{result.total} 通过, exit_code={result.exit_code}")
    print(f"报告目录: {result.html_dir}")
