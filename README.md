# CloudCompose

**NOTE**: This is work-in-progress. Do not use just yet.

tl;dr: An automated method for deploying [Docker Compose](https://docs.docker.com/compose/).

## Requirements

 * An Ubuntu 14.04 VM
 * A `docker-compose.yml`-file available over HTTP
 * Ansible

## Installation

Install Ansible:

 * `pip install -r requirements.txt`

Configure the VM:

 * `ansible-playbook -u YourUser --diff -i inventory/foobar site.yml`
