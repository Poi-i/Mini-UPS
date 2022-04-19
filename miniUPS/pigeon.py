from struct import pack
from time import sleep
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint
from protos import world_ups_pb2 as World_UPS
from protos import UA_pb2 as UA
import PBwrapper
from django.db.models import Q
import website.models as md

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


def handle_world(u_rsp: World_UPS.UResponses, socket_to_world, socket_to_amz):
    print("recv from world: " + str(u_rsp))
    # send ack to world

    for u_finished in u_rsp.completions:
        # renew truck's status
        # tell amz truck has arrived
        pass

    for u_delivery_made in u_rsp.delivered:
        # renew truck's status
        # renew package's status -> delivered
        pass

    for ack in u_rsp.acks:
        # terminate the request from our side, where ack = seqnum of our req
        pass

    return


'''
pick an IDLE or DELIVERING truck to pickup packages
@return: truck_id
'''


def pick_truck():
    while True:
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


def varify_user(username, package):
    user = md.User.objects.filter(name=username)
    if user != None:
        # update package's username
        package.user = username
        package.save()
        return True
    return False


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
    # World part
    # pick an idle or delivering truck to pickup
    truck_id = pick_truck()
    ship_id = pickup.shipment_id
    # TODO: atomically increase seqnum += 1
    global seqnum
    # send UCommands to World
    write_to_world(socket_to_world, World_UPS.UCommands().pickups.append(PBwrapper.go_pickup(
        truck_id, pickup.whid, seqnum)))
    # update truck status to Traveling
    truck = md.Truck.objects.update(status='TRAVELING')
    # Amazon part
    # insert to Package
    package = md.Package.objects.create(
        shipment_id=ship_id, truckid=truck_id, x=pickup.x, y=pickup.y, status='in WH')
    if pickup.HasField("ups_username"):
        is_binded = varify_user(pickup.ups_username, package)  # TODO
        # package = md.Package.objects.get(shipment_id = pickup.shipment_id).update(user=)
    pac_pickup_res = PBwrapper.pac_pickup_res(
        package.tracking_id, is_binded, ship_id, truck_id)
    # send response to Amazon
    write_to_amz(socket_to_amz, UA.UAmessage(
    ).pickup_res.CopyFrom(pac_pickup_res))
    return


'''
 handle Amazon request "ASendAllLoaded"
 @recv from Amazon:
    ASendAllLoaded: truckid, packages
 @send to World:
    UGoDeliver: truckid, packages, seqnum
'''


def handle_amz_all_loaded(bind_upsuser: UA.ASendAllLoaded, socket_to_world, socket_to_amz):

    return


'''
 handle Amazon request "ABindUpsUser"
'''


def handle_amz_bindups(pickup: UA.ABindUpsUser, socket_to_world, socket_to_amz):
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
