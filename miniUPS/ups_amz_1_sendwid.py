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

    ua_msg = UA.AUmessage()
    ua_msg.pickup.whid = 1
    ua_msg.pickup.shipment_id = 1
    ua_msg.pickup.x = 5
    ua_msg.pickup.y = 6
    write_msg(socket_to_ups, ua_msg)
    msg_str, _ = recv_msg(socket_to_ups)
    ua_msg = UA.UAmessage()
    ua_msg.ParseFromString(msg_str)
    print("recv from ups: " + str(ua_msg))

    while True:
        continue
except:
    socket_to_ups.close()
    print("socket_to_ups close")
finally:
    # socket_to_ups.close()
    print("socket_to_ups close")