from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint


class UPS:
    def __init__(self, to_world_socket=None, to_amazon_socket=None):
        self.to_world_socket = to_world_socket
        self.to_amazom_socket = to_amazon_socket

    def set_world_socket(self, to_world_socket):
        self.to_world_socket = to_world_socket

    def set_amazon_socket(self, to_amazon_socket):
        self.to_amazom_socket = to_amazon_socket

    def write_msg(self, s, msg):
        string_msg = msg.SerializeToString()
        _EncodeVarint(s.send, len(string_msg), None)
        s.send(string_msg)

    def write_to_world(self, msg):
        self.write_msg(self.to_world_socket, msg)
    
    def write_to_amz(self, msg):
        self.write_msg(self.to_amazom_socket, msg)

    def recv_from_world(self):
        return