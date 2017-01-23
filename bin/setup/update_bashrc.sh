#!/bin/bash

if grep -Fxq "cd /osboxes/ZOOM" /home/osboxes/.bashrc; then
    echo "bashrc already updated"
else
    echo "Updating ~/.bashrc..."
    sudo -u osboxes echo "cd /ZOOM" >> /home/osboxes/.bashrc
    sudo -u osboxes echo "echo 'Starting supervisor...'"
    sudo -u osboxes echo "python ./manage.py supervisor --daemonize" >> /home/osboxes/.bashrc
    sudo -u osboxes echo "echo 'Started.'"
fi
