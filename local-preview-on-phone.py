#!/usr/bin/env python3
from __future__ import annotations

from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import socket
import os

PORT = 8000
ROOT = Path(__file__).resolve().parent


def local_ips() -> list[str]:
    found = []
    try:
        hostname = socket.gethostname()
        for info in socket.getaddrinfo(hostname, None, family=socket.AF_INET):
            ip = info[4][0]
            if ip.startswith('127.'):
                continue
            if ip not in found:
                found.append(ip)
    except OSError:
        pass
    # UDP trick to discover the primary outbound interface without sending traffic
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            if not ip.startswith('127.') and ip not in found:
                found.insert(0, ip)
    except OSError:
        pass
    return found


def main() -> None:
    os.chdir(ROOT)
    server = ThreadingHTTPServer(("0.0.0.0", PORT), SimpleHTTPRequestHandler)
    print("\nThe Press preview server is running.\n")
    print(f"Open on this computer: http://localhost:{PORT}/index.html")
    ips = local_ips()
    if ips:
        print("\nTry one of these on your phone while both devices are on the same Wi-Fi:\n")
        for ip in ips:
            print(f"  http://{ip}:{PORT}/index.html")
    else:
        print("\nI couldn't detect a local network IP automatically.")
        print("Use your computer's local IP address with port 8000.")
    print("\nPress Ctrl+C to stop the preview server.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping preview server.")


if __name__ == "__main__":
    main()
