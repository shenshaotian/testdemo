import configparser
import os
import pytest
import allure
import jsonpath
from common.commom_requests import Requests
from common.logger import logger
from common.data_loader import test_data_loader

current_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(current_dir, '..', 'config.ini')


@allure.story("自动搜索策略")
class TestAutoSearchPolicy:
    policy_task_id = None
    root_task_id = None

    @classmethod
    def setup_class(cls):
        logger.info("初始化测试配置")
        config = configparser.ConfigParser()
        config.read(config_file_path)

        cls.headers = {
            "Authorization": config.get('API', 'TOKEN'),
            "advertising-api": config.get('API', 'advertising'),
            "Content-Type": "application/json"
        }

        cls.data1 = test_data_loader.get_test_data("auto_search_data_noe")
        cls.data2 = test_data_loader.get_test_data("auto_search_data_tow")
        cls.data3 = test_data_loader.get_test_data("auto_search_data_three")
    @allure.tag("创建策略")
    def test_01_create(self):
        """创建策略"""
        logger.info("执行第一步：创建策略")

        # 发送请求
        res = Requests(headers=self.headers).post_request(
            "/python/v1/ad_strategy/auto_search_policy",
            json=self.data1
        )
        response = res.json()
        logger.info(f"响应状态码: {res.status_code}")

        # 验证响应
        assert response["code"] == 200

        # 提取任务ID
        task_id = jsonpath.jsonpath(response, '$.data.policy_task_id')
        if task_id:
            TestAutoSearchPolicy.policy_task_id = task_id[0]
            logger.info(f"提取到policy_task_id: {TestAutoSearchPolicy.policy_task_id}")
        else:
            logger.warning("未找到policy_task_id")

    @allure.tag("提交策略")
    def test_02_submit(self):
        """提交策略"""
        logger.info("执行第二步：提交策略")

        if not TestAutoSearchPolicy.policy_task_id:
            logger.error("缺少policy_task_id")
            pytest.fail("需要先执行第一步")

        # 准备数据
        submit_data = self.data2.copy()
        submit_data["policy_task_id"] = TestAutoSearchPolicy.policy_task_id
        logger.info(f"使用policy_task_id: {TestAutoSearchPolicy.policy_task_id}")

        # 发送请求
        res = Requests(headers=self.headers).post_request(
            "/python/v1/ad_strategy/auto_search_policy_submit",
            json=submit_data
        )
        response = res.json()
        logger.info(f"响应状态码: {res.status_code}")

        # 验证响应
        assert response["code"] == 200
        logger.info("策略提交成功")
        # 提取任务ID
        root_task_id = jsonpath.jsonpath(response, '$.data.root_task_id')
        if root_task_id:
            TestAutoSearchPolicy.root_task_id = root_task_id[0]
            logger.info(f"提取到root_task_id: {TestAutoSearchPolicy.root_task_id}")
        else:
            logger.warning("未找到root_task_id")

    @allure.tag("提交策略")
    def test_03_auto_search_root_submit(self):
        """提交策略"""
        logger.info("执行第三步：提交策略")

        if not TestAutoSearchPolicy.root_task_id:
            logger.error("缺少root_task_id")

        # 准备数据
        submit3_data = self.data3.copy()
        submit3_data["root_task_id"] = TestAutoSearchPolicy.root_task_id
        logger.info(f"使用root_task_id: {TestAutoSearchPolicy.root_task_id}")

        # 发送请求
        res = Requests(headers=self.headers).post_request(
            "/python/v1/ad_strategy/auto_search_root_submit",
            json=submit3_data
        )
        response = res.json()
        logger.info(f"响应状态码: {res.status_code}")

        # 验证响应
        assert response["code"] == 200
        logger.info("策略提交成功")
