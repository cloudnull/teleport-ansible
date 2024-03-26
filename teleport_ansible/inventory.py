#!/usr/bin/env python3
#
#   Copyright Cloudnull <kevin@cloudnull.com>. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import json
import subprocess


INVENTORY = {
    "_meta": {"hostvars": {}},
    "all": {
        "hosts": [],
        "children": [],
    },
}


def _group_add(group_name, hostname):
    """Set group information for a given name and host.

    :param group_name: String
    :param hostname: String
    """
    try:
        group = INVENTORY[group_name]
    except KeyError:
        # Per ansible spec, group names can not have dashes in them.
        group_name = group_name.replace("-", "_")
        # Per ansible spec, group names can not have periods in them.
        group_name = group_name.replace(".", "_")
        # Per ansible spec, group names can not start with an int.
        try:
            int(group_name[0])
        except ValueError:
            pass
        else:
            return

        INVENTORY.setdefault(group_name, {"hosts": [], "children": []})
        group = INVENTORY[group_name]

    group["hosts"].append(hostname)
    group["hosts"] = sorted(set(group["hosts"]))


def main():
    """Return dynamic inventory using teleport data.

    :returns: String
    """
    # Presently using subprocess to get the node JSON, may revise this later.
    tsh_return = subprocess.run(
        "tsh ls --format=json", shell=True, capture_output=True
    )

    try:
        teleport_items = json.loads(tsh_return.stdout)
    except Exception:
        raise SystemExit("No inventory JSON data found. Check login via tsh.")
    else:
        if not teleport_items:
            raise SystemExit("Nothing available via teleport, check login via tsh.")


    # Run the tsh status command and capture the output
    tsh_status_output = subprocess.run(["tsh", "status", "--format=json"], capture_output=True, text=True)

    # Check if the command was successful
    if tsh_status_output.returncode == 0:
        try:
            # Parse the JSON data
            status_data = json.loads(tsh_status_output.stdout)

            # Extract the value of the "cluster" key from the "active" section
            cluster_value = status_data.get("active", {}).get("cluster")

     #       if cluster_value:
     #           print("Cluster Value:", cluster_value)
     #       else:
     #           print("No 'cluster' key found in the 'active' section of the tsh status output.")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
    else:
        print(f"Error running 'tsh status' command. Return code: {tsh_status_output.returncode}")

    for item in teleport_items:
        if item["kind"] != "node":
            continue

        node = item
        #hostname = node["metadata"]["name"]
        hostname = node["spec"]["hostname"]

        #_group_add(group_name=node["cluster"], hostname=hostname)
        _group_add(group_name=cluster_value, hostname=hostname)

        meta_data = INVENTORY["_meta"]["hostvars"]
        all_data = INVENTORY["all"]
        all_data["hosts"].append(hostname)
        all_data["hosts"] = sorted(set(all_data["hosts"]))

        for k, v in node["metadata"]["labels"].items():
            try:
                host_vars = meta_data[hostname]
            except KeyError:
                host_vars = meta_data[hostname] = dict()

            host_vars[k] = v
            host_vars["teleport_id"] = node["metadata"]["id"]

            # If a label is an ansible variable, omit it from groups
            if k.startswith("ansible_"):
                continue

            _group_add(group_name=v, hostname=hostname)

    print(json.dumps(INVENTORY, indent=4))


if __name__ == "__main__":
    main()
