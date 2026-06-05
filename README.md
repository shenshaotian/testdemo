# API 接口自动化测试平台

基于 **pytest + Allure** 的接口自动化测试框架，并提供 **Web 测试平台**，支持一键触发测试、历史记录与 Allure 报告查看。

## 功能概览

| 能力 | 说明 |
|------|------|
| 接口自动化 | pytest 用例、Allure 报告、YAML 数据驱动 |
| 动态登录 | 验证码 OCR + RSA 加密，自动获取 Token |
| Web 测试平台 | FastAPI 后端 + 控制台页面，异步执行任务 |
| 报告归档 | 每次执行独立保存 Allure 报告与任务记录 |
| 飞书通知 | 平台可选推送；`Webhook.py` 支持独立脚本通知 |

## 项目结构

```
test_case_demo/
├── common/                     # 公共模块
│   ├── common_requests.py      # HTTP 请求封装（GET/POST/PUT/DELETE）
│   ├── data_loader.py          # 测试数据加载（YAML/JSON）
│   ├── deal_with_response.py   # 响应处理，集成 Allure
│   ├── logger.py               # 日志（控制台 + 按日文件）
│   ├── login.py                # 登录（验证码 + RSA + 重试）
│   ├── mysql_operate.py        # MySQL 操作
│   ├── tools.py                # 路径等工具函数
│   └── yaml_config.py          # YAML 配置读取
│
├── config/
│   └── config_yaml.yaml        # 环境配置（URL、账号、登录、数据库）
│
├── testcases/
│   ├── conftest.py             # pytest fixture（token 缓存）
│   └── test_case.py            # 策略接口测试用例
│
├── test_data/
│   └── products.yaml           # 接口请求体测试数据
│
├── test_platform/              # Web 测试平台
│   ├── app.py                  # FastAPI 路由与任务调度
│   ├── runner.py               # pytest 执行引擎
│   ├── storage.py              # SQLite 任务历史
│   └── static/index.html       # Web 控制台
│
├── report/
│   ├── tmp/                    # 本地执行 Allure 临时数据
│   ├── html/                   # 本地执行 Allure 报告
│   ├── history/{run_id}/       # 平台每次执行的报告归档
│   └── platform.db             # 平台任务数据库（运行时生成）
│
├── log/                        # 运行日志（按日期）
│
├── run.py                      # 命令行本地执行入口
├── start_platform.py           # 启动 Web 测试平台
├── Webhook.py                  # 测试 + 报告托管 + 飞书通知（独立脚本）
├── pytest.ini                  # pytest 配置
└── requirements.txt            # Python 依赖
```

## 环境要求

- Python 3.11+
- [Allure Commandline](https://docs.qameta.io/allure/)（生成 HTML 报告）
- 网络可访问被测环境

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

编辑 `config/config_yaml.yaml`：

```yaml
user:
  sam:
    username: your_username
    password: your_password

test_url: https://your-test-env.example.com
advertising_api: <advertising-api header 值>

login:
  login_url: /python/v1/api/system/passport/login
  captcha_url: /python/v1/api/system/passport/get_captcha
  company_name: 公司名称
  rsa_public_key: |
    -----BEGIN PUBLIC KEY-----
    ...
    -----END PUBLIC KEY-----

mysql:
  host: ...
  port: 3306
  user: ...
  password: ...
  db: ...
```

> 配置已从 `config.ini` 迁移至 YAML，无需再维护 `config.ini`。

### 3. 运行方式

#### 方式一：命令行（本地单次执行）

```bash
python run.py
```

执行流程：清理旧报告 → 运行全部用例 → 生成 Allure 报告到 `report/html/`。

#### 方式二：Web 测试平台（推荐）

```bash
python start_platform.py
```

浏览器访问：**http://127.0.0.1:8088**

平台支持：
- 一键触发测试（全量 / 指定文件 / `-m` / `-k` 过滤）
- 查看执行历史与通过率统计
- 打开每次执行的 Allure 报告
- 可选飞书通知

**平台环境变量（可选）：**

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `PLATFORM_PORT` | 服务端口 | `8088` |
| `PLATFORM_HOST` | 通知中的报告访问地址 | `http://127.0.0.1:8088` |
| `FEISHU_WEBHOOK_URL` | 飞书机器人 Webhook | 空（不通知） |

#### 方式三：Webhook 脚本（报告 + 飞书 + 本地 HTTP 服务）

```bash
python Webhook.py
```

适合在本地跑完测试后，启动 HTTP 服务并通过飞书推送报告链接。

#### 方式四：直接使用 pytest

```bash
pytest testcases -v --alluredir report/tmp
allure generate report/tmp -o report/html --clean
allure open report/html
```

## 测试平台 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | Web 控制台 |
| GET | `/api/stats` | 执行统计 |
| GET | `/api/runs` | 历史任务列表 |
| POST | `/api/runs` | 提交测试任务 |
| GET | `/api/runs/{id}` | 任务详情 |
| GET | `/api/status` | 是否正在执行 |
| GET | `/reports/{id}/html/index.html` | Allure 报告 |

**提交任务示例：**

```bash
curl -X POST http://127.0.0.1:8088/api/runs \
  -H "Content-Type: application/json" \
  -d '{"target":"testcases","keyword":"auto_targeting","notify":false}'
```

## 模块说明

### common/login.py

登录流程：获取 RSA 公钥 → 生成 UUID → 拉取验证码 → ddddocr 识别 → 提交登录。  
识别失败或验证码错误时自动重试（默认最多 3 次）。

### common/common_requests.py

HTTP 请求封装，支持 GET/POST/PUT/DELETE，自动重试，响应写入 Allure。

### common/data_loader.py

从 `test_data/` 加载 YAML/JSON，用例通过 `test_data_loader.load_all()` 一次性读取。

### testcases/test_case.py

广告策略相关接口回归用例，特点：
- `setup_class` 动态登录，避免 Token 过期
- 数据驱动，请求体来自 `products.yaml`
- 抽取 `_post_and_verify`、`_extract_id` 等公共方法

### test_platform/runner.py

统一测试执行逻辑，`run.py` 与 Web 平台共用：
- `run_tests_local()` — 本地 `report/tmp` + `report/html`
- `run_tests(run_id, ...)` — 平台归档到 `report/history/{run_id}/`

## 编写测试用例

```python
import allure
from common.common_requests import Requests
from common.login import login
from common.yaml_config import GetConfig
from common.data_loader import test_data_loader


@allure.story("策略")
class TestExample:

    @classmethod
    def setup_class(cls):
        config = GetConfig()
        token = login("sam").json()["data"]
        cls.headers = {
            "Authorization": f"Bearer {token}",
            "advertising-api": config.get_advertising_api(),
            "Content-Type": "application/json",
        }
        cls.request = Requests(headers=cls.headers)
        cls.data = test_data_loader.load_all()

    @allure.tag("示例")
    def test_example(self):
        res = self.request.post_request(
            "/python/v1/your/api",
            json=self.data["your_key"],
        )
        assert res.json()["code"] == 200
```

新增接口数据：在 `test_data/products.yaml` 增加条目，用例中引用即可，无需改 loader。

## 依赖说明

| 包名 | 用途 |
|------|------|
| pytest | 测试框架 |
| allure-pytest | Allure 报告集成 |
| requests | HTTP 请求 |
| PyYAML | YAML 解析 |
| PyMySQL | MySQL 操作 |
| jsonpath | JSON 路径提取 |
| ddddocr | 验证码识别 |
| cryptography | RSA 密码加密 |
| fastapi / uvicorn | Web 测试平台 |

## 常见问题

**Q: 提示找不到 `allure` 命令？**  
A: 安装 Allure Commandline 并加入 PATH，或使用 IDE 插件查看 `report/html`。

**Q: 登录失败 / 验证码识别错误？**  
A: 检查 `config_yaml.yaml` 中账号、RSA 公钥、公司名；可查看 `log/` 与 `captcha_debug.png`（调试时生成）。

**Q: 平台提示「已有任务正在执行」？**  
A: 平台同一时间只允许一个任务，等待当前任务结束后再提交。

**Q: 报告目录很大？**  
A: `report/history/` 与 `report/html/` 为生成物，可按需清理，不影响代码。
