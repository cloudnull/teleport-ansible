#   Copyright Peznauts <kevin@cloudnull.com>. All Rights Reserved.
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

import setuptools

from teleport_ansible import meta


with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()


REQUIREMENTS = {}


setuptools.setup(
    name="teleport-ansible",
    author=meta.__author__,
    author_email=meta.__email__,
    description=("Teleport driven ansible inventory script."),
    version=meta.__version__,
    packages=["teleport_ansible"],
    include_package_data=True,
    zip_safe=False,
    test_suite="tests",
    install_requires=list(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cloudnull/teleport-ansible",
    project_urls={
        "Bug Tracker": "https://github.com/cloudnull/teleport-ansible/issues",
    },
    python_requires=">=3.6",
    extras_require=dict(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points={
        "console_scripts": [
            "teleport-ansible = teleport_ansible.inventory:main",
        ],
    },
)
