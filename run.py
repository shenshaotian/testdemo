import pytest
import os
import shutil

if __name__ == '__main__':
    # 清理旧报告
    report_dir = 'report'
    tmp_dir = os.path.join(report_dir, 'tmp')
    html_dir = os.path.join(report_dir, 'html')

    for dir_path in [tmp_dir, html_dir]:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        os.makedirs(dir_path, exist_ok=True)

    # 运行测试
    pytest.main(['-v', '--alluredir', tmp_dir])

    # 生成报告
    os.system(f'allure generate {tmp_dir} -o {html_dir} --clean')

    # 可选：自动打开报告
    os.system(f'allure open {html_dir}')