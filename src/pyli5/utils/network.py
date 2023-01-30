import socket

def get_free_tcp_port()->int:
    """
    Starts a socket connection to grab a free port (Involves a race
        condition but will do for now)
    :return: An open port in the system
    """
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', 0))
    _, port = tcp.getsockname()
    tcp.close()
    return port 

