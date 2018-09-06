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
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"net/url"
	"os"
	"strings"
	"text/template"
	"time"
)

var env *InfoFetchConfig

type userInfo struct {
	UserDomainName    string
	UserName          string
	Password          string
	ProjectDomainName string
	ProjectName       string
}

var tokenJSONTemplate = `{
  "auth": {
    "identity": {
      "methods": [
        "password"
      ],
      "password": {
        "user": {
          "domain": {
            "name": "{{.UserDomainName}}"
          },
          "name": "{{.UserName}}",
          "password": "{{.Password}}"
        }
      }
    },
    "scope": {
      "project": {
        "domain": {
          "name": "{{.ProjectDomainName}}"
        },
        "name": "{{.ProjectName}}"
      }
    }
  }
}
`

type tokenReply struct {
	Token struct {
		IsDomain bool     `json:"is_domain"`
		Methods  []string `json:"methods"`
		Roles    []struct {
			ID   string `json:"id"`
			Name string `json:"name"`
		} `json:"roles"`
		ExpiresAt time.Time `json:"expires_at"`
		Project   struct {
			Domain struct {
				ID   string `json:"id"`
				Name string `json:"name"`
			} `json:"domain"`
			ID   string `json:"id"`
			Name string `json:"name"`
		} `json:"project"`
		User struct {
			PasswordExpiresAt interface{} `json:"password_expires_at"`
			Domain            struct {
				ID   string `json:"id"`
				Name string `json:"name"`
			} `json:"domain"`
			ID   string `json:"id"`
			Name string `json:"name"`
		} `json:"user"`
		AuditIds []string  `json:"audit_ids"`
		IssuedAt time.Time `json:"issued_at"`
	} `json:"token"`
}

type token struct {
	Token     string
	ExpiresAt time.Time
}

func (t *token) CheckToken() {
	now := time.Now()

	if t.ExpiresAt.Sub(now).Seconds() < 30 {
		newToken, _ := getToken()
		t.Token = newToken.Token
		t.ExpiresAt = newToken.ExpiresAt
	}
}

func getToken() (*token, error) {
	var buf bytes.Buffer

	t := template.Must(template.New("json template1").Parse(tokenJSONTemplate))
	p := userInfo{
		UserDomainName:    env.OSUserDomainName,
		UserName:          env.OSUsername,
		Password:          env.OSPassword,
		ProjectDomainName: env.OSProjectDomainName,
		ProjectName:       env.OSProjectName,
	}
	t.Execute(&buf, p)

	body := bytes.NewReader(buf.Bytes())
	req, err := http.NewRequest("POST", env.OSAuthURL+"/auth/tokens?nocatalog", body)
	if err != nil {
		return &token{"", time.Unix(0, 0)}, fmt.Errorf("http request failed: %v", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return &token{"", time.Unix(0, 0)}, fmt.Errorf("http POST failed: %v", err)
	}
	defer resp.Body.Close()
	b, err := ioutil.ReadAll(resp.Body)

	tokenStr, ok := resp.Header["X-Subject-Token"]
	if ok != true && len(tokenStr) != 1 {
		return &token{"", time.Unix(0, 0)}, fmt.Errorf("no token in openstack reply")
	}

	var repl tokenReply
	err = json.Unmarshal(b, &repl)

	return &token{tokenStr[0], repl.Token.ExpiresAt}, nil
}

type service struct {
	Description string `json:"description"`
	Links       struct {
		Self string `json:"self"`
	} `json:"links"`
	Enabled bool   `json:"enabled"`
	Type    string `json:"type"`
	ID      string `json:"id"`
	Name    string `json:"name"`
}

type serviceListReply struct {
	Services []service `json:"services"`
}

func (s *serviceListReply) GetService(name string) (*service, error) {
	for _, v := range s.Services {
		if v.Name == name {
			return &v, nil
		}
	}
	return nil, fmt.Errorf("no service id (%s) found", name)
}

type endPoint struct {
	RegionID string `json:"region_id"`
	Links    struct {
		Self string `json:"self"`
	} `json:"links"`
	URL       string `json:"url"`
	Region    string `json:"region"`
	Enabled   bool   `json:"enabled"`
	Interface string `json:"interface"`
	ServiceID string `json:"service_id"`
	ID        string `json:"id"`
}

type endPointReply struct {
	Endpoints []endPoint `json:"endpoints"`
}

func (e *endPointReply) GetEndpoint(serviceid string, ifname string) (*endPoint, error) {
	for _, v := range e.Endpoints {
		if v.Interface == ifname && v.ServiceID == serviceid {
			return &v, nil
		}
	}
	return nil, fmt.Errorf("no endpoint found (%s/%s)", serviceid, ifname)
}

func getEndpoints(token *token) (endPointReply, error) {
	token.CheckToken()
	req, err := http.NewRequest("GET", env.OSAuthURL+"/endpoints", nil)
	if err != nil {
		return endPointReply{}, fmt.Errorf("request failed:%v", err)
	}
	req.Header.Set("X-Auth-Token", token.Token)

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return endPointReply{}, fmt.Errorf("http GET failed:%v", err)
	}
	defer resp.Body.Close()

	b, err := ioutil.ReadAll(resp.Body)
	//fmt.Printf("%s", string(b))

	var repl endPointReply
	err = json.Unmarshal(b, &repl)
	if err != nil {
		return endPointReply{}, fmt.Errorf("http reply decoding failed:%v", err)
	}
	//fmt.Printf("%v", repl)
	return repl, nil
}

func getServiceList(token *token) (serviceListReply, error) {
	token.CheckToken()
	req, err := http.NewRequest("GET", env.OSAuthURL+"/services", nil)
	if err != nil {
		return serviceListReply{}, fmt.Errorf("request failed:%v", err)
	}
	req.Header.Set("X-Auth-Token", token.Token)

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return serviceListReply{}, fmt.Errorf("http GET failed:%v", err)
	}
	defer resp.Body.Close()
	b, err := ioutil.ReadAll(resp.Body)

	var repl serviceListReply
	err = json.Unmarshal(b, &repl)
	if err != nil {
		return serviceListReply{}, fmt.Errorf("http reply decoding failed:%v", err)
	}
	return repl, nil
}

type neutronPort struct {
	AllowedAddressPairs []interface{} `json:"allowed_address_pairs"`
	ExtraDhcpOpts       []interface{} `json:"extra_dhcp_opts"`
	UpdatedAt           time.Time     `json:"updated_at"`
	DeviceOwner         string        `json:"device_owner"`
	RevisionNumber      int           `json:"revision_number"`
	PortSecurityEnabled bool          `json:"port_security_enabled"`
	BindingProfile      struct {
	} `json:"binding:profile"`
	FixedIps []struct {
		SubnetID  string `json:"subnet_id"`
		IPAddress string `json:"ip_address"`
	} `json:"fixed_ips"`
	ID                string        `json:"id"`
	SecurityGroups    []interface{} `json:"security_groups"`
	BindingVifDetails struct {
		PortFilter    bool   `json:"port_filter"`
		DatapathType  string `json:"datapath_type"`
		OvsHybridPlug bool   `json:"ovs_hybrid_plug"`
	} `json:"binding:vif_details"`
	BindingVifType  string        `json:"binding:vif_type"`
	MacAddress      string        `json:"mac_address"`
	ProjectID       string        `json:"project_id"`
	Status          string        `json:"status"`
	BindingHostID   string        `json:"binding:host_id"`
	Description     string        `json:"description"`
	Tags            []interface{} `json:"tags"`
	QosPolicyID     interface{}   `json:"qos_policy_id"`
	Name            string        `json:"name"`
	AdminStateUp    bool          `json:"admin_state_up"`
	NetworkID       string        `json:"network_id"`
	TenantID        string        `json:"tenant_id"`
	CreatedAt       time.Time     `json:"created_at"`
	BindingVnicType string        `json:"binding:vnic_type"`
	DeviceID        string        `json:"device_id"`
}

type neutronPortReply struct {
	Ports []neutronPort `json:"ports"`
}

func getNeutronPorts(token *token, endpoint string) (neutronPortReply, error) {
	token.CheckToken()
	req, err := http.NewRequest("GET", endpoint+"/v2.0/ports", nil)
	if err != nil {
		return neutronPortReply{}, fmt.Errorf("request failed:%v", err)
	}
	req.Header.Set("X-Auth-Token", token.Token)

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return neutronPortReply{}, fmt.Errorf("http GET failed:%v", err)
	}
	defer resp.Body.Close()

	b, err := ioutil.ReadAll(resp.Body)

	var repl neutronPortReply
	err = json.Unmarshal(b, &repl)
	if err != nil {
		return neutronPortReply{}, fmt.Errorf("http reply decoding failed:%v", err)
	}
	return repl, nil
}

func (n *neutronPortReply) GetNeutronPortfromMAC(mac string) (*neutronPort,
	error) {
	for _, v := range n.Ports {
		if v.MacAddress == strings.ToLower(mac) {
			return &v, nil
		}
	}
	return nil, fmt.Errorf("no port (%s) found", mac)
}

type neutronNetwork struct {
	ProviderPhysicalNetwork string        `json:"provider:physical_network"`
	Ipv6AddressScope        interface{}   `json:"ipv6_address_scope"`
	RevisionNumber          int           `json:"revision_number"`
	PortSecurityEnabled     bool          `json:"port_security_enabled"`
	Mtu                     int           `json:"mtu"`
	ID                      string        `json:"id"`
	RouterExternal          bool          `json:"router:external"`
	AvailabilityZoneHints   []interface{} `json:"availability_zone_hints"`
	AvailabilityZones       []string      `json:"availability_zones"`
	ProviderSegmentationID  interface{}   `json:"provider:segmentation_id"`
	Ipv4AddressScope        interface{}   `json:"ipv4_address_scope"`
	Shared                  bool          `json:"shared"`
	ProjectID               string        `json:"project_id"`
	Status                  string        `json:"status"`
	Subnets                 []string      `json:"subnets"`
	Description             string        `json:"description"`
	Tags                    []interface{} `json:"tags"`
	UpdatedAt               time.Time     `json:"updated_at"`
	IsDefault               bool          `json:"is_default"`
	QosPolicyID             interface{}   `json:"qos_policy_id"`
	Name                    string        `json:"name"`
	AdminStateUp            bool          `json:"admin_state_up"`
	TenantID                string        `json:"tenant_id"`
	CreatedAt               time.Time     `json:"created_at"`
	ProviderNetworkType     string        `json:"provider:network_type"`
}

type neutronNetworkReply struct {
	Networks []neutronNetwork `json:"networks"`
}

func (n *neutronNetworkReply) GetNetworkFromID(netid string) (*neutronNetwork, error) {
	for _, v := range n.Networks {
		if v.ID == netid {
			return &v, nil
		}
	}
	return nil, fmt.Errorf("no network (%s) found", netid)
}

func getNetworkReply(token *token, endpoint string) (neutronNetworkReply, error) {
	token.CheckToken()
	req, err := http.NewRequest("GET", endpoint+"/v2.0/networks", nil)
	if err != nil {
		return neutronNetworkReply{}, fmt.Errorf("request failed:%v", err)
	}
	req.Header.Set("X-Auth-Token", token.Token)

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return neutronNetworkReply{}, fmt.Errorf("http GET failed:%v", err)
	}
	defer resp.Body.Close()

	b, err := ioutil.ReadAll(resp.Body)

	var repl neutronNetworkReply
	err = json.Unmarshal(b, &repl)
	if err != nil {
		return neutronNetworkReply{}, fmt.Errorf("http reply decoding failed:%v", err)
	}
	return repl, nil
}

type novaCompute struct {
	ID    string `json:"id"`
	Links []struct {
		Href string `json:"href"`
		Rel  string `json:"rel"`
	} `json:"links"`
	Name string `json:"name"`
}

type novaComputeReply struct {
	Servers []novaCompute `json:"servers"`
}

func (n *novaComputeReply) GetComputeFromID(vmid string) (*novaCompute, error) {
	for _, v := range n.Servers {
		if v.ID == vmid {
			return &v, nil
		}
	}
	return nil, fmt.Errorf("no vm (%s) found", vmid)
}

func getComputeReply(token *token, endpoint string) (novaComputeReply, error) {
	token.CheckToken()
	values := url.Values{}
	values.Add("all_tenants", "1")

	req, err := http.NewRequest("GET", endpoint+"/servers", nil)
	if err != nil {
		return novaComputeReply{}, fmt.Errorf("request failed:%v", err)
	}
	req.Header.Set("X-Auth-Token", token.Token)
	req.URL.RawQuery = values.Encode()

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return novaComputeReply{}, fmt.Errorf("http GET failed:%v", err)
	}
	defer resp.Body.Close()

	b, err := ioutil.ReadAll(resp.Body)

	var repl novaComputeReply
	err = json.Unmarshal(b, &repl)
	if err != nil {
		return novaComputeReply{}, fmt.Errorf("http reply decoding failed:%v", err)
	}

	return repl, nil
}

type osNeutronInterfaceAnnotation struct {
	IfName      string
	VMName      string
	NetworkName string
}

// RunNeutronInfoFetch gets redis key update from libvirt and get network information
// from Neutron with REST api. The retrieved information is stored under redis,
// if/<tap name>/neutron_network
func RunNeutronInfoFetch(ctx context.Context, config *Config, vmIfInfo chan string) error {
	env = &config.InfoFetch
	token, err := getToken()

	if err != nil {
		fmt.Fprintf(os.Stderr, "cannot get token: %v", err)
		return err
	}

	svc, _ := getServiceList(token)
	neuID, _ := svc.GetService("neutron")
	//fmt.Printf("neutron id:%s\n", id.ID)

	novaID, _ := svc.GetService("nova")
	//fmt.Printf("nova id:%s\n", id.ID)

	endpoints, _ := getEndpoints(token)
	neuEndpoint, _ := endpoints.GetEndpoint(neuID.ID, "admin")
	//fmt.Printf("neutron endpoint:%s\n", neuEndpoint.URL)

	novaEndpoint, _ := endpoints.GetEndpoint(novaID.ID, "admin")
	//fmt.Printf("nova endpoint:%s\n", novaEndpoint.URL)

	getComputeReply(token, novaEndpoint.URL)
	getNeutronPorts(token, neuEndpoint.URL)
	//vmrepl, _ := getComputeReply(token, novaEndpoint.URL)
	//prepl, _ := getNeutronPorts(token, neuEndpoint.URL)

EVENTLOOP:
	for {
		select {
		case <-ctx.Done():
			break EVENTLOOP
		case key := <-vmIfInfo:
			log.Printf("Incoming IF: %v", key)
			libvirtIfInfo, err := infoPool.Get(key)
			if err != nil {
				log.Fatalf("Err: %v", err)
			} else {
				var ifInfo osVMInterfaceAnnotation
				err = json.Unmarshal([]byte(libvirtIfInfo), &ifInfo)
				if err != nil {
					log.Fatalf("Err: %v", err)
				} else {
					vmrepl, _ := getComputeReply(token, novaEndpoint.URL)
					prepl, _ := getNeutronPorts(token, neuEndpoint.URL)
					nrepl, _ := getNetworkReply(token, neuEndpoint.URL)
					netid, _ := prepl.GetNeutronPortfromMAC(ifInfo.MacAddr)
					net, _ := nrepl.GetNetworkFromID(netid.NetworkID)
					vm, _ := vmrepl.GetComputeFromID(netid.DeviceID)
					osIfInfo := osNeutronInterfaceAnnotation{
						IfName:      ifInfo.Target,
						VMName:      vm.Name,
						NetworkName: net.Name}

					osIfInfoJSON, err := json.Marshal(osIfInfo)
					if err != nil {
						log.Fatalf("Err: %v", err)
					} else {
						log.Printf("Get: vmname: %s / networkname:%s", vm.Name, net.Name)
						infoPool.Set(fmt.Sprintf("if/%s/%s", ifInfo.Target, "neutron_network"), string(osIfInfoJSON))
					}
				}
			}
		}
	}
	return nil
}
