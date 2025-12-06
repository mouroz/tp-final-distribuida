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

import messenger_pb2

def extract_receive_all_response(
        response: messenger_pb2.InboxResponse
    ) -> list[tuple[int, str, str, str]]:
    
    output_list = []
    
    # 1. Access the repeated field by its name in the .proto ('messages')
    # This acts strictly like a Python list
    for msg in response.messages:
        
        # 2. 'msg' is now a single SendRequest object.
        # Access its fields directly using dot notation.
        # (Replace these attribute names with the actual ones from your .proto)
        msg_id = msg.id          # int
        sender = msg.msg      # str
        recipient = msg.self_email # str
        body = msg.dest_email          # str
        
        # 3. Create the tuple and append
        output_list.append((msg_id, sender, recipient, body))

    return output_list





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
    ) ->list[messenger_pb2.InboxResponse | None]:
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
            inboxes.append(inbox)   
            

        except grpc.RpcError as e:
            inboxes.append(None)
            print(e)
            
    return inboxes

def extract_receive_all_unique_responses(
        inbox_list: list[messenger_pb2.InboxResponse | None]
    ) -> list[tuple[int, str, str, str]]:
    """Function that merges multiple inbox responses, removing duplicates based on message ID. Assumes each inbox is sorted by ID.
    Args:
        inbox_list (list[tuple[messenger_pb2.InboxResponse, str]]): List of tuples containing inbox response and server IP
    Returns:
        list[tuple[int, str, str, str]]: id, msg, self_email, dest_email    
    """
    results = []
    responses = []
    counters = [0] * len(inbox_list)

    # Extract messages from each inbox response
    for i, inbox in enumerate(inbox_list):
        response = extract_receive_all_response(inbox)
        if response is None:
            response = []
        responses.append(response)
        counters[i] = 0
    
    # Merge responses while removing duplicates based on message ID
    all_read_messages = False
    while not all_read_messages:
        ids = [0] * len(responses)
        min_id = (sys.maxsize, -1)  # (id, index)
        
        # Find minimum ID among current positions
        for i in range(len(responses)):
            if counters[i] < len(responses[i]):
                current_id = responses[i][counters[i]][0]
                ids[i] = current_id
                if current_id < min_id[0]:
                    min_id = (current_id, i)
        
        # If no more messages to read
        if min_id[1] == -1:
            all_read_messages = True
        else:
            # Add the message with minimum ID
            results.append(responses[min_id[1]][counters[min_id[1]]])
            
            # Advance all counters that have this same ID and sender address (remove duplicates)
            minID_sender_addrs = responses[min_id[1]][counters[min_id[1]]][1]
            for i in range(len(responses)):
                I_sender_addrs = responses[i][counters[i]][1]
                if counters[i] < len(responses[i]) and ids[i] == min_id[0] and I_sender_addrs == minID_sender_addrs:
                    counters[i] += 1

    return results


    



    