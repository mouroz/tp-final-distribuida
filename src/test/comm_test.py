# Add grpc generated folder to path
import sys
import os
import grpc


current_test_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_test_dir)
comm_dir = os.path.join(src_dir, "comm")
generated_code_dir = os.path.join(comm_dir, "grpc_messenger")

# Ensure the imports are based on the location of the py file
if comm_dir not in sys.path:
    sys.path.insert(0, comm_dir)
if generated_code_dir not in sys.path:
    sys.path.insert(0, generated_code_dir)

try:
    import client as cli
    import server as ser
    import messenger_pb2
    import messenger_pb2_grpc
except ImportError as e:
    print(f"Import Error: {e}")
    print(f"Debug: sys.path is currently: {sys.path}")
    sys.exit(1)
    



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
        self_email="example@gmail.com",
        dest_email="example@gmail.com"
    )
    
    failed_recvs = cli.send_messages(
        id=102, 
        connections=connections, 
        dest_message="Hello from gRPC!! skeleton!",
        self_email="example@gmail.com",
        dest_email="example@gmail.com"
    )

    for addr in failure_addrs:
        print(f"Failure when sending to: {addr}")
        

           
    # Receive all messages
    inbox_list_per_server:list[messenger_pb2.InboxResponse | None]
    inbox_list_per_server = cli.receive_all_messages(
        connections=connections,
        self_email="example@gmail.com",
    )

    # Old code for printing per server inboxes

    print("----- INBOXES PER SERVER -----")
    for i, inbox in enumerate(inbox_list_per_server):
        addr = connections[i].address
        if inbox is None:
            print(f"Failure when receiving from: {addr}")
            continue
        
        print(type(inbox))
        messages = cli.extract_receive_all_response(inbox)
        
        for message in messages:
            id, msg, self_email, dest_email = message
            print(f"server{addr}: [id: {id}, message: {msg}, received from: {self_email}]")

    print("----- UNIQUE MESSAGES ACROSS ALL SERVERS -----")

    # New code for printing unique messages across all servers
    unique_messages = cli.extract_receive_all_unique_responses(inbox_list_per_server)

    for message in unique_messages:
        id, msg, self_email, dest_email = message
        print(f"[id: {id}, message: {msg}, received from: {self_email}]")

if __name__ == '__main__':
    send_to_self(["localhost:50051", "localhost:50052", "localhost:50053"])
    
    