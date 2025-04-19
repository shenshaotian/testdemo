# 导入获取yaml方法
from common.yaml_config import GetConfig
# 导入封装好的request
from common.commom_requests import Requests


def login(user):
    """
    封装登录接口
    :param user: yaml文件里账号密码的用户名称
    :return:
    """
    # 取出账号密码
    username, password = GetConfig().get_username_password(user)
    # 赋值给登录接口的入参
    login_data = {
        "name": f"{username}",
        "pwd": f"{password}"
    }
    # 执行接口请求
    login_res = Requests().post_request("https://gw.lingxingerp.com/newadmin/api/passport/login", data=login_data)
    # 返回出参
    return login_res

# 测试一下，道友们可以用自己公司系统测试
if __name__ == '__main__':
    print(login("sam").json())

