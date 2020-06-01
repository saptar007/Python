import time
import paramiko
import yaml
#from PyYAML import yaml
from jinja2 import Environment, FileSystemLoader

def send_cmd(conn, command):
    conn.send(command+ "\n")
    time.sleep(2.0)

def get_output(conn):
    return conn.recv(65535).decode("utf-8")

def main():


     #   Here we are commenting out the dictionary that was statically defined in the previous iteration
     #   host_dict = {
     #       "10.2.4.21": "Admin123",
     #       "10.2.4.23": "Admin123"
     #   }
    with open("host_yaml/host.yml", "r") as hosts:
        host_root = yaml.load(hosts)

    for host in host_root["host_list"]:
        print (host)
        # paramiko can be client or server, we are using client here
        conn_param = paramiko.SSHClient()

        # We dont want paramiko to refuse connection due to missing SSH Keys
        conn_param.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        conn_param.connect (hostname=host["ip"], username="admin", password=host["passw"], look_for_keys=False, allow_agent=False)
        conn = conn_param.invoke_shell()
        time.sleep(2.0)
        #print ("test")

        # testing this using only 1 command and will move to a list when testing multiple commands
        commands = [
            #"show version",
            "expert",
            "ls /ngfw/var/common",
        ]
        for command in commands:
            #time.sleep(1.0)
            send_cmd(conn, command)
            time.sleep(1.0)
            print(get_output(conn))

        conn.close()

if __name__ == "__main__":
    main()