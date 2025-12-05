# Add grpc generated folder to path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "grpc_messenger"))



import grpc
from concurrent import futures
import messenger_pb2
import messenger_pb2_grpc
from collections import defaultdict
import argparse

const_max_workers = 10

class MessengerService(messenger_pb2_grpc.MessengerServiceServicer):
    def __init__(self):
        # simple in-memory storage: key="ip:port", value=[list of messages]
        self.mailboxes = defaultdict(list)

    def Send(self, request, context):
        # Create a unique key for the recipient
        recipient_id = f"{request.sendip}:{request.sendport}"
        
        # Store the message in the recipient's mailbox
        # In a real app, you'd persist this to a database
        self.mailboxes[recipient_id].append(request)
        
        print(f"sent: {request}")
        return messenger_pb2.SendResponse(success=True, message="Message queued.")

    def ReceiveAll(self, request, context):
        requester_id = f"{request.selfip}:{request.selfport}"
        messages = self.mailboxes.get(requester_id, [])
        
        print(f"sent: {messages}")
        # Pop list from dictionary table
        if requester_id in self.mailboxes:
            del self.mailboxes[requester_id]
            
        return messenger_pb2.InboxResponse(messages=messages)



def serve_syncronous_server(ip:str, port:int):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=const_max_workers))
    messenger_pb2_grpc.add_MessengerServiceServicer_to_server(MessengerService(), server)
    
    bind_address = f'{ip}:{port}'
    server.add_insecure_port(bind_address)
    print(f"Server started. Listening on {bind_address} ...")
    
    server.start()
    server.wait_for_termination() #Completely blocking



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
    