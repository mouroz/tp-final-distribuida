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





def format_address_for_grpc(addr: str) -> str:
    """Format address for gRPC - IPv6 addresses need brackets around the IP part."""
    # If already has brackets or no colons (IPv4/hostname), return as-is
    if '[' in addr or addr.count(':') <= 1:
        return addr
    
    # IPv6 address without brackets - split IP and port, add brackets
    # Format: 2804:14c:...:1dfa:50051 -> [2804:14c:...:1dfa]:50051
    last_colon = addr.rfind(':')
    ip_part = addr[:last_colon]
    port_part = addr[last_colon+1:]
    return f'[{ip_part}]:{port_part}'


def connect_to_servers(server_addresses: list[str]) -> tuple[list[ServerConnection], list[str]]:
    """ 
        Attempts to connect to a list of server addresses.
        Returns a tuple containing a list of successful connections and a list of failed addresses.
    """
    
    connections = []
    failed_connections = []
    
    for addr in server_addresses:
        formatted_addr = format_address_for_grpc(addr)
        channel = grpc.insecure_channel(formatted_addr)
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
        inbox_list: List of inbox responses (or None for failed servers)
    Returns:
        list[tuple[int, str, str, str]]: id, msg, self_email, dest_email    
    """
    unique_messages = []  # antes: results
    messages_per_server = []  # antes: server
    read_positions = [0] * len(inbox_list)  # antes: counters

    # Extract messages from each inbox response
    for server_index, inbox in enumerate(inbox_list):
        extracted_messages = extract_receive_all_response(inbox)
        if extracted_messages is None:
            extracted_messages = []
        messages_per_server.append(extracted_messages)
        read_positions[server_index] = 0
    
    # Merge servers while removing duplicates based on message ID
    all_messages_processed = False  # antes: all_read_messages
    while not all_messages_processed:
        current_ids = [0] * len(messages_per_server)  # antes: ids
        lowest_id_info = (sys.maxsize, -1)  # (message_id, server_index) - antes: min_id
        
        # Find minimum ID among current positions
        for server_index in range(len(messages_per_server)):
            if read_positions[server_index] < len(messages_per_server[server_index]):
                current_message_id = messages_per_server[server_index][read_positions[server_index]][0]
                current_ids[server_index] = current_message_id
                if current_message_id < lowest_id_info[0]:
                    lowest_id_info = (current_message_id, server_index)
        
        # If no more messages to read
        if lowest_id_info[1] == -1:
            all_messages_processed = True
        else:
            # Add the message with minimum ID
            is_duplicate = False  # antes: repeatedMessage
            server_with_lowest_id = lowest_id_info[1]  # para clareza
            
            for result_index in range(len(unique_messages)):
                current_result = unique_messages[result_index]
                candidate_message = messages_per_server[server_with_lowest_id][read_positions[server_with_lowest_id]]
                
                # Check if same ID and same sender (msg field is the sender)
                if current_result[0] == candidate_message[0] and current_result[1] == candidate_message[1]:
                    is_duplicate = True
                    break
                    
            if not is_duplicate:
                unique_messages.append(messages_per_server[server_with_lowest_id][read_positions[server_with_lowest_id]])
            
            # Advance all counters that have this same ID and sender address (remove duplicates)
            lowest_message_sender = messages_per_server[server_with_lowest_id][read_positions[server_with_lowest_id]][1]
            
            for server_index in range(len(messages_per_server)):
                if read_positions[server_index] < len(messages_per_server[server_index]):
                    current_message_sender = messages_per_server[server_index][read_positions[server_index]][1]
                    has_same_id = current_ids[server_index] == lowest_id_info[0]
                    has_same_sender = current_message_sender == lowest_message_sender
                    
                    if has_same_id and has_same_sender:
                        read_positions[server_index] += 1

    return unique_messages


    



    