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
        "tsh ls --all --format=json", shell=True, capture_output=True
    )
    try:
        teleport_items = json.loads(tsh_return.stdout)
    except Exception:
        raise SystemExit("No inventory JSON data found. Check login via tsh.")
    else:
        if not teleport_items:
            raise SystemExit(
                "Nothing available via teleport, check login via tsh."
            )

    for item in teleport_items:
        node = item["node"]
        if node["kind"] != "node":
            continue

        hostname = node["spec"]["hostname"]

        _group_add(group_name=item["cluster"], hostname=hostname)

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
