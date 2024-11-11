#!/bin/bash

sudo yum update -y

sudo tee /etc/yum.repos.d/pgdg.repo<<EOF

[pgdg14]

name=PostgreSQL 14 for RHEL/CentOS 7 - x86_64

baseurl=https://download.postgresql.org/pub/repos/yum/14/redhat/rhel-7-x86_64

enabled=1

gpgcheck=0

EOF

sudo yum update -y

sudo yum install postgresql14 -y
