# 导出处理yaml文件的包
import yaml
# 导入3.1编写好的tools里的方法
from common.tools import get_project_path, sep


class GetConfig:
    # 使用构造函数，初始化yaml文件，把yaml文件读取出来
    def __init__(self):
        # 用tools里的get_project_path()获取项目路径
        project_path = get_project_path()
        # 使用with——open方法读取yaml文件内容
        # open里的project_path + sep(["config", "environment.yaml"）用于把yaml文件路径拼出来
        with open(project_path + sep(["config", "config_yaml.yaml"], add_sep_before=True), "r",
                  encoding="utf-8") as env_file:
            # 使用yaml.load方法把读取出的文件转化为列表或字典，方便后续取值
            # Loader=yaml.FullLoader意思为加载完整的YAML语言，避免任意代码执行
            self.env = yaml.load(env_file, Loader=yaml.FullLoader)

    def get_username_password(self, sam):
        """
        读取配置文件里的账号密码
        :param user: 需要取哪一个账号的就输入对应的名称，比如我想去york的账密，user就传“york”
        :return:
        """
        # 直接return出来对应的账号密码
        return self.env["user"][f"{sam}"]["username"], self.env["user"][f"{sam}"]["password"]

    def get_url(self):
        """
        测试地址
        :return:
        """
        # 直接return出来对应的测试域名
        return self.env["test_url"]

    def get_mysql_config(self):
        """
        获取数据库配置
        :return:
        """
        # 直接return出来对应yaml里的数据库参数，输出字典
        return self.env["mysql"]


# 测试一下
if __name__ == "__main__":
    getConfig = GetConfig()
    print(getConfig.get_username_password("sam"))
    print(getConfig.get_url())
    print(getConfig.get_mysql_config())

