# Add grpc generated folder to path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "grpc_messenger"))


import grpc
import messenger_pb2
import messenger_pb2_grpc

import client as cli
import server as ser


def send_to_self(addr:list[str]) -> None:
    port = 8080
    
    # Connect to the actual gRPC server
    connections: list[cli.ServerConnection] 
    failure_addrs:list[str] 
    connections, failure_addrs = cli.connect_to_servers(addr)
    
    for addr in failure_addrs:
        print(f"Warning: Failed to connect to: {addr}")
    
    if not connections:
        print(f"CRITICAL: NO CONNECTIONS FUNCTIONAL. ABORTING TEST CONNECT AND DISPATCH")
        return
    
    # Send message
    failed_recvs = cli.send_messages(
        id=101, 
        connections=connections, 
        dest_message="Hello from gRPC skeleton!",
        dest_ip="example@gmail.com",
        dest_port=port
    )
    
    for addr in failure_addrs:
        print(f"Failure when sending to: {addr}")
    
    inbox_list_per_server:list[tuple[messenger_pb2.InboxResponse, str]]
    failed_recvs:list[str]
    inbox_list_per_server, failed_recvs = cli.receive_all_messages(
        connections=connections, 
        self_ip="example@gmail.com",
        self_port=port
    )
    
    for addr in failed_recvs:
        print(f"Failure when receiving from: {addr}")
        
    for inbox_ip in inbox_list_per_server:
        inbox, ip = inbox_ip
        messages = cli.read_inbox_response(inbox)
        
        for msg in messages:
            id, port, port, message = msg
            print(f"server{ip}: [message: {message} received from user {ip}:{port}]")

if __name__ == '__main__':
    send_to_self(["localhost:50051"])
    
    