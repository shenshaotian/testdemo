# API 自动化测试框架

基于 pytest + allure 的接口自动化测试框架。

## 项目结构

```
test_case_demo/
├── common/                     # 公共模块
│   ├── common_requests.py      # HTTP 请求封装（GET/POST/PUT/DELETE）
│   ├── data_loader.py          # 测试数据加载器（YAML/JSON）
│   ├── deal_with_response.py   # 响应处理，集成 Allure 报告
│   ├── logger.py               # 日志模块
│   ├── login.py                # 登录接口封装
│   ├── mysql_operate.py        # MySQL 数据库操作
│   ├── tools.py                # 工具函数（路径处理）
│   └── yaml_config.py          # YAML 配置文件读取
│
├── config/                     # 配置文件目录
│   └── config_yaml.yaml        # 环境配置（URL、数据库、账号）
│
├── testcases/                  # 测试用例目录
│   ├── conftest.py             # pytest 夹具（fixture）
│   └── test_case.py            # 测试用例
│
├── test_data/                  # 测试数据目录
│   └── products.yaml           # 测试数据文件
│
├── report/                     # 测试报告目录
│   ├── tmp/                    # Allure 临时数据
│   └── html/                   # Allure HTML 报告
│
├── log/                        # 日志目录
│
├── config.ini                  # API 认证配置（TOKEN）
├── pytest.ini                  # pytest 配置
├── requirements.txt            # 依赖包
└── run.py                      # 运行入口
```

## 模块说明

### common/common_requests.py
HTTP 请求封装类，支持：
- GET 请求
- POST 请求（form-data / json）
- PUT 请求
- DELETE 请求
- 自动重试机制
- 响应信息自动记录到 Allure 报告

### common/logger.py
日志模块，支持：
- 控制台输出
- 文件输出（按日期生成）
- 统一日志格式

### common/mysql_operate.py
MySQL 数据库操作，支持：
- 查询（query）
- 插入/更新（insert_update_table）

### common/data_loader.py
测试数据加载器，支持：
- YAML 文件读取
- JSON 文件读取
- 测试用例数据获取

### testcases/conftest.py
pytest 夹具，提供：
- token 获取与缓存

### testcases/test_case.py
测试用例类，包含：
- 策略创建、提交等接口测试
- 公共方法抽取，减少重复代码

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

编辑 `config/config_yaml.yaml` 配置测试环境：
- test_url: 测试服务器地址
- mysql: 数据库连接信息
- user: 测试账号

编辑 `config.ini` 配置 API 认证：
- TOKEN: Bearer Token
- advertising: 广告 API 参数

### 3. 运行测试

```bash
python run.py
```

运行后会自动：
1. 清理旧报告
2. 执行测试用例
3. 生成 Allure HTML 报告
4. 自动打开报告页面

## 依赖包

| 包名 | 用途 |
|------|------|
| pytest | 测试框架 |
| allure-pytest | Allure 测试报告 |
| requests | HTTP 请求 |
| PyYAML | YAML 配置解析 |
| PyMySQL | MySQL 数据库操作 |
| jsonpath | JSON 路径提取 |

## 编写测试用例

```python
import allure
from common.common_requests import Requests
from common.logger import logger

@allure.story("功能模块")
class TestExample:
    
    @classmethod
    def setup_class(cls):
        cls.headers = {"Authorization": "Bearer xxx"}
        cls.request = Requests(headers=cls.headers)
    
    @allure.tag("测试标签")
    def test_example(self):
        """测试用例描述"""
        res = self.request.post_request("/api/endpoint", json={"key": "value"})
        assert res.json()["code"] == 200
```
