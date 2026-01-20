import configparser
import os
import pytest
import allure
from common.commom_requests import Requests
from common.logger import logger
from common.data_loader import test_data_loader
import warnings

# 配置忽略警告
warnings.filterwarnings("ignore")

# 获取配置文件路径
current_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(current_dir, '..', 'config.ini')


def get_token():
    """获取API访问令牌"""
    config = configparser.ConfigParser()
    config.read(config_file_path, encoding='utf-8')
    return config.get('API', 'TOKEN')


@pytest.fixture(scope="class")
def setup_class(request):
    """类级别的fixture，用于共享测试数据"""
    token = get_token()
    assert token, "无法获取有效的API令牌，请检查config.ini配置"

    headers = {"Authorization": token}
    request.cls.headers = headers

    # 从YAML文件加载测试数据
    try:
        request.cls.test_product_data = test_data_loader.get_test_data("new_product")
        request.cls.update_data = test_data_loader.get_test_data("update_data")
        request.cls.list_params = test_data_loader.get_test_data("list_params")
        request.cls.restore_to_archived_status = test_data_loader.get_test_data("restore_to_archived_status")

        logger.info("测试数据加载成功")
    except Exception as e:
        logger.error(f"加载测试数据失败: {e}")
        raise


@pytest.fixture
def new_product_id(setup_class, request):
    """获取新品ID的fixture"""
    logger.info("** 开始获取新品ID **")

    # 使用外部化的列表参数
    json_data = request.cls.list_params

    with allure.step("获取新品列表"):
        res = Requests(headers=request.cls.headers).post_request(
            "/svip/product/getNewProductList",
            json=json_data
        )
        logger.info(f"请求URL: {res.request.url}")
        logger.info(f"请求参数: {json_data}")
        logger.info(f"请求响应: {res.json()}")

    assert res.json()["code"] == 200, "获取新品列表失败"
    result_data = res.json()["data"]["result"]
    assert result_data, "新品列表为空，无法获取new_product_id"

    return result_data[0]["new_product_id"]


@allure.story("新品管理")
class TestProductManagement:
    """新品管理测试套件"""

    @allure.tag("新增新品")
    def test_add_new_product(self, setup_class):
        """测试新增新品功能"""
        logger.info("** 开始执行新增新品测试 **")

        with allure.step("准备测试数据"):
            test_data = self.test_product_data.copy()

        with allure.step("发送新增新品请求"):
            res = Requests(headers=self.headers).put_request(
                "/svip/product/addNewProduct",
                json=test_data
            )
            response = res.json()
            logger.info(f"API响应: {response}")
        with allure.step("验证响应"):
            assert response["code"] == 200, f"新增失败: {response.get('message', '未知错误')}"
            assert "data" in response, "响应中缺少data字段"

    @allure.tag("获取新品列表")
    def test_get_product_list(self, setup_class):
        """测试获取新品列表功能"""
        logger.info("** 开始执行获取新品列表测试 **")

        with allure.step("准备请求参数"):
            params = self.list_params

        with allure.step("发送获取列表请求"):
            res = Requests(headers=self.headers).post_request(
                "/svip/product/getNewProductList",
                json=params
            )
            response = res.json()
            logger.info(f"API响应: {response}")

        with allure.step("验证响应"):
            assert response["code"] == 200, f"获取列表失败: {response.get('message', '未知错误')}"
            assert "data" in response, "响应中缺少data字段"
            assert "result" in response["data"], "响应中缺少result字段"

    @allure.tag("更新负责人")
    def test_update_product_manager(self, setup_class, new_product_id):
        """测试更新产品负责人功能"""
        logger.info("** 开始执行更新负责人测试 **")

        with allure.step("准备更新数据"):
            update_data = {
                "new_product_id": new_product_id,
                "user_id": self.update_data["user_id"],
            }

        with allure.step("发送更新请求"):
            res = Requests(headers=self.headers).put_request(
                "/svip/product/updateNewProduct",
                json=update_data
            )
            response = res.json()
            logger.info(f"API响应: {response}")

        with allure.step("验证响应"):
            assert response["code"] == 200, f"更新失败: {response.get('message', '未知错误')}"

    @allure.tag("新品归档")
    def test_archive_product(self, setup_class, new_product_id):
        """测试新品归档功能"""
        logger.info("** 开始执行新品归档测试 **")
        with allure.step("准备归档请求"):
            url = f"/svip/product/deleteNewProduct?new_product_id={new_product_id}"

        with allure.step("发送归档请求"):
            res = Requests(headers=self.headers).put_request(url)
            response = res.json()
            logger.info(f"API响应: {response}")

        with allure.step("验证响应"):
            assert response["code"] == 200, f"归档失败: {response.get('message', '未知错误')}"

    @allure.tag("复原新品")
    def test_recover_product(self, setup_class,new_product_id):
        """测试复原新品功能"""
        logger.info("** 开始执行复原新品测试 **")

        with allure.step("准备复原请求"):
            url = f"/svip/product/recoverNewProduct?new_product_id={new_product_id}"
        with allure.step("发送复原请求"):
            res = Requests(headers=self.headers).put_request(url)
            response = res.json()
            logger.info(f"API响应: {response}")

        with allure.step("验证响应"):
            assert response["code"] == 200, f"复原失败: {response.get('message', '未知错误')}"