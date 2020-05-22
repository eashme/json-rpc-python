import json


class Codec:
    """
    codec 接口, 该类用于规范化编解码工具类定义
    该类子类必须实现以下两个方法,否则无法使用

    marshal: 用于将python数据类型转换为bytes类型

    unmarshal: 用于将bytes类型转换为 python数据类型
    """

    def marshal(self, data) -> bytes:
        """
        用于将python类型数据编码为 bytes类型
        :param data: python 类型数据
        :return:  data编码后的bytes
        """
        raise NotImplemented

    def unmarshal(self, raw: bytes):
        """
        用于将str类型数据解码为python类型数据
        :param raw: 原始bytes
        :return: data 解码后得python类型数据
        """
        raise NotImplemented

    def recv_eof(self) -> bytes:
        """
        接收数据停止标记
        :return:
        """
        raise NotImplemented


class DefaultCodec(Codec):
    """
    本次实现得默认编解码工具, 采用 json进行编解码
    后续若对性能要求提高,可以增加其他编码方式,如 bit编码等
    """

    def marshal(self, data) -> bytes:
        return json.dumps(data).encode()

    def unmarshal(self, raw: bytes):
        return json.loads(raw.decode())

    def recv_eof(self) -> bytes:
        return bytes(10)  # bytes(10) 即\n换行符, ASCII码为10
