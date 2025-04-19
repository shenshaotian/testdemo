import pytest
import os

if __name__ == '__main__':
    pytest.main(['-s','--alluredir','report/tmp'])
    os.system(r'allure generate report/tmp -o report/html --clean')
