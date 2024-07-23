from scapy.all import ARP, Ether, srp, get_if_addr

def scan_network(manufacturer):
    # Get the IP address of the network interface
    ip_address = get_if_addr()

    # Create an ARP request packet
    arp_request = ARP(pdst=f"{ip_address}/24")
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp_request

    # Send the packet and capture the response
    result = srp(packet, timeout=3, verbose=0)[0]

    # Extract the MAC addresses of devices with the specified manufacturer
    devices = []
    for sent, received in result:
        if received.haslayer(ARP) and received[ARP].op == 2:
            if manufacturer in received[ARP].hwsrc:
                devices.append({'IP': received[ARP].psrc, 'MAC': received[ARP].hwsrc})

    return devices

# Specify the manufacturer to search for
manufacturer = "Trust International B.V."

# Scan the network for devices with the specified manufacturer
devices = scan_network(manufacturer)

# Print the results
for device in devices:
    print(f"Device IP: {device['IP']}, MAC Address: {device['MAC']}")