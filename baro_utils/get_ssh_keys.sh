mkdir /home/opnfv/.ssh/
scp $ssh_opts root@"$INSTALLER_IP":/root/.ssh/* /home/opnfv/.ssh/
