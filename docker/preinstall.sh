#!/bin/bash

#OvS
if [ -S /var/run/openvswitch/db.sock ] && \
  ps -ef | grep vswitchd | grep -v grep > /dev/null
then
  echo "Found OvS on host system"
  sudo ovs-vsctl set-manager ptcp:6640
  echo "COPY collectd.d/ovs*.conf /opt/collectd/etc/collectd.d/" >> Dockerfile
  sed -i '/LoadPlugin ovs_/s/^#//g' collectd.conf
else
  echo "Dont found OvS on host system"
fi

#mcelog
if which mcelog > /dev/null && [ -S /var/run/mcelog-client ] &&  ps -ef | grep mcelog | grep -v grep > /dev/null
then
  echo "Found mcelog on host system"
  echo "COPY collectd.d/mcelog.conf /opt/collectd/etc/collectd.d/" >> Dockerfile
  sed -i '/LoadPlugin mcelog/s/^#//g' collectd.conf
else
  echo "Dont found mcelog on host system"
fi

#intel_pmu Mandatory installation of jevents on host system
if [ ! -f /usr/local/include/jevents.h ]
then
  echo "Dont found intel_pmu on host system, forcing install"
  git clone https://github.com/andikleen/pmu-tools
  cd pmu-tools/jevents
  sed -i 's/CFLAGS := -g -Wall -O2 -Wno-unused-result/CFLAGS := -g -Wall -O2 -Wno-unused-result -fPIC/' Makefile
  make
  sudo make install
  cd ../..
else
  echo "Found intel_pmu on host system"
fi
echo "COPY collectd.d/intel_pmu.conf /opt/collectd/etc/collectd.d/" >> Dockerfile
sed -i '/LoadPlugin intel_pmu/s/^#//g' collectd.conf

#Hugepages
if [ -d /sys/devices/system/node ] && [ -d /sys/kernel/mm/hugepages ]
then
  echo "Found hugepages on host system"
  echo "COPY collectd.d/hugepages.conf /opt/collectd/etc/collectd.d/" >> Dockerfile
  sed -i '/LoadPlugin hugepages/s/^#//g' collectd.conf
else
  echo "Dont found hugepages on host system"
fi

#intel_rdt
#Dont know how I suppose to check cpu flags, ether and or or?
if grep -q cqm_llc "/proc/cpuinfo" &&
  grep -q cqm_occup_llc "/proc/cpuinfo" &&
  grep -q cqm_mbm_total "/proc/cpuinfo" &&
  grep -q cqm_mbm_local "/proc/cpuinfo"
then
  echo "Found RDT capabilities on host system"
  echo "COPY collectd.d/intel_rdt.conf /opt/collectd/etc/collectd.d/" >> Dockerfile
  sed -i '/LoadPlugin intel_rdt/s/^#//g' collectd.conf
#This shoud be runned in container, after it lunches
  lsmod | grep msr > /dev/null
  if [ ! $? ]
  then
    sudo modprobe msr
  fi
else
  echo "Dont found RDT capabilities on host system"
fi

#virt
ps -ef | grep libvirtd | grep -v grep > /dev/null
if [ $?  -eq "0" ]
then
  echo "Found libvirtd on host system"
  echo "COPY collectd.d/virt.conf /opt/collectd/etc/collectd.d/" >> Dockerfile
  sed -i '/LoadPlugin virt/s/^#//g' collectd.conf
fi

sudo docker build -t collectd:collectd .
