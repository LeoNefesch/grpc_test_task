import grpc
import time
from protobuf.timestamp_pb2 import Timestamp
import grpc_test_pb2
import grpc_test_pb2_grpc
import json


def load_config(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config

config = load_config('config.json')
TOTAL_PACKETS = config['TotalPackets']
RECORDS_IN_PACKET = config['RecordsInPacket']
TIME_INTERVAL = config['TimeInterval']
gRPC_SERVER_ADDR = config['gRPCServerAddr']
gRPC_SERVER_PORT = config['gRPCServerPort']


def send_packets(stub):
    for packet_seq_num in range(1, TOTAL_PACKETS + 1):
        packet = grpc_test_pb2.Packet()
        packet.packet_timestamp.GetCurrentTime()
        packet.packet_seq_num = packet_seq_num
        packet.n_records = RECORDS_IN_PACKET

        for _ in range(RECORDS_IN_PACKET):
            data = grpc_test_pb2.Data()
            data.decimal1 = 1.1  # Здесь можно вставить ваши данные
            data.decimal2 = 2.2
            data.decimal3 = 3.3
            data.decimal4 = 4.4
            record_timestamp = Timestamp()
            record_timestamp.GetCurrentTime()
            data.timestamp.CopyFrom(record_timestamp)
            packet.packet_data.append(data)
        response = stub.SendPacket(packet)
        time.sleep(TIME_INTERVAL)


def run():
    with grpc.insecure_channel(f'{gRPC_SERVER_ADDR}:{gRPC_SERVER_PORT}') as channel:
        stub = grpc_test_pb2_grpc.RecommendationsServiceStub(channel)
        send_packets(stub)


if __name__ == '__main__':
    run()
