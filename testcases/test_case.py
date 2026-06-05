import pytest
import allure
import jsonpath
from common.common_requests import Requests
from common.login import login
from common.yaml_config import GetConfig
from common.logger import logger
from common.data_loader import test_data_loader


@allure.story("策略")
class TestAutoSearchPolicy:
    policy_task_id = None
    root_task_id = None
    policy_task_id_b = None
    root_task_id_b = None

    @classmethod
    def setup_class(cls):
        logger.info("初始化测试配置")
        config = GetConfig()

        # 动态登录获取最新 token，避免 token 过期问题
        token = login("sam").json()["data"]
        cls.headers = {
            "Authorization": f"Bearer {token}",
            "advertising-api": config.get_advertising_api(),
            "Content-Type": "application/json",
        }
        cls.request = Requests(headers=cls.headers)

        # 一次性加载 products.yaml 全部数据，新增接口数据无需改动此处
        cls.data = test_data_loader.load_all()

    # ------------------------------------------------------------------ #
    #  通用辅助方法
    # ------------------------------------------------------------------ #

    def _post_and_verify(self, url, data, policy_name="策略"):
        """POST 请求并断言 code==200，返回响应 dict"""
        logger.info(f"执行：{policy_name}")
        res = self.request.post_request(url, json=data.copy())
        response = res.json()
        logger.info(f"响应状态码: {res.status_code}")
        assert response["code"] == 200, f"{policy_name}失败: {response}"
        logger.info(f"{policy_name}成功")
        return response

    def _extract_id(self, response, json_path, id_name):
        """从响应 dict 中提取 ID，未找到时记录警告"""
        result = jsonpath.jsonpath(response, json_path)
        if result:
            logger.info(f"提取到 {id_name}: {result[0]}")
            return result[0]
        logger.warning(f"未找到 {id_name}")
        return None

    def _check_required_id(self, id_value, id_name, step_name):
        """前置 ID 存在性检查，不存在则 fail"""
        if not id_value:
            pytest.fail(f"缺少 {id_name}，请先执行{step_name}")

    # ------------------------------------------------------------------ #
    #  自动搜索词策略 A（紧密）：三步流程
    # ------------------------------------------------------------------ #

    @allure.tag("自动搜索词紧密提交策略A")
    def test_01_create_auto_search_policy_a(self):
        """创建策略 A"""
        response = self._post_and_verify(
            "/python/v1/ad_strategy/auto_search_policy",
            self.data["auto_search_data_noe"],
            "自动搜索词紧密策略A-创建",
        )
        TestAutoSearchPolicy.policy_task_id = self._extract_id(
            response, "$.data.policy_task_id", "policy_task_id"
        )

    @allure.tag("紧密提交策略第二步")
    def test_02_submit_auto_search_policy_a(self):
        """提交策略 A"""
        self._check_required_id(TestAutoSearchPolicy.policy_task_id, "policy_task_id", "第一步")
        submit_data = self.data["auto_search_data_tow"].copy()
        submit_data["policy_task_id"] = TestAutoSearchPolicy.policy_task_id
        response = self._post_and_verify(
            "/python/v1/ad_strategy/auto_search_policy_submit",
            submit_data,
            "自动搜索词紧密策略A-提交",
        )
        TestAutoSearchPolicy.root_task_id = self._extract_id(
            response, "$.data.root_task_id", "root_task_id"
        )

    @allure.tag("紧密提交策略第三步")
    def test_03_submit_root_task_a(self):
        """提交 root 任务 A"""
        self._check_required_id(TestAutoSearchPolicy.root_task_id, "root_task_id", "第二步")
        submit_data = self.data["auto_search_data_three"].copy()
        submit_data["root_task_id"] = TestAutoSearchPolicy.root_task_id
        self._post_and_verify(
            "/python/v1/ad_strategy/auto_search_root_submit",
            submit_data,
            "自动搜索词紧密策略A-root提交",
        )

    # ------------------------------------------------------------------ #
    #  自动搜索词策略 B（宽泛）：三步流程
    # ------------------------------------------------------------------ #

    @allure.tag("自动搜索词宽泛提交策略B")
    def test_04_create_auto_search_policy_b(self):
        """创建策略 B"""
        response = self._post_and_verify(
            "/python/v1/ad_strategy/auto_search_policy",
            self.data["auto_search_data_noe_b"],
            "自动搜索词宽泛策略B-创建",
        )
        TestAutoSearchPolicy.policy_task_id_b = self._extract_id(
            response, "$.data.policy_task_id", "policy_task_id_b"
        )

    @allure.tag("宽泛策略B第二步")
    def test_05_submit_auto_search_policy_b(self):
        """提交策略 B"""
        self._check_required_id(TestAutoSearchPolicy.policy_task_id_b, "policy_task_id_b", "第四步")
        submit_data = self.data["auto_search_data_tow_b"].copy()
        submit_data["policy_task_id"] = TestAutoSearchPolicy.policy_task_id_b
        response = self._post_and_verify(
            "/python/v1/ad_strategy/auto_search_policy_submit",
            submit_data,
            "自动搜索词宽泛策略B-提交",
        )
        TestAutoSearchPolicy.root_task_id_b = self._extract_id(
            response, "$.data.root_task_id", "root_task_id_b"
        )

    @allure.tag("宽泛策略B第三步")
    def test_06_submit_root_task_b(self):
        """提交 root 任务 B"""
        self._check_required_id(TestAutoSearchPolicy.root_task_id_b, "root_task_id_b", "第五步")
        submit_data = self.data["auto_search_data_three_b"].copy()
        submit_data["root_task_id"] = TestAutoSearchPolicy.root_task_id_b
        self._post_and_verify(
            "/python/v1/ad_strategy/auto_search_root_submit",
            submit_data,
            "自动搜索词宽泛策略B-root提交",
        )

    # ------------------------------------------------------------------ #
    #  单步策略（直接 POST 即可）
    # ------------------------------------------------------------------ #

    @allure.tag("自动投放紧密")
    def test_auto_targeting_policy_a(self):
        """自动投放紧密策略"""
        self._post_and_verify(
            "/python/v1/ad_strategy/auto_targeting_policy",
            self.data["auto_targeting_policy_a"],
            "自动投放紧密策略",
        )

    @allure.tag("自动投放宽泛")
    def test_auto_targeting_policy_b(self):
        """自动投放宽泛策略"""
        self._post_and_verify(
            "/python/v1/ad_strategy/auto_targeting_policy",
            self.data["auto_targeting_policy_b"],
            "自动投放宽泛策略",
        )

    @allure.tag("大词投放-SP")
    def test_auto_targeting_policy_big_keyword(self):
        """大词投放策略"""
        response = self._post_and_verify(
            "/python/v1/ad_strategy/large_phrase_policy",
            self.data["large_phrase_keyword_normal"],
            "大词投放策略",
        )
        logger.info(response)

    @allure.tag("广泛投放")
    def test_broad_targeting_policy(self):
        """广泛投放策略"""
        self._post_and_verify(
            "/python/v1/ad_strategy/broad_targeting_policy",
            self.data["broad_targeting_policy"],
            "广泛投放策略",
        )

    @allure.tag("SP-ASIN投放")
    def test_asin_targeting_policy(self):
        """SP-ASIN 投放策略"""
        self._post_and_verify(
            "/python/v1/ad_strategy/asin_targeting_policy",
            self.data["asin_targeting_policy"],
            "SP-ASIN投放策略",
        )

    @allure.tag("SB-词组搜索")
    def test_phrase_search_policy_sb(self):
        """SB 词组搜索策略"""
        self._post_and_verify(
            "/python/v1/ad_sb_strategy/phrase_search_policy",
            self.data["phrase_search_policy_sb"],
            "SB词组搜索策略",
        )

    @allure.tag("SB-词组投放")
    def test_phrase_targeting_policy_sb(self):
        """SB 词组投放策略"""
        self._post_and_verify(
            "/python/v1/ad_sb_strategy/phrase_targeting_policy",
            self.data["phrase_targeting_policy_sb"],
            "SB词组投放策略",
        )

    @allure.tag("SB-ASIN投放")
    def test_asin_targeting_policy_sb(self):
        """SB-ASIN 投放策略"""
        self._post_and_verify(
            "/python/v1/ad_sb_strategy/asin_targeting_policy",
            self.data["asin_targeting_policy_sb"],
            "SB-ASIN投放策略",
        )
