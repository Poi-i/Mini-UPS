import socket
from hello_world_amz import recv_msg
from hello_world_amz import write_msg
from protos import UA_pb2 as UA
from protos import world_amazon_pb2 as World_AMZ

socket_to_ups = socket.socket()
socket_amz_w = socket.socket()

try:
    ip_port = ('127.0.0.1', 54321)
    socket_to_ups.connect(ip_port)

    msg_str, _ = recv_msg(socket_to_ups)
    ua_msg = UA.UAmessage()
    ua_msg.ParseFromString(msg_str)
    print("recv from ups: " + str(ua_msg))

    # ip_port_world = ('vcm-26474.vm.duke.edu', 23456)
    # socket_amz_w = socket_amz_w.connect(ip_port_world)
    # a_connect = World_AMZ.AConnect()
    # a_connect.worldid = ua_msg.world_id.world_id
    # a_connect.isAmazon = True
    # wh_1 = World_AMZ.AInitWarehouse()
    # wh_1.id = 1
    # wh_1.x = 8
    # wh_1.y = 7
    # a_connect.initwh.extend(wh_1)
    # write_msg()

    # err_msg = "{}"
    # socket_to_ups.send(err_msg.encode())

finally:
    socket_to_ups.close()
    print("socket_to_ups close")