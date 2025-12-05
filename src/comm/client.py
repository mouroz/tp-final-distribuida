# Add grpc generated folder to path
import sys
import os
import grpc
from dataclasses import dataclass




sys.path.append(os.path.join(os.path.dirname(__file__), "grpc_messenger"))
try: 
    import messenger_pb2
    import messenger_pb2_grpc
except ImportError as e:
    print(f"Import Error: {e}")
    print(f"Debug: sys.path is currently: {sys.path}")
    sys.exit(1)





@dataclass
class ServerConnection:
    address: str
    channel: grpc.Channel
    stub: messenger_pb2_grpc.MessengerServiceStub
    
            
MAX_HANDSHAKE_TIMEOUT = 2  # seconds


def extract_send_response(
        response:messenger_pb2.SendResponse
    ) -> tuple[bool, str]:
    return response.success, response.debug_message

def extract_receive_all_response(
        inbox: messenger_pb2.InboxResponse
    ) -> list[tuple[int, str, str, str]]:
    """_summary_

    Args:
        inbox (messenger_pb2.InboxResponse): _description_

    Returns:
        list[tuple[int, str, int, str]]: id, msg, self_email, dest_email    
    """
    
    results = []
    for msg_obj in inbox.messages:
        
        entry = (
            msg_obj.id,
            msg_obj.msg,
            msg_obj.self_email,
            msg_obj.dest_email
        )
        
        results.append(entry)
        
    return results






def connect_to_servers(server_addresses: list[str]) -> tuple[list[ServerConnection], list[str]]:
    """ 
        Attempts to connect to a list of server addresses.
        Returns a tuple containing a list of successful connections and a list of failed addresses.
    """
    
    connections = []
    failed_connections = []
    
    for addr in server_addresses:
        channel = grpc.insecure_channel(addr)
        try:
            # Force handshake to ensure its connectable
            grpc.channel_ready_future(channel).result(timeout=MAX_HANDSHAKE_TIMEOUT)
            stub = messenger_pb2_grpc.MessengerServiceStub(channel)
            connections.append(ServerConnection(address=addr, channel=channel, stub=stub))
            
        except grpc.FutureTimeoutError:
            failed_connections.append(addr)
            channel.close()
            
    return connections, failed_connections


 
def send_messages(
        id: int, connections: list[ServerConnection], 
        dest_message: str, self_email:str, dest_email: str
    ) -> list[str]:
    """
        Send message to all connected servers
        dest_message and dest_port simulates the logical addressing of the recipient.
        In a real-world app, these would correspond to actual user identifiers.
    """
    
    
    send_payload = messenger_pb2.SendRequest(
        id=id,
        msg=dest_message,
        self_email=self_email,
        dest_email=dest_email
    )
    
    failure_servers = []
    for conn in connections:
        try:
            #message and status, which is always positive currently
            response = conn.stub.Send(send_payload, timeout=2)
            
        except grpc.RpcError as e:
            failure_servers.append(conn.address)
           
    
    return failure_servers



# Warning: This is an extremly naive implementation for demo purposes only.
# All messages are being returned: handling duplicates is done at a higher layer.
def receive_all_messages(
        connections: list[ServerConnection], self_email:str,
    ) -> tuple[list[tuple[messenger_pb2.InboxResponse, str]], list[str]]:
    """
        Retrieve all messages from all connected servers.
        
        self_ip and self_port simulates the logical addressing of the client.
        In a real-world app, these would correspond to actual user identifiers.
    """

    receive_payload = messenger_pb2.ReceiveRequest(self_email=self_email)

    failure_servers = []
    inboxes = []
    for conn in connections:
        try:
            inbox = conn.stub.ReceiveAll(receive_payload, timeout=2)
            inboxes.append([inbox, conn.address])   
            

        except grpc.RpcError as e:
            failure_servers.append(conn.address)
            print(e)
            
    return inboxes, failure_servers



    



    