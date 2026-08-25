# Met un await pour attendre la connexion à la base de données SQL, ne lance pas le docker sans la db
import socket
import sys
import time

host = sys.argv[1]
port = 3306

while True:
    try:
        with socket.create_connection((host, port), timeout=1):
            break
    except OSError:
        print("Waiting for database...")
        time.sleep(1)

import subprocess
subprocess.run(sys.argv[2:])
