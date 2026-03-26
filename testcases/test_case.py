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
        cls.request = Requests(headers=cls.headers)

        cls.auto_search_create_a = test_data_loader.get_test_data("auto_search_data_noe")
        cls.auto_search_submit_a = test_data_loader.get_test_data("auto_search_data_tow")
        cls.auto_search_root_a = test_data_loader.get_test_data("auto_search_data_three")
        cls.auto_search_create_b = test_data_loader.get_test_data("auto_search_data_noe_b")
        cls.auto_search_submit_b = test_data_loader.get_test_data("auto_search_data_tow_b")
        cls.auto_search_root_b = test_data_loader.get_test_data("auto_search_data_three_b")
        cls.auto_targeting_a = test_data_loader.get_test_data("auto_targeting_policy_a")
        cls.auto_targeting_b = test_data_loader.get_test_data("auto_targeting_policy_b")
        cls.asin_targeting_sp = test_data_loader.get_test_data("asin_targeting_policy")
        cls.phrase_search_sb = test_data_loader.get_test_data("phrase_search_policy_sb")
        cls.phrase_targeting_sb = test_data_loader.get_test_data("phrase_targeting_policy_sb")
        cls.asin_targeting_sb = test_data_loader.get_test_data("asin_targeting_policy_sb")
        cls.broad_targeting = test_data_loader.get_test_data("broad_targeting_policy")
        cls.large_phrase_keyword = test_data_loader.get_test_data("large_phrase_keyword_normal")

    def _post_and_verify(self, url, data, policy_name="策略"):
        """通用POST请求并验证响应"""
        logger.info(f"执行：提交{policy_name}")
        res = self.request.post_request(url, json=data.copy())
        response = res.json()
        logger.info(f"响应状态码: {res.status_code}")
        assert response["code"] == 200, f"{policy_name}提交失败: {response}"
        logger.info(f"{policy_name}提交成功")
        return response

    def _extract_id(self, response, json_path, id_name):
        """从响应中提取ID"""
        result = jsonpath.jsonpath(response, json_path)
        if result:
            logger.info(f"提取到{id_name}: {result[0]}")
            return result[0]
        logger.warning(f"未找到{id_name}")
        return None

    def _check_required_id(self, id_value, id_name, step_name):
        """检查必需的ID是否存在"""
        if not id_value:
            logger.error(f"缺少{id_name}")
            pytest.fail(f"需要先执行{step_name}")

    @allure.tag("自动搜索词紧密提交策略A")
    def test_01_create_auto_search_policy_a(self):
        """创建策略"""
        logger.info("执行第一步：创建策略")

        # 发送请求
        res = self.request.post_request(
            "/python/v1/ad_strategy/auto_search_policy",
            json=self.auto_search_create_a
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
        submit_data = self.auto_search_submit_a.copy()
        submit_data["policy_task_id"] = TestAutoSearchPolicy.policy_task_id
        logger.info(f"使用policy_task_id: {TestAutoSearchPolicy.policy_task_id}")

        # 发送请求
        res = self.request.post_request(
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
            pytest.fail("需要先执行第二步")

        # 准备数据
        submit3_data = self.auto_search_root_a.copy()
        submit3_data["root_task_id"] = TestAutoSearchPolicy.root_task_id
        logger.info(f"使用root_task_id: {TestAutoSearchPolicy.root_task_id}")

        # 发送请求
        res = self.request.post_request(
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
        res = self.request.post_request(
            "/python/v1/ad_strategy/auto_search_policy",
            json=self.auto_search_create_b
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
        submit_data = self.auto_search_submit_b.copy()
        submit_data["policy_task_id"] = TestAutoSearchPolicy.policy_task_id_b
        logger.info(f"使用policy_task_id_b: {TestAutoSearchPolicy.policy_task_id_b}")

        # 发送请求
        res = self.request.post_request(
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
        submit_data = self.auto_search_root_b.copy()
        submit_data["root_task_id"] = TestAutoSearchPolicy.root_task_id_b
        logger.info(f"使用root_task_id_b: {TestAutoSearchPolicy.root_task_id_b}")

        # 发送请求
        res = self.request.post_request(
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
        """自动投放紧密策略"""
        self._post_and_verify(
            "/python/v1/ad_strategy/auto_targeting_policy",
            self.auto_targeting_a,
            "自动投放紧密策略"
        )

    @allure.tag("自动投放宽泛")
    def test_auto_targeting_policy_b(self):
        """自动投放宽泛策略"""
        self._post_and_verify(
            "/python/v1/ad_strategy/auto_targeting_policy",
            self.auto_targeting_b,
            "自动投放宽泛策略"
        )

    @allure.tag("大词投放-SP")
    def test_auto_targeting_policy_big_keyword(self):
        """大词投放策略"""
        response = self._post_and_verify(
            "/python/v1/ad_strategy/large_phrase_policy",
            self.large_phrase_keyword,
            "大词投放策略"
        )
        logger.info(response)

    @allure.tag("广泛投放")
    def test_broad_targeting_policy(self):
        """广泛投放策略"""
        self._post_and_verify(
            "/python/v1/ad_strategy/broad_targeting_policy",
            self.broad_targeting,
            "广泛投放策略"
        )

    @allure.tag("SP-ASIN投放")
    def test_asin_targeting_policy(self):
        """SP-ASIN投放策略"""
        self._post_and_verify(
            "/python/v1/ad_strategy/asin_targeting_policy",
            self.asin_targeting_sp,
            "SP-ASIN投放策略"
        )

    @allure.tag("SB-词组搜索")
    def test_phrase_search_policy_sb(self):
        """SB词组搜索策略"""
        self._post_and_verify(
            "/python/v1/ad_sb_strategy/phrase_search_policy",
            self.phrase_search_sb,
            "SB词组搜索策略"
        )

    @allure.tag("SB-词组投放")
    def test_phrase_targeting_policy_sb(self):
        """SB词组投放策略"""
        self._post_and_verify(
            "/python/v1/ad_sb_strategy/phrase_targeting_policy",
            self.phrase_targeting_sb,
            "SB词组投放策略"
        )

    @allure.tag("SB-ASIN投放")
    def test_asin_targeting_policy_sb(self):
        """SB-ASIN投放策略"""
        self._post_and_verify(
            "/python/v1/ad_sb_strategy/asin_targeting_policy",
            self.asin_targeting_sb,
            "SB-ASIN投放策略"
        )
