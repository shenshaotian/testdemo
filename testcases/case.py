import yaml

# 从 YAML 文件中读取 header 值
def read_header_from_yaml(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
        return data

# 导入必要的包
import pytest
from common.commom_requests import Requests

# 测试案例必须要以 Test 开头
class TestAddUser:
    def test_add_user(self):
        # 从 YAML 文件中读取 header 值
        header_data = read_header_from_yaml('config_yaml.yaml')
        header = {
            "advertising-api": header_data.get("advertising-api"),
            "authorization": header_data.get("authorization")
        }

        # 其他代码保持不变
        json = {
            "ad_type": "sp",
            "rule_model": "A",
            "module": "sp_auto_search_a_normal",
            "campaign_configs": [
                {
                    "asin_down_limit": 0.8,
                    "asin_up_limit": 1.5,
                    "campaign_id": 297168231118598,
                    "campaign_name": "US-海洋系列灭鼠先锋-自动组1-B09HGT8V9L",
                    "hight_down_limit": 1.1,
                    "hight_up_limit": 1.4,
                    "low_related_up_limit": 0.7,
                    "price": 16.99,
                    "strategy_config": 0,
                    "target_acos": 40,
                    "target_cr": 17.86
                }
            ],
            "ad_group_configs": [
                {
                    "ad_campaign_type": "sp_auto_a_campaign",
                    "ad_group_id": 435772146687517,
                    "ad_group_name": "自动",
                    "ad_group_type": "sp_auto_search_a_group",
                    "ad_type": "sp",
                    "campaign_id": 297168231118598,
                    "campaign_name": "US-海洋系列灭鼠先锋-自动组1-B09HGT8V9L",
                    "default_bid": 0.97,
                    "id": 151573,
                    "manual_targeting": "ProductAuto",
                    "portfolio_id": 104379592268941,
                    "portfolio_name": "US-海洋系列灭鼠先锋-B09HGT8V9L",
                    "sys_ad_group_id": 151573,
                    "allowed_campaign_id": 199037102594621,
                    "asin_allowed_campaign_id": 153771028520781,
                    "allowed_campaign_name": "US-海洋系列灭鼠先锋-手动组-B09HGT8V9L",
                    "asin_allowed_campaign_name": "US-海洋系列灭鼠先锋-ASIN组-B09HGT8V9L"
                }
            ]
        }
        res = Requests(headers=header).post_request("/python/v1/ad_strategy/auto_search_policy", json=json)
        print(res.json())
        assert res.status_code == 200
