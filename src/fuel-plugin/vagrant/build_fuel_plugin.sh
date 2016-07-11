#!/bin/bash
sudo apt-get update -y
sudo apt-get install -y ruby-dev rubygems-integration python-pip rpm createrepo dpkg-dev git
sudo gem install fpm
sudo pip install fuel-plugin-builder
cp -r /fuel-plugin /home/vagrant
cd /home/vagrant/fuel-plugin; 
rm -rf vagrant/.vagrant
fpb --debug --build .
cp *.rpm /vagrant
