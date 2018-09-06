package main

import (
	"fmt"
	"os/exec"
	"strings"
)

func createCollectdConf() error {
	outStatus, errStatus := exec.Command("ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", "localhost", "sudo", "systemctl", "status", "collectd").Output()
	if errStatus != nil {
		return fmt.Errorf("status NG")
	}
	if !strings.Contains(string(outStatus), "running") {
		return fmt.Errorf("status not running")
	}

	_, errStop := exec.Command("ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", "localhost", "sudo", "systemctl", "stop", "collectd").Output()
	if errStop != nil {
		return fmt.Errorf("stop NG")
	}

	_, errStart := exec.Command("ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", "localhost", "sudo", "systemctl", "start", "collectd").Output()
	if errStart != nil {
		return fmt.Errorf("start NG")
	}

	fmt.Println("All complete!")

	return nil
}
