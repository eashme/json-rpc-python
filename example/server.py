from rpc.sc import SocketRpcServer

server = SocketRpcServer(host="localhost", port=8875)


@server.method
def Echo(msg, **kwargs):
    return {
        "Msg": msg,
        "Code": 999,
    }


print("server running ...")
server.server_and_listen()
