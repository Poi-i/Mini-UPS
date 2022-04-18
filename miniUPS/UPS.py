from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint
from protos import world_ups_pb2 as World_UPS
from protos import UA_pb2 as UA

class UPS:
    def __init__(self, world_id = -1, to_world_socket=None, to_amazon_socket=None):
        self.world_id = world_id
        self.to_world_socket = to_world_socket
        self.to_amazom_socket = to_amazon_socket

    def set_world_socket(self, to_world_socket):
        self.to_world_socket = to_world_socket

    def set_amazon_socket(self, to_amazon_socket):
        self.to_amazom_socket = to_amazon_socket

    # Helper function for writing message
    def write_msg(self, socket_, msg):
        string_msg = msg.SerializeToString()
        _EncodeVarint(socket_.send, len(string_msg), None)
        socket_.send(string_msg)

    # Helper function for receiving message
    def recv_msg(self, socket_) -> str:
        var_int_buff = []
        while True:
            buf = socket_.recv(1)
            var_int_buff += buf
            msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
            if new_pos != 0:
                break
        whole_message = socket_.recv(msg_len)
        return whole_message

    def write_to_world(self, msg):
        self.write_msg(self.to_world_socket, msg)

    def write_to_amz(self, msg: UA.UAmessage):
        self.write_msg(self.to_amazom_socket, msg)

    # Recv from world's response after successfully connected
    def recv_from_world(self):
        whole_message = self.recv_msg(self.to_world_socket)
        world_res = World_UPS.UResponses()
        world_res.ParseFromString(whole_message)
        return world_res

    def recv_from_amz(self) -> UA.AUmessage:
        whole_message = self.recv_msg(self.to_amazom_socket)
        au_msg = UA.AUmessage()
        au_msg.ParseFromString(whole_message)
        return au_msg
    
    def reconnect_to_word(self) -> bool:
        msg = World_UPS.UConnect()
        msg.worldid = self.world_id
        msg.isAmazon = False
        self.write_to_world(msg)
        uconnected = World_UPS.UConnected()
        uconnected.ParseFromString(self.recv_msg(self.to_world_socket))
        if uconnected.result == "connected!":
            return True
        return False