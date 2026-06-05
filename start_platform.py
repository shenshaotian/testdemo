"""启动接口自动化测试平台 Web 服务。"""
import os

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PLATFORM_PORT", "8088"))
    uvicorn.run(
        "test_platform.app:app",
        host="0.0.0.0",
        port=port,
        reload=False,
    )
