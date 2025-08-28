Simple python code to receive a message from Meshcom and send it to Meshtastic<br>
<br>
This is an one-way bridge: MeshCom -> Meshtastic<br> 
<br>
How it works:<br>
- Receives JSON frames from MeshCom via UDP (port 1799).<br>
- Checks that the "src", "dst", and "msg" fields are present.<br>
- Only accepts frames with "dst" equal to MESHCOM_BRIDGE_NODE.<br>
- If msg begins with "!", it is sent as the destination to the Meshtastic node.<br>
- Otherwise, it is sent as a broadcast message to the set channel.<br>
- Sending to Meshtastic occurs via TCP (port 4403).<br>
<br>
Edit the code in the configuration section. You must specify the IP address of the Meshcom LoRa system on which to listen for incoming messages (the standard port is 1799/UDP). Enter the callsign of the node we will use as our bridge (incoming node): messages addressed to this Meshcom node will be forwarded to the Meshtastic network. Specify the IP address of the Meshtastic node we will use as the "outgoing" node (the standard port is 4403/TCP). If we operate outside the LAN, it will be necessary to intervene on the NAT configurations of the routers where the LoRa cards work. If you intend to broadcast messages, make sure the correct channel is specified. Avoid broadcasting and creating unnecessary traffic on shared and primary channels; it's best to create a dedicated channel. Nothing else needs to be changed in the code. In the Meshcom/bridge node, enable extudp and specify the IP address of the computer where the bridge software is running.
<br><br>
A message sent from the Meshcom network to the bridge and starting with ! (e.g. !a45c0af2 hello) will be forwarded to the indicated Meshtastic node, if it does not start with ! the message will be sent to the channel (as configured inside the code -- and in the LoRa Meshtastic card that we use in output --).<br>
<br>
