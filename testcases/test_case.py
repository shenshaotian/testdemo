import configparser
import os
import pytest
import allure
import jsonpath
from common.common_requests import Requests
from common.logger import logger
from common.data_loader import test_data_loader

current_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(current_dir, '..', 'config.ini')


@allure.story("策略")
class TestAutoSearchPolicy:
    policy_task_id = None
    root_task_id = None
    policy_task_id_b = None
    root_task_id_b = None

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
        cls.data4 = test_data_loader.get_test_data("auto_search_data_noe_b")
        cls.data5 = test_data_loader.get_test_data("auto_search_data_tow_b")
        cls.data6 = test_data_loader.get_test_data("auto_search_data_three_b")
        cls.data7 = test_data_loader.get_test_data("auto_targeting_policy_a")
        cls.data8 = test_data_loader.get_test_data("auto_targeting_policy_b")
        cls.data9 = test_data_loader.get_test_data("asin_targeting_policy")
        cls.data10 = test_data_loader.get_test_data("phrase_search_policy_sb")
        cls.data11 = test_data_loader.get_test_data("phrase_targeting_policy_sb")
        cls.data12 = test_data_loader.get_test_data("asin_targeting_policy_sb")
        cls.data13 = test_data_loader.get_test_data("broad_targeting_policy")
        cls.data14 = test_data_loader.get_test_data("large_phrase_keyword_normal")

    @allure.tag("自动搜索词紧密提交策略A")
    def test_01_create_auto_search_policy_a(self):
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

    @allure.tag("紧密提交策略第二步")
    def test_02_submit_auto_search_policy_a(self):
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

    @allure.tag("紧密提交策略第三步")
    def test_03_submit_root_task_a(self):
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

    @allure.tag("自动搜索词宽泛提交策略B")
    def test_04_create_auto_search_policy_b(self):
        """创建策略"""
        logger.info("执行第一步：创建策略")

        # 发送请求
        res = Requests(headers=self.headers).post_request(
            "/python/v1/ad_strategy/auto_search_policy",
            json=self.data4
        )
        response = res.json()
        logger.info(f"响应状态码: {res.status_code}")

        # 验证响应
        assert response["code"] == 200

        # 提取任务ID
        task_id = jsonpath.jsonpath(response, '$.data.policy_task_id')
        if task_id:
            TestAutoSearchPolicy.policy_task_id_b = task_id[0]
            logger.info(f"提取到policy_task_id_b: {TestAutoSearchPolicy.policy_task_id_b}")
        else:
            logger.warning("未找到policy_task_id_b")

    @allure.tag("宽泛策略B第二步")
    def test_05_submit_auto_search_policy_b(self):
        """提交策略"""
        logger.info("执行第二步：提交策略")

        if not TestAutoSearchPolicy.policy_task_id_b:
            logger.error("缺少policy_task_id_b")
            pytest.fail("需要先执行第一步")

        # 准备数据
        submit_data = self.data5.copy()
        submit_data["policy_task_id"] = TestAutoSearchPolicy.policy_task_id_b
        logger.info(f"使用policy_task_id_b: {TestAutoSearchPolicy.policy_task_id_b}")

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
        root_task_id_b = jsonpath.jsonpath(response, '$.data.root_task_id')
        if root_task_id_b:
            TestAutoSearchPolicy.root_task_id_b = root_task_id_b[0]
            logger.info(f"提取到root_task_id_b: {TestAutoSearchPolicy.root_task_id_b}")
        else:
            logger.warning("未找到root_task_id_b")

    @allure.tag("宽泛策略B第三步")
    def test_06_submit_root_task_b(self):
        """提交策略"""
        logger.info("执行第三步：提交策略")

        if not TestAutoSearchPolicy.root_task_id_b:
            logger.error("缺少root_task_id_b")
            pytest.fail("需要先执行第一步")

        # 准备数据
        submit_data = self.data6.copy()
        submit_data["root_task_id"] = TestAutoSearchPolicy.root_task_id_b
        logger.info(f"使用root_task_id_b: {TestAutoSearchPolicy.root_task_id_b}")

        # 发送请求
        res = Requests(headers=self.headers).post_request(
            "/python/v1/ad_strategy/auto_search_root_submit",
            json=submit_data
        )
        response = res.json()
        logger.info(f"响应状态码: {res.status_code}")

        # 验证响应
        assert response["code"] == 200
        logger.info("策略提交成功")

    @allure.tag("自动投放紧密")
    def test_auto_targeting_policy_a(self):
        """提交策略"""
        logger.info("执行：提交策略")
        # 准备数据
        submit_data = self.data7.copy()
        # 发送请求
        res = Requests(headers=self.headers).post_request(
            "/python/v1/ad_strategy/auto_targeting_policy",
            json=submit_data
        )
        response = res.json()
        logger.info(f"响应状态码: {res.status_code}")

        # 验证响应
        assert response["code"] == 200
        logger.info("策略提交成功")

    @allure.tag("自动投放宽泛")
    def test_auto_targeting_policy_b(self):
        """提交策略"""
        logger.info("执行：提交策略")
        # 准备数据
        submit_data = self.data8.copy()
        # 发送请求
        res = Requests(headers=self.headers).post_request(
            "/python/v1/ad_strategy/auto_targeting_policy",
            json=submit_data
        )
        response = res.json()
        logger.info(f"响应状态码: {res.status_code}")

        # 验证响应
        assert response["code"] == 200
        logger.info("策略提交成功")

    @allure.tag("大词投放-SP")
    def test_auto_targeting_policy_big_keyword(self):
        """提交策略"""
        logger.info("执行：提交策略")
        # 准备数据
        submit_data = self.data14.copy()
        # 发送请求
        res = Requests(headers=self.headers).post_request(
            "/python/v1/ad_strategy/large_phrase_policy",
            json=submit_data
        )
        response = res.json()
        logger.info(f"响应状态码: {res.status_code}")
        logger.info(response)

        # 验证响应
        assert response["code"] == 200
        logger.info("策略提交成功")

    @allure.tag("广泛投放")
    def test_broad_targeting_policy(self):
        """提交策略"""
        logger.info("执行：提交策略")
        # 准备数据
        submit_data = self.data13.copy()
        # 发送请求
        res = Requests(headers=self.headers).post_request(
            "/python/v1/ad_strategy/broad_targeting_policy",
            json=submit_data
        )
        response = res.json()
        logger.info(f"响应状态码: {res.status_code}")

        # 验证响应
        assert response["code"] == 200
        logger.info("策略提交成功")

    @allure.tag("SP-ASIN投放")
    def test_asin_targeting_policy(self):
        """提交策略"""
        logger.info("执行：提交策略")
        # 准备数据
        submit_data = self.data9.copy()
        # 发送请求
        res = Requests(headers=self.headers).post_request(
            "/python/v1/ad_strategy/asin_targeting_policy",
            json=submit_data
        )
        response = res.json()
        logger.info(f"响应状态码: {res.status_code}")

        # 验证响应
        assert response["code"] == 200
        logger.info("策略提交成功")

    @allure.tag("SB-词组搜索")
    def test_phrase_search_policy_sb(self):
        """提交策略"""
        logger.info("执行：提交策略")
        # 准备数据
        submit_data = self.data10.copy()
        # 发送请求
        res = Requests(headers=self.headers).post_request(
            "/python/v1/ad_sb_strategy/phrase_search_policy",
            json=submit_data
        )
        response = res.json()
        logger.info(f"响应状态码: {res.status_code}")

        # 验证响应
        assert response["code"] == 200
        logger.info("策略提交成功")

    @allure.tag("SB-词组投放")
    def test_phrase_targeting_policy_sb(self):
        """提交策略"""
        logger.info("执行：提交策略")
        # 准备数据
        submit_data = self.data11.copy()
        # 发送请求
        res = Requests(headers=self.headers).post_request(
            "/python/v1/ad_sb_strategy/phrase_targeting_policy",
            json=submit_data
        )
        response = res.json()
        logger.info(f"响应状态码: {res.status_code}")

        # 验证响应
        assert response["code"] == 200
        logger.info("策略提交成功")

    @allure.tag("SB-ASIN投放")
    def test_asin_targeting_policy_sb(self):
        """提交策略"""
        logger.info("执行：提交策略")
        # 准备数据
        submit_data = self.data12.copy()
        # 发送请求
        res = Requests(headers=self.headers).post_request(
            "/python/v1/ad_sb_strategy/asin_targeting_policy",
            json=submit_data
        )
        response = res.json()
        logger.info(f"响应状态码: {res.status_code}")

        # 验证响应
        assert response["code"] == 200
        logger.info("策略提交成功")
