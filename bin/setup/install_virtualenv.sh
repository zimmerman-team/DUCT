#!/bin/bash

if [ ! -d "/home/osboxes/.env/" ]; then
    echo "Creating virtualenv..."
    sudo -H -u osboxes virtualenv /home/osboxes/.env
    sudo -H -u osboxes /home/osboxes/.env/bin/pip install --upgrade pip
    sudo -H -u osboxes /home/osboxes/.env/bin/pip install -r /home/osboxes/Documents/Zimmerman/ZOOM/requirements.txt

    sudo -H -u osboxes echo "source ~/.env/bin/activate" >> /home/osboxes/.bashrc
else
    echo "Virtualenv already created."
fi
