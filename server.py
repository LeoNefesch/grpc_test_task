import grpc
from concurrent import futures
import psycopg2
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
PG_USER = config['pg_user']
PG_PASSWORD = config['pg_password']
PG_HOST = config['pg_host']
PG_DATABASE = config['pg_database']
PG_PORT = config['pg_port']
GRPC_PORT = config['gRPCServerPort']


class RecommendationsService(grpc_test_pb2_grpc.RecommendationsServiceServicer):
    def SendPacket(self, request, context):
        conn = psycopg2.connect(database=PG_DATABASE,
                                user=PG_USER,
                                password=PG_PASSWORD,
                                host=PG_HOST,
                                port=PG_PORT)
        cursor = conn.cursor()

        for record_seq_num, data in enumerate(request.packet_data, start=1):
            cursor.execute("""INSERT INTO grpc_data (PacketSeqNum, RecordSeqNum, PacketTimestamp, Decimal1, Decimal2,
                              Decimal3, Decimal4, RecordTimestamp)
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (request.packet_seq_num,
                 record_seq_num,
                 request.packet_timestamp.ToDatetime(),
                 data.decimal1,
                 data.decimal2,
                 data.decimal3,
                 data.decimal4,
                 data.timestamp.ToDatetime()))
        conn.commit()
        cursor.close()
        conn.close()
        return grpc_test_pb2.Response(message="Data saved successfully.")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpc_test_pb2_grpc.add_RecommendationsServiceServicer_to_server(RecommendationsService(), server)
    server.add_insecure_port('[::]:GRPC_PORT')
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
