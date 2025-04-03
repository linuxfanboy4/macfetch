import platform
import psutil
import socket
import os
import cpuinfo
import gpuinfo
import uuid
import time
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress
from datetime import datetime

console = Console()

def get_system_info():
    system_info = {}
    system_info['OS'] = platform.system()
    system_info['OS Version'] = platform.version()
    system_info['Architecture'] = platform.architecture()[0]
    system_info['Machine'] = platform.machine()
    system_info['Processor'] = platform.processor()
    system_info['CPU Cores'] = psutil.cpu_count(logical=False)
    system_info['Logical CPUs'] = psutil.cpu_count(logical=True)
    system_info['Memory'] = psutil.virtual_memory().total / (1024 ** 3)
    system_info['Swap Memory'] = psutil.swap_memory().total / (1024 ** 3)
    system_info['Hostname'] = socket.gethostname()
    system_info['IP Address'] = socket.gethostbyname(system_info['Hostname'])
    system_info['MAC Address'] = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2*6, 2)][::-1])
    return system_info

def get_gpu_info():
    try:
        gpus = gpuinfo.get_info()
        return gpus
    except Exception as e:
        return str(e)

def get_cpu_info():
    cpu_info = cpuinfo.get_cpu_info()
    return cpu_info.get('cpu', 'N/A')

def get_battery_info():
    try:
        battery = psutil.sensors_battery()
        if battery:
            return battery.percent, battery.secsleft
        else:
            return 'No Battery Info', ''
    except Exception:
        return 'No Battery Info', ''

def get_disk_info():
    partitions = psutil.disk_partitions()
    disk_info = {}
    for partition in partitions:
        usage = psutil.disk_usage(partition.mountpoint)
        disk_info[partition.device] = {
            'Total': usage.total / (1024 ** 3),
            'Used': usage.used / (1024 ** 3),
            'Free': usage.free / (1024 ** 3),
            'Percentage': usage.percent
        }
    return disk_info

def get_network_info():
    network_info = psutil.net_if_addrs()
    network_data = {}
    for interface, addrs in network_info.items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                network_data[interface] = addr.address
    return network_data

def display_system_info(system_info):
    table = Table(title="System Information", style="bold white")
    for key, value in system_info.items():
        table.add_row(key, str(value))
    console.print(Panel(table, title="System Overview", style="bold cyan"))

def display_gpu_info(gpus):
    if isinstance(gpus, str):
        console.print(Panel(Text(gpus, style="bold red"), title="GPU Info", style="bold red"))
    else:
        table = Table(title="GPU Information", style="bold green")
        for gpu in gpus:
            table.add_row(gpu['name'], gpu['driver'], gpu['memory'], gpu['utilization'])
        console.print(Panel(table, title="GPU Overview", style="bold green"))

def display_cpu_info(cpu_info):
    table = Table(title="CPU Information", style="bold magenta")
    table.add_row('CPU Model', cpu_info)
    console.print(Panel(table, title="CPU Overview", style="bold magenta"))

def display_battery_info(battery_info):
    if isinstance(battery_info, tuple) and len(battery_info) > 1:
        table = Table(title="Battery Information", style="bold red")
        table.add_row('Battery Percentage', f"{battery_info[0]}%")
        table.add_row('Time Remaining', f"{battery_info[1]} seconds")
        console.print(Panel(table, title="Battery Status", style="bold red"))
    else:
        console.print(Panel(Text(battery_info, style="bold red"), title="Battery Info", style="bold red"))

def display_disk_info(disk_info):
    table = Table(title="Disk Information", style="bold cyan")
    for device, usage in disk_info.items():
        table.add_row(device, f"{usage['Total']} GB", f"{usage['Used']} GB", f"{usage['Free']} GB", f"{usage['Percentage']}%")
    console.print(Panel(table, title="Disk Usage", style="bold cyan"))

def display_network_info(network_info):
    table = Table(title="Network Interfaces", style="bold yellow")
    for interface, ip in network_info.items():
        table.add_row(interface, ip)
    console.print(Panel(table, title="Network Interfaces", style="bold yellow"))

def display_progress_bar():
    progress = Progress("[progress.description]{task.description}", "[progress.percentage]{task.percentage:>3}%", "{task.completed}/{task.total}")
    task = progress.add_task("Collecting system information...", total=5)

    with progress:
        for _ in range(5):
            time.sleep(0.5)
            progress.update(task, advance=1)

def main():
    display_progress_bar()
    system_info = get_system_info()
    gpu_info = get_gpu_info()
    cpu_info = get_cpu_info()
    battery_info = get_battery_info()
    disk_info = get_disk_info()
    network_info = get_network_info()

    console.print(Panel(Text(f"System Overview as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style="bold blue"), style="bold blue"))
    display_system_info(system_info)
    display_gpu_info(gpu_info)
    display_cpu_info(cpu_info)
    display_battery_info(battery_info)
    display_disk_info(disk_info)
    display_network_info(network_info)

if __name__ == "__main__":
    main()
