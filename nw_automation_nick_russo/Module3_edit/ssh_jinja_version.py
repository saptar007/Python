import time
import paramiko
import yaml
import smtplib
import re
#from PyYAML import yaml
from jinja2 import Environment, FileSystemLoader
email = 'saptbane@cisco.com'

def send_email(email,host):
    smtpObj = smtplib.SMTP('outbound.cisco.com', 25)
    smtpObj.ehlo()
    smtpObj.sendmail('noreply@cisco.com',email, 'Subject:"Core Found on" + host')
    smtpObj.quit()

def send_cmd(conn, command):
    conn.send(command+ "\n")
    time.sleep(2.0)

def get_output(conn):
    return conn.recv(65535).decode("utf-8")

def is_core(output,host):
    model_regex = re.compile(r"core_(?P<file>\S+)")
    model_match = model_regex.search(output)
    if model_match:
        email_subject = "Core file "+(model_match.group("file"))+" found on "+host
        print (email_subject)
        send_email(email, host)

def main():


     #   Here we are commenting out the dictionary that was statically defined in the previous iteration
     #   host_dict = {
     #       "10.2.4.21": "Admin123",
     #       "10.2.4.23": "Admin123"
     #   }
    with open("host_yaml/host.yml", "r") as hosts:
        host_root = yaml.load(hosts, Loader=yaml.FullLoader)

    for host in host_root["host_list"]:
        #print (host)
        # paramiko can be client or server, we are using client here
        conn_param = paramiko.SSHClient()

        # We dont want paramiko to refuse connection due to missing SSH Keys
        conn_param.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        conn_param.connect (hostname=host["ip"], username="admin", password=host["passw"], look_for_keys=False, allow_agent=False)
        conn = conn_param.invoke_shell()
        time.sleep(2.0)
        #print ("test")
        send_cmd(conn, "expert")

        # testing this using only 1 command and will move to a list when testing multiple commands
        commands = [
            #"show version",
            #"expert",
            "ls /ngfw/var/common | grep core",
        ]
        for command in commands:
            #time.sleep(1.0)
            send_cmd(conn, command)
            time.sleep(1.0)
            result = (get_output(conn))
            is_core(result,host["ip"])

            # model_regex = re.compile(r"core_(?P<file>\S+)")
            # model_match = model_regex.search(result)
            # if model_match:
            #     print (model_match.group("file"))
                #break

        conn.close()

if __name__ == "__main__":
    main()