#!/usr/bin/env python3

import argparse
import json
import subprocess

def list_hosts():
    host_info_j = subprocess.check_output(["ansible-inventory", "--list"])
    host_info = json.loads(host_info_j)

    if "target" not in host_info:
        print("No targets found")
        exit(1)
    elif "hosts" not in host_info["target"]:
        print("No hosts found in target")
        exit(1)
    else:
        for host in host_info["target"]["hosts"]:
            print(host)

def get_ssh_cmd(host):
    try:
        host_info_j = subprocess.run(["ansible-inventory", "--host", host],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        if b"Could not match supplied host pattern" in e.stderr:
            print("FAIL: ansible-inventory failed to find host:")
            print(e.stderr.decode())
        else:
            print("FAIL: ansible-inventory failed")
            print(e.stderr.decode())
        exit(1)
    host_info = json.loads(host_info_j.stdout)

    if "ansible_host" not in host_info:
        # No host address found - using hostname
        host_info["ansible_host"] = host
    elif "ansible_user" not in host_info:
        print("No user address found")
        exit(1)

    ssh_key = ""
    if "ansible_ssh_private_key_file" in host_info:
        ssh_key = "-i {}".format(host_info["ansible_ssh_private_key_file"])

    ssh_cmd = [
        "ssh",
        "{}@{}".format(host_info["ansible_user"], host_info["ansible_host"]),
        "{}".format(host_info.get("ansible_ssh_common_args", "")),
        "{}".format(ssh_key),
    ]

    print(" ".join(entry for entry in ssh_cmd if entry != ""))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Get the SSH command line for an Ansible host")
    parser.add_argument("--list", action = "store_true",
        help = "List the available hosts")
    parser.add_argument("host", default = None, nargs = "?")
    args = parser.parse_args()

    if args.list:
        list_hosts()
    elif args.host is None:
        parser.print_help()
        parser.exit(1, "Specify the host!\n")
    else:
        get_ssh_cmd(args.host)
