from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint
from protos import world_ups_pb2 as World_UPS
from protos import UA_pb2 as UA

'''
communication tool to Amazon and World
'''

# Helper function for writing, write msg to socket_


def write_msg(socket_, msg):
    string_msg = msg.SerializeToString()
    _EncodeVarint(socket_.send, len(string_msg), None)
    socket_.send(string_msg)

# Helper function for receiving, recv from socket_


def recv_msg(socket_) -> str:
    var_int_buff = []
    while True:
        buf = socket_.recv(1)
        var_int_buff += buf
        msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
        if new_pos != 0:
            break
    whole_message = socket_.recv(msg_len)
    return whole_message


def write_to_world(to_world_socket, msg):
    write_msg(to_world_socket, msg)


def write_to_amz(to_amazom_socket, msg: UA.UAmessage):
    write_msg(to_amazom_socket, msg)

# Recv from world's response after successfully connected


def recv_from_world(to_world_socket):
    whole_message = recv_msg(to_world_socket)
    world_res = World_UPS.UResponses()
    world_res.ParseFromString(whole_message)
    return world_res


def recv_from_amz(to_amazom_socket) -> UA.AUmessage:
    whole_message = recv_msg(to_amazom_socket)
    au_msg = UA.AUmessage()
    au_msg.ParseFromString(whole_message)
    return au_msg


def connect_to_word(truck_num, to_world_socket) -> bool:
    msg = World_UPS.UConnect()
    msg.isAmazon = False
    for i in range(truck_num):
        truck_to_add = msg.trucks.add()
        truck_to_add.id = i
        truck_to_add.x = 0
        truck_to_add.y = 0
    msg.isAmazon = False
    write_to_world(to_world_socket, msg)
    uconnected = World_UPS.UConnected()
    uconnected.ParseFromString(recv_msg(to_world_socket))
    print("world id: " + str(uconnected.worldid))
    print("result: " + uconnected.result)
    if uconnected.result == "connected!":
        return True
    return False


def reconnect_to_word(world_id, to_world_socket) -> bool:
    msg = World_UPS.UConnect()
    msg.worldid = world_id
    msg.isAmazon = False
    write_to_world(to_world_socket, msg)
    uconnected = World_UPS.UConnected()
    uconnected.ParseFromString(recv_msg(to_world_socket))
    print("world id: " + str(uconnected.worldid))
    print("result: " + uconnected.result)
    if uconnected.result == "connected!":
        return True
    return False


def handle_world(u_rsp, socket_to_world, socket_to_amz):
    return
def handle_amz(au_msg, socket_to_world, socket_to_amz):
    return