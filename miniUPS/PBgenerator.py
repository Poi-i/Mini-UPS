from typing import List
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint
from protos import world_ups_pb2 as World_UPS
from protos import UA_pb2 as UA
import pigeon
import PBparser

seqnum = 0
# request to world

# UGoPickup:truckid, whid = 2, seqnum


class PBgenerator:
    def __init__(self, to_world_socket, to_amazom_socket) -> None:
        self.to_world_socket = to_world_socket
        self.to_amazom_socket = to_amazom_socket
        self.pbParser = PBparser()

    def go_pickup(self, truckid, whid) -> World_UPS.UGoPickup:
        global seqnum
        seqnum += 1
        Ugo_pickup = World_UPS.UGoPickup()
        Ugo_pickup.truckid = truckid
        Ugo_pickup.whid = whid
        Ugo_pickup.seqnum = seqnum
        return Ugo_pickup

    def gene_package(self, packageid, x, y) -> World_UPS.UDeliveryLocation:
        Upackage = World_UPS.UDeliveryLocation()
        Upackage.packageid = packageid
        Upackage.x = x
        Upackage.y = y
        return Upackage

    def go_deliver(self, truckid, packages: List[World_UPS.UDeliveryLocation]) -> World_UPS.UGoDeliver:
        global seqnum
        seqnum += 1
        Ugo_deliver = World_UPS.UGoDeliver()
        Ugo_deliver.truckid = truckid
        for package in packages:
            Ugo_deliver.packages.append(package)
        Ugo_deliver.seqnum = seqnum
        return Ugo_deliver
    
    def query_truck(self, truckid) -> World_UPS.UQuery:
        global seqnum
        seqnum += 1
        Uquery = World_UPS.UQuery()
        Uquery.truckid = truckid
        Uquery.seqnum = seqnum
        return Uquery
