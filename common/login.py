import sys
import os
# 直接运行此文件时，把项目根目录加入 sys.path，确保 common 包可被找到
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
import base64
import requests
import ddddocr
from requests.adapters import HTTPAdapter
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from common.yaml_config import GetConfig
from common.deal_with_response import deal_with_res
from common.logger import logger


def _rsa_encrypt(public_key_pem: str, plaintext: str) -> str:
    """用 RSA 公钥加密明文密码，返回 base64 字符串"""
    pub_key = serialization.load_pem_public_key(public_key_pem.encode())
    encrypted = pub_key.encrypt(plaintext.encode(), padding.PKCS1v15())
    return base64.b64encode(encrypted).decode()


def login(user, max_retry: int = 3):
    """
    带验证码（ddddocr 识别）+ UUID + RSA 密码加密的登录封装。
    流程：获取 RSA 公钥 → 生成 UUID → 拉验证码图 → OCR 识别 → 提交登录。
    识别失败或服务端返回验证码错误时自动重试，最多 max_retry 次。

    :param user:      yaml 里配置的用户名称，如 "sam"
    :param max_retry: 最大重试次数，默认 3
    :return:          登录接口的 Response 对象
    """
    config = GetConfig()
    base_url = config.get_url()
    login_cfg = config.get_login_config()
    username, password_plain = config.get_username_password(user)

    login_url = base_url + login_cfg["login_url"]
    captcha_url = base_url + login_cfg["captcha_url"]
    company_name = login_cfg.get("company_name", "")

    # 从配置文件读取 RSA 公钥并加密密码
    pub_key_pem = login_cfg["rsa_public_key"]
    password_encrypted = _rsa_encrypt(pub_key_pem, password_plain)
    logger.info("[login] 密码 RSA 加密完成")

    ocr = ddddocr.DdddOcr(show_ad=False)

    for attempt in range(1, max_retry + 1):
        session = requests.Session()
        session.mount("https://", HTTPAdapter(max_retries=3))

        captcha_uuid = str(uuid.uuid4())
        logger.info(f"[login] 第 {attempt} 次尝试，uuid={captcha_uuid}")

        # 拉取验证码图片
        try:
            captcha_resp = session.get(captcha_url, params={"uuid": captcha_uuid}, timeout=10)
            captcha_resp.raise_for_status()
        except Exception as e:
            logger.warning(f"[login] 获取验证码失败：{e}")
            continue

        # OCR 识别，转大写与服务端保持一致
        try:
            code = ocr.classification(captcha_resp.content).upper()
            logger.info(f"[login] 验证码识别结果：{code}")
        except Exception as e:
            logger.warning(f"[login] 验证码识别异常：{e}")
            continue

        # 提交登录
        login_data = {
            "account": username,
            "password": password_encrypted,
            "code": code,
            "uuid": captcha_uuid,
            "company_name": company_name,
        }
        try:
            res = session.post(login_url, json=login_data, timeout=10)
        except Exception as e:
            logger.warning(f"[login] 登录请求异常：{e}")
            continue

        deal_with_res(login_data, res)

        # 解析响应 JSON
        try:
            resp_json = res.json()
        except Exception:
            logger.warning("[login] 响应非 JSON，直接返回")
            return res

        resp_code = resp_json.get("code")
        resp_msg = str(resp_json.get("msg", "") or resp_json.get("message", ""))

        # 验证码相关错误 → 重新拉图重试
        captcha_keywords = ("验证码", "验证错误", "captcha", "code error")
        if any(kw in resp_msg for kw in captcha_keywords):
            logger.warning(f"[login] 验证码错误（code={resp_code}, msg={resp_msg}），准备重试")
            continue

        # 登录成功：data 不为 None 或 code 为常见成功值
        if resp_json.get("data") is not None or resp_code in (0, 200):
            logger.info(f"[login] 登录成功，code={resp_code}")
            return res

        # 其他业务错误（账号密码错误等），无需重试，直接抛出
        raise RuntimeError(f"[login] 登录业务错误，code={resp_code}, msg={resp_msg}")

    raise RuntimeError(f"[login] 登录失败，已重试 {max_retry} 次，请检查账号或验证码识别效果")


if __name__ == "__main__":
    print(login("sam").json())
