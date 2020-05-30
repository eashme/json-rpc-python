# json-rpc-python
json格式socket方式传输的python版本server端,可以直接被go 标准库中的 json-rpc client调起

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

