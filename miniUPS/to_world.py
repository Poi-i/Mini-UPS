import socket
from protos import world_ups_pb2 as World_UPS


def main():
    world_host = 'vcm-26338.vm.duke.edu'
    ip_port = (world_host, 12345)
    socket_to_world = socket.socket()
    socket_to_world.connect(ip_port)
    world_id = None
    
    # create new world or receonnect
    if world_id:
        return
        # get the host name of world from user input (default localhost)

        # set connect info


if __name__ == "__main__":
    main()
