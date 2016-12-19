#!/bin/bash
sudo apt-get update -y
sudo apt-get install -y ruby-dev rubygems-integration python-pip rpm createrepo dpkg-dev git docker.io
sudo gem install fpm
sudo pip install fuel-plugin-builder
cd /fuel-plugin;
fpb --debug --build .
