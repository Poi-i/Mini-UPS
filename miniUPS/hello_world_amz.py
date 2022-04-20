import sys
from concurrent.futures import ThreadPoolExecutor
import socket
from threading import Thread
import threading
from time import sleep
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint
from protos import world_ups_pb2 as World_UPS
from protos import UA_pb2 as UA
import PBwrapper
from django.db.models import Q
import website.models as md
import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "miniUPS.settings")
if django.VERSION >= (1, 7):
    django.setup()


# import pigeon


executer = ThreadPoolExecutor(50)
lock = threading.Lock()
lock_socket_world = threading.Lock()
lock_socket_amz = threading.Lock()

request_map = {}
seq_num = 0
world_id = None


def get_socket_to_amz():
    ups_host = '127.0.0.1'
    ip_port_amz = (ups_host, 8888)
    listen_to_amz = socket.socket()
    listen_to_amz.bind(ip_port_amz)
    listen_to_amz.listen(5)
    socket_to_amz, address = listen_to_amz.accept()
    return socket_to_amz


def get_socket_to_world():
    world_host = 'vcm-26474.vm.duke.edu'
    ip_port_w = (world_host, 12345)
    socket_to_world = socket.socket()
    socket_to_world.connect(ip_port_w)
    return socket_to_world


def get_seqnum() -> int:
    global seq_num
    lock.acquire()
    to_ret = seq_num
    seq_num += 1
    lock.release()
    return to_ret


def get_world_id_from_input():
    # ask user to reconnect or create a new world
    return None


def dock_amz(socket_to_world, socket_to_amz):
    while True:
        au_msg = recv_from_amz(socket_to_amz)
        executer.submit(handle_amz, au_msg,
                        socket_to_world, socket_to_amz)


def dock_world(socket_to_world, socket_to_amz):
    while True:
        u_resp = recv_from_world(socket_to_world)
        executer.submit(handle_world, u_resp,
                        socket_to_world, socket_to_amz)


"""
Helper function for writing, write msg to socket_
"""


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


def write_to_world(socket_to_world, msg):
    # if (not msg.Is("UConnect")):
    #     Ucommands = World_UPS.UCommands()
    #     if(msg.Is("UGoPickup")):
    #         Ucommands.pickups.append(msg)
    #     if(msg.Is("UGoDeliver")):
    #         Ucommands.deliveries.append(msg)
    #     if(msg.Is("UQuery")):
    #         Ucommands.queries.append(msg)
    #     write_msg(to_world_socket, Ucommands)
    # else:
    # TODO: set simspeed, disconnect, acks
    # write_msg(socket_to_world, msg)
    string_msg = msg.SerializeToString()
    lock_socket_world.acquire()
    _EncodeVarint(socket_to_world.send, len(string_msg), None)
    socket_to_world.send(string_msg)
    lock_socket_world.release()


def write_to_amz(socket_to_amz, msg: UA.UAmessage):
    # write_msg(to_amazom_socket, msg)
    string_msg = msg.SerializeToString()
    lock_socket_amz.acquire()
    _EncodeVarint(socket_to_amz.send, len(string_msg), None)
    socket_to_amz.send(string_msg)
    lock_socket_amz.release()

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


def connect_to_word(truck_num, socket_to_world) -> bool:
    msg = World_UPS.UConnect()
    msg.isAmazon = False
    for i in range(truck_num):
        truck_to_add = msg.trucks.add()
        truck_to_add.id = i
        truck_to_add.x = i
        truck_to_add.y = i
    msg.isAmazon = False
    write_msg(socket_to_world, msg)  # no need for repeat
    uconnected = World_UPS.UConnected()
    uconnected.ParseFromString(recv_msg(socket_to_world))
    print("world id: " + str(uconnected.worldid))
    print("result: " + uconnected.result)
    world_id = uconnected.worldid
    if uconnected.result == "connected!":
        # TODO: write truck to db
        return world_id, True
    return world_id, False


def reconnect_to_word(world_id, socket_to_world) -> bool:
    msg = World_UPS.UConnect()
    msg.worldid = world_id
    msg.isAmazon = False
    write_msg(socket_to_world, msg)
    uconnected = World_UPS.UConnected()
    uconnected.ParseFromString(recv_msg(socket_to_world))
    print("world id: " + str(uconnected.worldid))
    print("result: " + uconnected.result)
    if uconnected.result == "connected!":
        return world_id, True
    return world_id, False


"""
send ack back to each item in UResponses structs
"""


def handle_world_send_ack(u_rsp, socket_to_world):
    seqnum_list = []
    for u_finished in u_rsp.completions:
        print("before u_finished: " + seqnum_list + "\n")
        seqnum_list.append(u_finished.seqnum)
        print("after u_finished: " + seqnum_list + "\n")

    for u_delivery_made in u_rsp.delivered:
        print("before u_delivery_made: " + seqnum_list + "\n")
        seqnum_list.append(u_delivery_made.seqnum)
        print("after u_delivery_made: " + seqnum_list + "\n")

    for ack_ in u_rsp.acks:
        print("before ack_: " + seqnum_list + "\n")
        seqnum_list.append(ack_.seqnum)
        print("after ack_: " + seqnum_list + "\n")

    for trcuk_status in u_rsp.truckstatus:
        print("before trcuk_status: " + seqnum_list + "\n")
        seqnum_list.append(trcuk_status.seqnum)
        print("after trcuk_status: " + seqnum_list + "\n")

    for err_ in u_rsp.error:
        print("before err_: " + seqnum_list + "\n")
        seqnum_list.append(err_.seqnum)
        print("after err_: " + seqnum_list + "\n")

    if seqnum_list:
        u_commands = World_UPS.UCommands()
        u_commands.acks.extend(seqnum_list)
        # synchronized out?
        write_to_world(socket_to_world, u_commands)


"""
Handle UFinished
"""


def handle_world_finished(u_finished, socket_to_world, socket_to_amz):
    truck_id_ = u_finished.truckid
    print("World tells truck[" + str(truck_id_) +
          "]" + " arrived at warehouse" + "\n")
    truck_status = u_finished.status
    print("truck[" + str(truck_id_) + "]'s status: " + truck_status + "\n")
    if truck_status == "ARRIVE WAREHOUSE":
        # tell amz truck has arrived
        ua_msg = UA.UAmessage()
        ua_msg.UsendArrive.truck_id = truck_id_
        print("send to amz: " + ua_msg + "\n")
        # lock on socket?
        write_to_amz(socket_to_amz, ua_msg)
    # renew truck's status
    # lock on row?
    truck = md.Truck.objects.get(truckid=truck_id_)
    truck.status = truck_status
    truck.save()


def handle_world_delievered(u_delivery_made, socket_to_world, socket_to_amz):
    print(u_delivery_made)
    package_id = u_delivery_made.packageid

    # update package status
    package = md.Package.objects.get(shipment_id=package_id)
    package.status = "delivered"
    package.save()

    # tell amz package delievered
    ua_msg = UA.UAmessage()
    ua_msg.UPacDelivered.shipment_id = package_id
    print("send to amz: " + ua_msg + "\n")
    # lock on socket?
    write_to_amz(socket_to_amz, ua_msg)


def handle_world_truck_status(truck_status, socket_to_world, socket_to_amz):
    return


def handle_world(u_rsp: World_UPS.UResponses, socket_to_world, socket_to_amz):
    print("recv from world: " + str(u_rsp))
    # send ack to world
    handle_world_send_ack(u_rsp, socket_to_world)

    for u_finished in u_rsp.completions:
        # renew truck's status
        # tell amz truck has arrived
        handle_world_finished(u_finished, socket_to_world, socket_to_amz)

    for u_delivery_made in u_rsp.delivered:
        # renew truck's status
        # renew package's status -> delivered
        handle_world_delievered(
            u_delivery_made, socket_to_world, socket_to_amz)

    for ack_ in u_rsp.acks:
        # terminate the request from our side, where ack = seqnum of our req
        if ack_ in request_map:
            request_map[ack_].cancel()
            del request_map[ack_]

    for truck_status in u_rsp.truckstatus:
        handle_world_truck_status(truck_status, socket_to_world, socket_to_amz)

    for err_ in u_rsp.error:
        print(err_)

    if u_rsp.HasField("finished") and u_rsp.finished:  # close connection
        print("disconnect successfully")


def pick_truck(wh_id):
    while True:
        # check whether already exist truck on the way to the WH
        assigned_truck = md.AssignedTruck.objects.filter(whid=wh_id).first()
        if(assigned_truck != None):
            return assigned_truck.truckid
        # sort the result sorted from IDLE to DELIVERING, pick the 1st one
        truck = md.Truck.objects.filter(Q(status='IDLE') | Q(
            status='DELIVERING')).order_by('-status').first()
        if truck != None:
            print("the picked truck is:" + truck)
            return truck.truckid
        else:
            # if no truck meet requirement, wait for 5s and try again
            sleep(5)
            continue


'''
verify the validation of ups username from Amazon
@return: true if username valid, false vice versa
'''


def verify_user(username, package):
    user = md.User.objects.filter(name=username)
    if user != None:
        # update package's username
        package.user = username
        package.save()
        print("updated package = " + package)
        return True
    return False


'''
handle World part for handle_amz_pickup
'''


def w_pickup(truck_id, wh_id, socket_to_world):
    # insert into DB: AssignedTruck
    md.AssignedTruck.objects.create(whid=wh_id, truckid=truck_id)
    # global seqnum  # TODO: atomically increase seqnum += 1
    seqnum_ = get_seqnum()
    go_pickup = PBwrapper.go_pickup(truck_id, wh_id, seqnum_)
    print("send go_pickup = " + go_pickup)
    # send UCommands(UGoPickup) to World
    write_to_world(socket_to_world,
                   World_UPS.UCommands().pickups.append(go_pickup))
    # update truck status to Traveling
    truck = md.Truck.objects.update(status='TRAVELING')
    print("updated truck = " + truck)


'''
handle Amazon part for handle_amz_pickup
'''


def a_pickup(truck_id, pickup: UA.APacPickup, socket_to_amz):
    ship_id = pickup.shipment_id
    # insert into DB: Package
    package = md.Package.objects.create(
        shipment_id=ship_id, truckid=truck_id, x=pickup.x, y=pickup.y, status='in WH')
    # update package with username if valid
    if pickup.HasField("ups_username"):
        is_binded = verify_user(pickup.ups_username, package)
    pac_pickup_res = PBwrapper.pac_pickup_res(
        package.tracking_id, is_binded, ship_id, truck_id)

    print("send pac_pickup_res = " + pac_pickup_res)

    # send response to Amazon
    write_to_amz(socket_to_amz, UA.UAmessage(
    ).pickup_res.CopyFrom(pac_pickup_res))


'''
 handle Amazon request "APacPickup"
 @recv from Amazon:
    APacPickup: whid, shipment_id, ups_username, x, y
 @send to World:
    UGoPickup: truckid, whid, seqnum
 @send to Amazon:
    UPacPickupRes: tracking_id, is_binded, shipment_id, truck_id
'''


def handle_amz_pickup(pickup: UA.APacPickup, socket_to_world, socket_to_amz):

    print("received APacPickup = " + pickup)
    wh_id = pickup.whid
    # pick an idle or delivering truck to pickup
    truck_id = pick_truck(wh_id)

    # World part
    w_pickup(truck_id, wh_id, socket_to_world)
    # Amazon part
    a_pickup(truck_id, pickup, socket_to_amz)
    return


'''
 handle Amazon request "ASendAllLoaded"
 @recv from Amazon:
    ASendAllLoaded: truckid, packages(x,y,shipment_id, 
                                        item(product_id, description, count))
 @send to World:
    UGoDeliver: truckid, packages(packageid,x,y), seqnum
'''


def handle_amz_all_loaded(all_loaded: UA.ASendAllLoaded, socket_to_world, socket_to_amz):
    # parse ASendAllLoaded, insert into db: Package
    pac_list = []
    for package in all_loaded.packages:
        ship_id = package.shipment_id
        track_id = md.Package.objects.filter(
            shipment_id=ship_id).tracking_id
        for item in package.items:
            # insert into Product
            item = md.Item.objects.create(
                id=item.id, description=item.description, count=item.count, tracking_id=track_id)
            print("insert item: " + item)
        pac_list.append(PBwrapper.gene_package(ship_id, package.x, package.y))

    # global seqnum  # TODO: atomically increase seqnum += 1
    # send Ucommands(UGoDeliver) to World
    seqnum_ = get_seqnum()
    go_deliver = PBwrapper.go_deliver(all_loaded.truck_id, pac_list, seqnum_)
    write_to_world(socket_to_world,
                   World_UPS.UCommands().deliveries.append(go_deliver))
    return


'''
 handle Amazon request "ABindUpsUser"
 @recv from Amazon:
    ABindUpsUser: shipment_id, ups_username
 @send to Amazon:
    UBindRes: shipment_id, is_binded
'''


def handle_amz_bindups(bind_upsuser: UA.ABindUpsUser, socket_to_world, socket_to_amz):
    ship_id = bind_upsuser.shipment_id
    package = md.Package.objects.filter(shipment_id=ship_id)
    # verify user validaty, update package is valid
    bind_res = PBwrapper.bind_res(
        ship_id, verify_user(bind_upsuser.ups_username, package))
    # send response to Amazon
    write_to_amz(socket_to_amz, UA.UAmessage.bind_res.CopyFrom(bind_res))
    return


def handle_amz(au_msg: UA.AUmessage, socket_to_world, socket_to_amz):
    # handle specific amazon request
    if au_msg.HasField("pickup"):
        handle_amz_pickup(au_msg.pickup, socket_to_world, socket_to_amz)
    if au_msg.HasField("all_loaded"):
        handle_amz_all_loaded(
            au_msg.all_loaded, socket_to_world, socket_to_amz)
    if au_msg.HasField("bind_upsuser"):
        handle_amz_bindups(au_msg.bind_upsuser, socket_to_world, socket_to_amz)
    return


'''
send worldid to Amazon
@send: 
    USendWorldId: worldid
'''


def a_worldid(socket_to_amz, worldid):
    world_id = PBwrapper.send_WorldId(worldid)
    write_to_amz(socket_to_amz, UA.UAmessage().world_id.CopyFrom(world_id))
    return


def main():
    global world_id
    # socket_to_world = None
    socket_to_amz = None
    socket_to_world = get_socket_to_world()
    # socket_to_amz = get_socket_to_amz()

    # send connect/reconnect to world
    retry = 5
    if sys.argv[1] == 'create':
        truck_num = int(sys.argv[2])
        print("# of trucks to create: " + str(truck_num) + "\n")
        world_id, is_connected = connect_to_word(truck_num, socket_to_world)
        while retry and not is_connected:
            print("Connect to world failed, retrying...")
            world_id, is_connected = connect_to_word(
                truck_num, socket_to_world)
            retry -= 1
    elif sys.argv[1] == 'reconnect':
        world_id = int(sys.argv[2])
        world_id, is_connected = reconnect_to_word(world_id, socket_to_world)
        while retry and not is_connected:
            print("Connect to world failed, retrying...")
            world_id, is_connected = reconnect_to_word(
                world_id, socket_to_world)
            retry -= 1
    else:
        print("Please check your input: " + str(sys.argv) + "\n")
        print(
            "Usage: python3 hello_world_amz.py create [truck_num] for create new world" + "\n")
        print(
            "Usage: python3 hello_world_amz.py reconnect [world_id] for create new world" + "\n")
        sys.exit()
    # return
    # send the world_id to amz
    a_worldid(socket_to_amz, world_id)
    # start one thread to dock amz
    t_to_amz = Thread(target=dock_amz, args=(socket_to_world, socket_to_amz))
    t_to_amz.start()

    # start one thread to dock world
    t_to_world = Thread(target=dock_world, args=(
        socket_to_world, socket_to_amz))
    t_to_world.start()

    t_to_world.join()
    t_to_amz.join()
    socket_to_world.close()
    socket_to_amz.close()


if __name__ == "__main__":
    main()
