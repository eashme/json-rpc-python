# json-rpc-python
json格式socket方式传输的python版本server端,可以直接被go 标准库中的 json-rpc client调起

> bg: 公司的算法模型需要部署到线上,但是公司的DevOps流水线暂时不支持python服务构建,由此临时造了个轮子配合golang服务调起python程序,后续有空再完善rpc-client吧。

### UseAge:
```
from rpc.sc import SocketRpcServer

server = SocketRpcServer(host="localhost", port=8875)


@server.method
def Echo(msg, **kwargs):
    print(msg)
    return {
        "Msg": msg,
        "Code": 999,
    }


print("server running ...")
server.server_and_listen()

```

