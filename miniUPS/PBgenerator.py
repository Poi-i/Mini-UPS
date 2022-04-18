from typing import List
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint
from protos import world_ups_pb2 as World_UPS
from protos import UA_pb2 as UA
import pigeon
import PBparser


class PBgenerator:
    def __init__(self, to_world_socket, to_amazom_socket) -> None:
        self.to_world_socket = to_world_socket
        self.to_amazom_socket = to_amazom_socket
        self.pbParser = PBparser()
        self.seqnum = 0

    # generate protobuf send to World

    def go_pickup(self, truckid, whid) -> World_UPS.UGoPickup:
        self.seqnum += 1
        Ugo_pickup = World_UPS.UGoPickup()
        Ugo_pickup.truckid = truckid
        Ugo_pickup.whid = whid
        Ugo_pickup.seqnum = self.seqnum
        return Ugo_pickup

    def gene_package(self, packageid, x, y) -> World_UPS.UDeliveryLocation:
        Upackage = World_UPS.UDeliveryLocation()
        Upackage.packageid = packageid
        Upackage.x = x
        Upackage.y = y
        return Upackage

    def go_deliver(self, truckid, packages: List[World_UPS.UDeliveryLocation]) -> World_UPS.UGoDeliver:
        self.seqnum += 1
        Ugo_deliver = World_UPS.UGoDeliver()
        Ugo_deliver.truckid = truckid
        for package in packages:
            Ugo_deliver.packages.append(package)
        Ugo_deliver.seqnum = self.seqnum
        return Ugo_deliver

    def query_truck(self, truckid) -> World_UPS.UQuery:
        self.seqnum += 1
        Uquery = World_UPS.UQuery()
        Uquery.truckid = truckid
        Uquery.seqnum = self.seqnum
        return Uquery

# generate protobuf send to Amazon
    def send_WorldId(self, worldid) -> UA.USendWorldId:
        Usend_Worldid = UA.USendWorldId()
        Usend_Worldid.worldid = worldid
        return Usend_Worldid

    def pac_pickup_res(self, tracking_id, is_binded, shipment_id, truck_id) -> UA.UPacPickupRes:
        UPac_pickup_res = UA.UPacPickupRes()
        UPac_pickup_res.tracking_id = tracking_id
        UPac_pickup_res.is_binded = is_binded
        UPac_pickup_res.shipment_id = shipment_id
        UPac_pickup_res.truck_id = truck_id
        return UPac_pickup_res
