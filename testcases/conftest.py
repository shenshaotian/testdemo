# 导入各种包，不一一介绍了，下面代码都要有用到的
import os
import json
import pytest
# 读取数据库的方法也可加到夹具里，我没加
from common.mysql_operate import MysqlOperate
from common.login import login
from common.tools import sep, get_project_path


# pytest的精髓，夹具fixture，效果类似setup
@pytest.fixture()
def token():
    def _token(user):
        # 判断存放token文件的文件夹是否存在，不存在则自动创建
        token_json_dir = sep([get_project_path(), "token_dir"])
        if not os.path.exists(token_json_dir):
            os.mkdir(token_json_dir)

        # 生成用户user对应token的json文件
        token_json_path = sep([token_json_dir, user + "_token.json"])
        # 若文件不存在，调用登录接口，并把token写入json文件
        if not os.path.exists(token_json_path):
            print(f"{user}对应的token的json文件不存在，调用登录接口")
            # 调用登录方法，拿到token，每个系统的token字段名不一样，自行修改
            token = login(user).json()["data"]
            print(f"写入{user}对应token的json文件{token}")
            # 拿到token后，开始生成token文件，并写入token
            with open(token_json_path,"w+") as write_token:
                # 写入是时候是键值对的形式，方便拿取
                write_token.write(json.dumps({"token": token}))
            # return出token
            return token
        else:
            # 文件存在了，直接取出文件里面的token
            print(f"{user}对应的token_json文件存在，直接取文件token")
            with open(token_json_path, "r") as token_info:
                token = json.loads(token_info.read())
                # 因为token是键值对的形式，需要取一下
                return token["token"]

    return _token
