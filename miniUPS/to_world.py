import socket
import pigeon
from protos import world_ups_pb2 as World_UPS


def get_socket_to_amz():
    ups_host = '127.0.0.1'
    ip_port_amz = (ups_host, 8888)
    listen_to_amz = socket.socket()
    listen_to_amz.bind(ip_port_amz)
    listen_to_amz.listen(5)
    socket_to_amz, address = listen_to_amz.accept()
    return socket_to_amz


def get_socket_to_world():
    world_host = 'vcm-26338.vm.duke.edu'
    ip_port_w = (world_host, 12345)
    socket_to_world = socket.socket()
    socket_to_world.connect(ip_port_w)
    return socket_to_world


def get_world_id_from_input():
    # ask user to reconnect or create a new world
    return None


def main():
    world_id = get_world_id_from_input()
    socket_to_world = get_socket_to_world()
    socket_to_amz = get_socket_to_amz()

    # send connect/reconnect to world

    # send the world_id to amz

    # start one process to dock world
    p_to_world = Process(target=dock_world, args=(
        socket_to_world, socket_to_amz))
    # start one process to dock amz
    p_to_amz = Process(target=dock_amz, args=(socket_to_world, socket_to_amz))


if __name__ == "__main__":
    main()
