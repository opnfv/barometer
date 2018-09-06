/*
 * Copyright 2017 Red Hat
 *
 *   Licensed under the Apache License, Version 2.0 (the "License");
 *   you may not use this file except in compliance with the License.
 *   You may obtain a copy of the License at
 *
 *       http://www.apache.org/licenses/LICENSE-2.0
 *
 *   Unless required by applicable law or agreed to in writing, software
 *   distributed under the License is distributed on an "AS IS" BASIS,
 *   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *   See the License for the specific language governing permissions and
 *   limitations under the License.
 */

package main

import (
	"context"
	"encoding/json"
	"encoding/xml"
	"fmt"
	libvirt "github.com/libvirt/libvirt-go"
	"log"
)

type instance struct {
	Name  string `xml:"name"`
	Owner struct {
		User    string `xml:"user"`
		Project string `xml:"project"`
	} `xml:"owner"`
	Flavor struct {
		Name string `xml:"name,attr"`
	} `xml:"flavor"`
}

type domain struct {
	Name    string `xml:"name"`
	Devices struct {
		Interfaces []struct {
			Type string `xml:"type,attr"`
			Mac  struct {
				Address string `xml:"address,attr"`
			} `xml:"mac"`
			Target struct {
				Dev string `xml:"dev,attr"`
			} `xml:"target"`
		} `xml:"interface"`
	} `xml:"devices"`
}

type osVMAnnotation struct {
	Name    string
	Owner   string
	Project string
	Flavor  string
}

type osVMInterfaceAnnotation struct {
	Type    string
	MacAddr string
	Target  string
	VMName  string
}

func parseNovaMetadata(metadata string) (*osVMAnnotation, error) {
	data := new(instance)

	if err := xml.Unmarshal([]byte(metadata), data); err != nil {
		log.Println("XML Unmarshal error:", err)
		return nil, err
	}
	log.Printf("Get name: %s user: %s, project: %s, flavor: %s", data.Name, data.Owner.User, data.Owner.Project, data.Flavor.Name)
	return &osVMAnnotation{
		Name:    data.Name,
		Owner:   data.Owner.User,
		Project: data.Owner.Project,
		Flavor:  data.Flavor.Name}, nil
}

func parseXMLForMAC(dumpxml string) (*[]osVMInterfaceAnnotation, error) {
	data := new(domain)

	if err := xml.Unmarshal([]byte(dumpxml), data); err != nil {
		log.Println("XML Unmarshal error:", err)
		return nil, err
	}

	ifAnnotation := make([]osVMInterfaceAnnotation, len(data.Devices.Interfaces))
	for i, v := range data.Devices.Interfaces {
		log.Printf("Interface type: %s, mac_addr: %s, target_dev: %s", v.Type, v.Mac.Address, v.Target.Dev)
		ifAnnotation[i] = osVMInterfaceAnnotation{
			Type:    v.Type,
			MacAddr: v.Mac.Address,
			Target:  v.Target.Dev,
			VMName:  data.Name}
	}
	return &ifAnnotation, nil
}

func setInterfaceAnnotation(ifInfo *[]osVMInterfaceAnnotation, vmIfInfoChan chan string) {
	for _, v := range *ifInfo {
		ifInfoJSON, err := json.Marshal(v)
		if err != nil {
			log.Fatalf("Err: %v", err)
		}
		infoPool.Set(fmt.Sprintf("if/%s/%s", v.Target, "network"), string(ifInfoJSON))

		vmIfInfoChan <- fmt.Sprintf("if/%s/%s", v.Target, "network")
	}
	return
}

func domainEventLifecycleCallback(vmIfInfo chan string) func(c *libvirt.Connect, d *libvirt.Domain, event *libvirt.DomainEventLifecycle) {

	return func(c *libvirt.Connect,
		d *libvirt.Domain, event *libvirt.DomainEventLifecycle) {
		domName, _ := d.GetName()

		switch event.Event {
		case libvirt.DOMAIN_EVENT_DEFINED:
			// VM defined: vmname (libvirt, nova), user, project, flavor
			// Redis: <vnname>/vminfo
			log.Printf("Event defined: domName: %s, event: %v", domName, event)
			metadata, err := d.GetMetadata(libvirt.DOMAIN_METADATA_ELEMENT, "http://openstack.org/xmlns/libvirt/nova/1.0", libvirt.DOMAIN_AFFECT_CONFIG)
			if err != nil {
				log.Fatalf("Err: %v", err)
			}
			vmInfo, err := parseNovaMetadata(metadata)
			if err != nil {
				log.Fatalf("Err: %v", err)
			}
			vmInfoJSON, err := json.Marshal(vmInfo)
			if err != nil {
				log.Fatalf("Err: %v", err)
			}
			infoPool.Set(fmt.Sprintf("vm/%s/%s", domName, "vminfo"), string(vmInfoJSON))
		case libvirt.DOMAIN_EVENT_STARTED:
			// VM started: interface type, interface mac addr, intarface type
			// Redis: <vnname>/interfaces
			log.Printf("Event started: domName: %s, event: %v", domName, event)

			xml, err := d.GetXMLDesc(0)
			if err != nil {
				log.Fatalf("Err: %v", err)
			}
			ifInfo, err := parseXMLForMAC(xml)
			if err != nil {
				log.Fatalf("Err: %v", err)
			}
			setInterfaceAnnotation(ifInfo, vmIfInfo)

			ifInfoJSON, err := json.Marshal(ifInfo)
			if err != nil {
				log.Fatalf("Err: %v", err)
			}
			infoPool.Set(fmt.Sprintf("vm/%s/%s", domName, "interfaces"), string(ifInfoJSON))
		case libvirt.DOMAIN_EVENT_UNDEFINED:
			log.Printf("Event undefined: domName: %s, event: %v", domName, event)
			vmIFInfo, err := infoPool.Get(fmt.Sprintf("vm/%s/%s", domName, "interfaces"))
			if err != nil {
				log.Fatalf("Err: %v", err)
			} else {
				var interfaces []osVMInterfaceAnnotation
				err = json.Unmarshal([]byte(vmIFInfo), &interfaces)
				if err != nil {
					log.Fatalf("Err: %v", err)
				} else {
					for _, v := range interfaces {
						infoPool.Del(fmt.Sprintf("if/%s/%s", v.Target, "network"))
						infoPool.Del(fmt.Sprintf("if/%s/%s", v.Target, "neutron_network"))
					}
				}
			}
			infoPool.Del(fmt.Sprintf("vm/%s/%s", domName, "vminfo"))
			infoPool.Del(fmt.Sprintf("vm/%s/%s", domName, "interfaces"))
		default:
			log.Printf("Event misc: domName: %s, event: %v", domName, event)
		}
	}
}

// GetActiveDomain gets all active domain information from libvirt and it should be called at startup to get
// current running domain information
func GetActiveDomain(conn *libvirt.Connect, vmIfInfoChan chan string) error {
	doms, err := conn.ListAllDomains(libvirt.CONNECT_LIST_DOMAINS_ACTIVE)
	if err != nil {
		log.Fatalf("libvirt dom list error: %s", err)
		return err
	}

	for _, d := range doms {
		name, err := d.GetName()

		// Get VM Info
		metadata, err := d.GetMetadata(libvirt.DOMAIN_METADATA_ELEMENT, "http://openstack.org/xmlns/libvirt/nova/1.0", libvirt.DOMAIN_AFFECT_CONFIG)
		if err != nil {
			log.Fatalf("Err: %v", err)
			return err
		}
		vmInfo, err := parseNovaMetadata(metadata)
		if err != nil {
			log.Fatalf("Err: %v", err)
			return err
		}
		vmInfoJSON, err := json.Marshal(vmInfo)
		if err != nil {
			log.Fatalf("Err: %v", err)
			return err
		}
		infoPool.Set(fmt.Sprintf("vm/%s/%s", name, "vminfo"), string(vmInfoJSON))

		// Get Network info
		xml, err := d.GetXMLDesc(0)
		if err != nil {
			log.Fatalf("Err: %v", err)
			return err
		}
		ifInfo, err := parseXMLForMAC(xml)
		if err != nil {
			log.Fatalf("Err: %v", err)
			return err
		}
		setInterfaceAnnotation(ifInfo, vmIfInfoChan)

		ifInfoJSON, err := json.Marshal(ifInfo)
		if err != nil {
			log.Fatalf("Err: %v", err)
			return err
		}
		infoPool.Set(fmt.Sprintf("vm/%s/%s", name, "interfaces"), string(ifInfoJSON))
	}
	return nil
}

// RunVirshEventLoop is event loop to watch libvirt update
func RunVirshEventLoop(ctx context.Context, conn *libvirt.Connect, vmIfInfoChan chan string) error {
	callbackID, err := conn.DomainEventLifecycleRegister(nil, domainEventLifecycleCallback(vmIfInfoChan))
	if err != nil {
		log.Fatalf("Err: callbackid: %d %v", callbackID, err)
	}

	libvirt.EventAddTimeout(5000, func(timer int) { return }) // 5000 = 5sec
	log.Printf("Entering libvirt event loop()")
EVENTLOOP:
	for {
		select {
		case <-ctx.Done():
			break EVENTLOOP
		default:
			if err := libvirt.EventRunDefaultImpl(); err != nil {
				log.Fatalf("%v", err)
			}
		}
	}
	log.Printf("Quitting libvirt event loop()")

	if err := conn.DomainEventDeregister(callbackID); err != nil {
		log.Fatalf("%v", err)
	}
	return nil
}
