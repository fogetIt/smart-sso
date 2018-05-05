# -*- coding: utf-8 -*-
# @Date:   2018-03-22 11:16:52
# @Last Modified time: 2018-03-22 14:30:44
from fabric.api import *


env.user = "zdd"
env.hosts = ["127.0.0.1"]
env.password = "123zhang"
pypi = "https://pypi.tuna.tsinghua.edu.cn/simple"
local_dir = "/home/zdd/zddHome/proj/smart-sso"


def kill():
    local("lsof -t -i:4567 && kill -9 $(lsof -t -i:4567 | sed -n '1p;1q')")


def install():
    sudo("virtualenv --version || pip install virtualenv -i %s" % pypi)
    sudo("apt-get install libssl-dev python-dev -y")
    sudo("apt-get install libpcre3 libpcre3-dev -y")
    with lcd(local_dir):
        local(
            """
            [[ -f ./venv/bin/activate ]] \\
            || virtualenv ./venv --system-site-packages -p $(which python)
            """
        )
        with prefix("source ./venv/bin/activate"):
            local("pip install -r requirements.txt -i %s" % pypi)


def nginx():
    with lcd(local_dir):
        sudo("cp ./sso.conf /etc/nginx/conf.d/")
        local("/etc/init.d/nginx restart")


def start():
    with lcd(local_dir):
        with prefix("source ./venv/bin/activate"):
            local("uwsgi --ini uwsgi.ini")


def doc():
    with lcd(local_dir):
        with prefix("npm run setup"):
            local("npm run doc:server")


@runs_once
def restart():
    execute(kill)
    execute(start)


def deploy():
    install()
    restart()


env.roledefs = {
    'ubuntu': [''],
}
env.passwords = {
    'ubuntu': '',
}

@roles("ubuntu")
def remote_option():
    remote_dir = "/home/ubuntu/www"
    with cd(remote_dir):
        run("ls")
        port = prompt('Please input port number: ', default=4001, validate=int)
        sudo("lsof -i:%s" % port)
        # reboot(wait=60)
