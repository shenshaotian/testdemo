import os
import json
import pytest
from common.mysql_operate import MysqlOperate
from common.login import login
from common.tools import sep, get_project_path
from common.logger import logger


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
            logger.info(f"{user}对应的token文件不存在，调用登录接口")
            # 调用登录方法，拿到token，每个系统的token字段名不一样，自行修改
            token = login(user).json()["data"]
            logger.info(f"写入{user}对应的token文件")
            # 拿到token后，开始生成token文件，并写入token
            with open(token_json_path,"w+") as write_token:
                # 写入是时候是键值对的形式，方便拿取
                write_token.write(json.dumps({"token": token}))
            # return出token
            return token
        else:
            # 文件存在了，直接取出文件里面的token
            logger.info(f"{user}对应的token文件存在，直接读取")
            with open(token_json_path, "r") as token_info:
                token = json.loads(token_info.read())
                # 因为token是键值对的形式，需要取一下
                return token["token"]

    return _token
