#!/bin/bash

sudo yum remove python3 -y

# if error occurs in install make sure python3.8 is present
amazon-linux-extras | grep python

# if python3.8 not modify commands below to use what is there

sudo amazon-linux-extras install python3.8 -y

sudo ln -s /usr/bin/python3.8 /usr/bin/python3

echo "alias python3='/usr/bin/python3.8'" >> ~/.bash_aliases
