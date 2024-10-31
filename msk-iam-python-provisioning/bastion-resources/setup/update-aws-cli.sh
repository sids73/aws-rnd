#!/bin/bash

sudo yum remove awscli -y

curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip

sudo ./aws/install

echo 'PATH=/usr/local/bin:$PATH' >> ~/.bash_profile