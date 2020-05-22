import logging
import socket
from concurrent.futures import ThreadPoolExecutor
from rpc.codec import DefaultCodec, Codec
from rpc.err import ErrBaseClass, ErrLackOfNecessaryKey, ErrTargetMethodNotFound, ErrUnKnownParams
from rpc.utils import get_key


# 这里不保持长连接, 下游请求按照单次请求进行, 可以在服务下游对进行连接池处理,调用的时候从连接池获取可达到性能最优
# 一直保持长连接的方案,需要更多更多的工作量,短时间内可能无法完成


class RpcRequest:
    def __init__(self, method, req_id, params=None):
        """
        rpc 调用请求
        :param method:
        :param req_id:
        :param params:
        """
        self.method = method
        self.id = req_id
        self.params = params


class RpcResponse:
    def __init__(self, req_id, result=None, error=None):
        """
        rpc 调用响应
        :param req_id: 请求id
        :param result: 请求的响应结果,可以进行编码的python类型数据,目前仅仅支持Json编码
        :param error:  处理该请求触发的 Exception的子类
        """
        self.req_id = req_id
        self.error = error
        self.result = result


class SocketRpcServer:
    def __init__(self, host="0.0.0.0", port=8875, timeout=3000, codec=None, pool_size=4,
                 max_length_per_req=1024 * 1024 * 10):
        """
        :param host: 服务host地址
        :param port:  服务端口号
        :param timeout: 单次请求处理最大市场
        :param codec: 数据编码解码方式 不填默认为json
        :param max_length_per_req: 单次请求最大传输数据长度
        :param pool_size: 协程池容量
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self._methods = {}  # 用于存储被装饰过得方法
        self.max_length_per_req = max_length_per_req
        # 初始化创建线程池
        self.thread_pool = ThreadPoolExecutor(max_workers=pool_size)
        if codec is None:
            self.codec = DefaultCodec()
        else:
            if not isinstance(codec, Codec):
                raise ErrBaseClass(Codec, codec)
            self.codec = codec

    def server_and_listen(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen(5)

        while True:
            client, addr = s.accept()
            self.thread_pool.submit(self._handler,client, addr)

    def method(self, *args, **kwargs):
        timeout = self.timeout
        if "timeout" in kwargs.keys():
            timeout = kwargs["timeout"]

        for arg in args:
            if callable(arg):
                # 将注册得handler函数保存
                self._methods[arg.__name__] = RpcMethod(arg.__name__, arg, timeout)
        if len(args):
            return args[0]

        return None

    def _handler(self, client, addr):

        bs = b""
        while True:
            # 单次请求处理字节长度超限 直接break, 防止请求数据量过大撑爆内存
            if len(bs) > self.max_length_per_req:
                logging.error("bytes length over limit ")
                break

            b = client.recv(512)  # 不停的读,直到读取到一个换行符为止,代表本次rpc调用的数据传输结束

            bs += b
            # 接收到了终止符
            if len(b) > 0 and bytes(b[-1]) == self.codec.recv_eof():
                req = self._unmarshal_request(bs)

                resp = self._call_method(req)
                # 将请求发送回去
                client.send(self._marshal_response(resp))

                # 处理完成,直接break,想要再次调用需要再次启一个链接
                break

    def _call_method(self, req: RpcRequest) -> RpcResponse:

        rpc_method = get_key(self._methods, req.method)

        # 没有找到想要调用的rpc方法,直接返回err
        if rpc_method is None:
            return RpcResponse(req_id=req.id, error=ErrTargetMethodNotFound(req.method))

        resp = None
        try:
            # 执行函数,获取执行结果
            result = rpc_method(**req.params)
        except Exception as e:
            print(e)
            resp = RpcResponse(req_id=req.id, error=e)
        else:
            resp = RpcResponse(req_id=req.id, result=result)

        return resp

    def _unmarshal_request(self, raw: bytes) -> RpcRequest:
        """
        用以解码请求
        Go的json rpc request格式为:{"method":"func1",params:[{"param1":11,"param2":"name"}],id:1}

        :param raw: socket接收到的原始bytes
        :return: 解析后得到的数据
        """

        req = self.codec.unmarshal(raw)
        method = get_key(req, "method")
        if method is None:
            raise ErrLackOfNecessaryKey("method")
        # 参数可能为None,因为可能不需要参数
        params = get_key(req, "params")
        if isinstance(params, list) and len(params) > 0:
            params = params[0]

        # 非空且不是dict则说明是意料之外的参数内容,直接报错
        if params is not None and not isinstance(params, dict):
            raise ErrUnKnownParams(params)

        # 请求id
        req_id = get_key(req, "id")
        if id is None:
            raise ErrLackOfNecessaryKey("id")

        return RpcRequest(method=method, req_id=req_id, params=params)

    def _marshal_response(self, resp: RpcResponse) -> bytes:
        """
        用以对响应进行编码
        Go的json rpc response格式为:{"id":0,"result":b"{"message":"ok","RCode":1}", error:"it's wrong"}
        :param data: 要进行编码的响应  Python数据类型
        :return: 编码后得到的bytes类型
        """
        rsp_dict = dict()

        rsp_dict["id"] = resp.req_id

        if resp.result is not None:
            rsp_dict["result"] = resp.result

        if resp.error is not None:
            # 获取异常信息
            rsp_dict["error"] = resp.error.__str__()

        return self.codec.marshal(rsp_dict)


class RpcMethod:

    def __init__(self, method_name, method_func, timeout=None, err_handler=None):
        """
        Rpc函数
        :param method_name: 函数名
        :param method_func: 函数对象,该函数对象返回值个数固定为1
        :param timeout: 该函数单次处理最大时常
        """
        self.name = method_name
        self.func = method_func
        self.timeout = timeout
        self.err_handler = err_handler

    def __call__(self, **kwargs):
        """
        rpc方法执行部分
        :param args:
        :param kwargs:
        :return:
        """
        # todo 这里加上单次调用时长限制
        res = self.func(**kwargs)

        return res
