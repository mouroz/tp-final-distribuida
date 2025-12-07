# Add grpc generated folder to path
import sys
import os

import grpc
from concurrent import futures
from collections import defaultdict
import argparse


sys.path.append(os.path.join(os.path.dirname(__file__), "grpc_messenger"))
try: 
    import messenger_pb2
    import messenger_pb2_grpc
except ImportError as e:
    print(f"Import Error: {e}")
    print(f"Debug: sys.path is currently: {sys.path}")
    sys.exit(1)
    
    

import logging
logging.basicConfig(level=logging.INFO)


const_max_workers = 10

def extract_receive_request(request:messenger_pb2.ReceiveRequest) -> str:
    return request.self_email

def extract_send_request(
        request:messenger_pb2.SendRequest
    ) -> tuple[int, str, str, str]:
    return request.id, request.msg, request.self_email, request.dest_email
    
    
class MessengerService(messenger_pb2_grpc.MessengerServiceServicer):
    def __init__(self):
        # Simple in-memory storage: key="ip:port", value=[list of messages]
        self.mailboxes = defaultdict(list)

    def Send(self, request, context):
        id, msg, self_email, dest_email = extract_send_request(request)
        recipient_id = dest_email
        
        # Persist to a database in real application
        self.mailboxes[recipient_id].append(request)
        
        print(f"Received from: {self_email}, to: {dest_email}, msg: {request}")
        return messenger_pb2.SendResponse(
            success=True, debug_message="Message queued."
        )

    def ReceiveAll(self, request, context):
        self_email = extract_receive_request(request)
        messages = self.mailboxes.get(self_email, [])
        
        print(f"Sent: {messages}")
        # Pop list from dictionary table
        if self_email in self.mailboxes:
            del self.mailboxes[self_email]
            
        return messenger_pb2.InboxResponse(messages=messages)



def serve_syncronous_server(ip:str, port:int):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=const_max_workers))
    messenger_pb2_grpc.add_MessengerServiceServicer_to_server(MessengerService(), server)
    
    # IPv6 addresses need brackets, e.g. [::]:50051 or [2804:14c:...]:50051
    if ':' in ip and not ip.startswith('['):
        bind_address = f'[{ip}]:{port}'
    else:
        bind_address = f'{ip}:{port}'
    
    server.add_insecure_port(bind_address)
    print(f"Server started. Listening on {bind_address} ...")
    
    server.start()
    
    try:
        server.wait_for_termination() #Completely blocking
    except KeyboardInterrupt:
        print("Terminated")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the gRPC Messenger Server.")
    
    # Add arguments for IP and Port
    parser.add_argument(
        "--ip", 
        type=str, 
        default="[::]", 
        help="The IP address to bind to (default: [::] for all interfaces)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=50051, 
        help="The port to listen on (default: 50051)"
    )
    
    args = parser.parse_args()
    srv = serve_syncronous_server(args.ip, args.port)
    