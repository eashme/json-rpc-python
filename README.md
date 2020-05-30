# json-rpc-python
json格式socket方式传输的python版本server端,可以直接被go 标准库中的 json-rpc client调起

## UseAge:

### python Server:

```
from rpc.sc import SocketRpcServer

server = SocketRpcServer(host="127.0.0.1", port=8875)


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

### Go client:
```
cli, err := jsonrpc.Dial("tcp4", "127.0.0.1:8875")
if err != nil {
    return nil, err
}

defer cli.Close()

req := struct {
    Msg string `json:"msg"`
}{Msg: "Ok !"}

rsp := struct {
    Msg  string
    Code int
}{}

err := cli.Call("Echo", &req, &rsp)
if err != nil {
    log.Fatalf("failed got rpc rsp, err:%v", err)
}
log.Infof("got rpc rsp: %+v",rsp)

```
