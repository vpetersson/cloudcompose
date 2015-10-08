# CloudCompose

tl;dr: An automated method for deploying [Docker Compose](https://docs.docker.com/compose/) for [Cloud.net](http://cloud.net) by [OnApp](https://onapp.com/).

## Requirements

 * An Ubuntu 14.04 VM
 * A `docker-compose.yml`-file available over HTTP
 * Ansible

## Installation

Install Ansible:

`$ pip install -r requirements.txt`

Configure the VM:

`$ ansible-playbook -u YourUser --diff -i inventory/foobar site.yml`

A more realistic usage would be something like this:

 ```
  $ ansible-playbook \
    -u YourUser \
    -e project=cloudnet \
    -e base_url=http://viktopia.io/cloudnet \
    -i inventory/myservers \
    --diff \
    site.yml
 ```

The inventory file (`inventory/myservers` above )is a regular [Ansible Inventory](https://docs.ansible.com/ansible/intro_inventory.html) and can look something like this:

```
[compose]
compose0 ansible_ssh_host=1.1.1.1
compose1 ansible_ssh_host=2.2.2.2
```

You can also configure the variables directly in this file to avoid having to specify them at runtime:

```
[compose]
compose0 ansible_ssh_host=1.1.1.1
compose1 ansible_ssh_host=2.2.2.2

[compose:vars]
project=cloudnet
base_url=http://viktopia.io/cloudnet
```

## Usage

The real magic in this application is done by [`cloudcompose.py`](https://github.com/vpetersson/cloudcompose/blob/master/roles/cloudcompose/files/cloudcompose.py). Beyond being a wrapper for `docker-compose` (which you can also use), `cloudcompose.py` is used to actually invoke a Docker Compose setup on first launch.

Here's how CloudCompose works:

 * When deploying CloudCompose to the server using Ansible, you provide a variables called `base_url`. CloudCompose will use this to look for a Docker Compose file. The first URL CloudCompose will try is `http://$base_url/$IP` (where $IP is the IP of `eth0`). If this fails, CloudCompose will default to `http://$base_url/docker-compose.yml`.
 * Once the file has been fetched, CloudCompose will then call on `docker-compose` to invoke the Docker containers described in the file.

Once you have CloudCompose up and running, you can interact with your instances either using `cloudcompose` or directly using `docker-compose` on the host.

```
$ cloudcompose --ps
Name                   Command             State              Ports
------------------------------------------------------------------------------------
cloudnet_redis_1   /entrypoint.sh redis-server   Up      6379/tcp
cloudnet_web_1     nginx -g daemon off;          Up      443/tcp, 0.0.0.0:80->80/tcp
```

```
$ docker-compose ps
Name                   Command             State              Ports
------------------------------------------------------------------------------------
cloudnet_redis_1   /entrypoint.sh redis-server   Up      6379/tcp
cloudnet_web_1     nginx -g daemon off;          Up      443/tcp, 0.0.0.0:80->80/tcp
```

For more information on how to use Docker Compose, please see the [official Docker Compose documentation](https://docs.docker.com/compose/).
