# 导入requests
import requests
# 导入adapters，处理接口重试
from requests.adapters import HTTPAdapter
# 导入前面写的两个方法
from common.yaml_config import GetConfig
from common.deal_with_response import deal_with_res


class Requests:
    # 构造函数，初始化session，封装requests
    def __init__(self, headers=None, timeout=None):
        """
        封装requests方法
        :param headers:接口的header
        :param timeout:如果需要设置设置超时时间就传，默认None
        """
        self.s = requests.Session()
        # 在session实例上挂载adapter实例，目的就是请求异常时，自动重试
        # self.s.mount("https://www.baidu.com", HTTPAdapter(max_retries=3))
        self.s.mount("/svip/homePage/OverviewUserGroupDoneRate", HTTPAdapter(max_retries=3))

        # 公共请求头设置，把对应的值设置好
        self.s.headers = headers
        self.timeout = timeout
        # 调用获取yaml里的url，把测试域名拿出来，下面做拼接接口用
        self.url = GetConfig().get_url()

    def get_request(self, url, params=None):
        """
        GET方法封装
        :param url: 接口地址
        :param params: 一般GET的参数都是放在URL里面
        :return:
        """
        # 可以看到用yaml里的self.url加上接口路径，就是完整的接口了
        # 后面要测试uat或者生产环境直接的话直接改yaml里面的域名就好了
        res = self.s.get(self.url + url, params=params, timeout=self.timeout)
        # 调用处理报文的方法，把接口信息加入到测试报告
        deal_with_res(params, res)
        return res

    def post_request(self, url, data=None, json=None):
        """
        POST方法封装
        :param url: 接口地址
        :param data: 参数放在表单中
        :param json: 参数放在请求体中，一般是json
        :param headers:
        :return:
        """
        # 如果传入的是表单，那接口就传data，适用一些接口是form-data格式的
        if data:
            res = self.s.post(self.url + url, data=data, timeout=self.timeout)
            # 调用处理报文的方法，把接口信息加入到测试报告
            deal_with_res(data, res)
            return res
        # 如果传入的json，就传入json，适用大部分接口
        if json:
            res = self.s.post(self.url + url, json=json, timeout=self.timeout)
            # 调用处理报文的方法，把接口信息加入到测试报告
            deal_with_res(json, res)
            return res
        # 有些post接口是什么也不传的，兼容这种情况
        res = self.s.post(self.url + url, timeout=self.timeout)
        # 调用处理报文的方法，把接口信息加入到测试报告
        deal_with_res(json, res)
        return res

    def put_request(self, url, data=None, json=None):
        if data:
            res = self.s.put(self.url + url, data=data, timeout=self.timeout)
            deal_with_res(data, res)
            return res
        if json:
            res = self.s.put(self.url + url, json=json, timeout=self.timeout)
            deal_with_res(json, res)
            return res
        res = self.s.put(self.url + url, timeout=self.timeout)
        deal_with_res(json, res)
        return res

    # 魔法函数
    def __del__(self):
        """
        当实例被销毁时，释放掉session所持有的连接
        :return:
        """
        if self.s:
            self.s.close()


# # 测试一下下
# if __name__ == '__main__':
#     # # 这里域名设置的是http://httpbin.org，懂得都懂
#     # get_res = Requests().get_request("/svip/homePage/OverviewUserGroupDoneRate")
#     # print(get_res.text, "\n", )
