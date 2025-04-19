import configparser
import os
import pytest
import allure
import time
from common.commom_requests import Requests
from common.logger import logger
import warnings

warnings.filterwarnings("ignore")

# 获取当前文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(current_dir, 'config.ini')


def get_token():
    config = configparser.ConfigParser()
    config.read(config_file_path)  # 读取配置文件

    token = config.get('API', 'TOKEN')  # 获取 TOKEN 的值
    return token


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@allure.story("新品管理")
@allure.tag("新增新品SKU")
class TestAddUser:
    def test_new_porduct(self):
        token = get_token()  # 获取 token
        logger.info("** 开始执行用例 **")
        with allure.step("获取登录token"):
            header = {
                "Authorization": token
            }
            json_data = {
                "local_sku": "PT-JJ-00047-BL-00",
                "product_name": "17*33in 电暖垫（天蓝）",
                "product_id": 10917,
                "images": "https://image.distributetop.com/lingxing-erp/90136091285737472/20241203/77b839f0564749d99dd7b63a2faa9e57.jpg",
                "country": "US",
                "selling_partner_id": "A3EDESUK4AJJ2G,A3N08DNTN5NG4S,A2D1SGKDVSC5DH,A149ACH9GZTR5F",
                "user_id": 15,
                "department": "SJY",
                "small_class": "Heating Pads",
                "remark": "测试1"
            }

        with allure.step("新增新品产品"):
            res = Requests(headers=header).put_request("/svip/product/addNewProduct", json=json_data)
            logger.info("请求 URL: {}".format(res.request.url))
            logger.info("请求 参数: {}".format(json_data))
            logger.info("请求 response: {}".format(res.json()))
            logger.info("** 结束执行用例 **")

        with allure.step("断言"):
            assert res.json()["code"] == 200

    @allure.story("新品管理")
    @allure.tag("获取新品管理列表")
    def test_get_list_product(self):
        token = get_token()  # 直接调用 get_token() 函数获取 token
        logger.info("** 开始执行用例 **")
        with allure.step("获取登录token"):
            header = {
                "Authorization": token
            }
            json_data = {
                "page": 1,
                "page_size": 20
            }

        with allure.step("获取"):
            res = Requests(headers=header).post_request("/svip/product/getNewProductList", json=json_data)
            new_product_id = res.json()["data"]["result"][0]["new_product_id"]
            logger.info("请求 URL: {}".format(res.request.url))
            logger.info("请求 参数: {}".format(json_data))
            logger.info("请求 response: {}".format(res.json()))
            logger.info("** 结束执行用例 **")

        with allure.step("断言"):
            assert res.json()["code"] == 200
            return new_product_id

    @allure.story("新品管理")
    @allure.tag("设置运营负责人")
    def test_set_operations_manager(self):
        new_product_id = self.test_get_list_product()  # 调用 test_get_list_product 方法获取 new_product_id
        token = get_token()  # 直接调用 get_token() 函数获取 token
        logger.info("** 开始执行用例 **")

        with allure.step("获取登录token"):
            header = {
                "Authorization": token
            }

            json_data = {
                "new_product_id": new_product_id,
                "user_id": "15",
            }

        with allure.step("调用修改对应运营负责人"):
            res = Requests(headers=header).put_request("/svip/product/updateNewProduct", json=json_data)
            logger.info("请求 URL: {}".format(res.request.url))
            logger.info("请求 参数: {}".format(json_data))
            logger.info("请求 response: {}".format(res.json()))
            logger.info("** 结束执行用例 **")

        with allure.step("断言"):
            assert res.json()["code"] == 200
