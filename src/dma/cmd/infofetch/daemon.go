/*
 * Copyright 2018 NEC Corporation
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
	"github.com/BurntSushi/toml"
	"github.com/distributed-monitoring/agent/pkg/common"
	"github.com/go-redis/redis"
	libvirt "github.com/libvirt/libvirt-go"
	"log"
	"sync"
)

var infoPool common.RedisPool

// Config is ...
type Config struct {
	Common    CommonConfig
	InfoFetch InfoFetchConfig
}

// CommonConfig is ...
type CommonConfig struct {
	RedisHost     string `toml:"redis_host"`
	RedisPort     string `toml:"redis_port"`
	RedisPassword string `toml:"redis_password"`
	RedisDB       int    `toml:"redis_db"`
}

// InfoFetchConfig is ...
type InfoFetchConfig struct {
	OSUsername          string `toml:"os_username"`
	OSUserDomainName    string `toml:"os_user_domain_name"`
	OSProjectDomainName string `toml:"os_project_domain_name"`
	OSProjectName       string `toml:"os_project_name"`
	OSPassword          string `toml:"os_password"`
	OSAuthURL           string `toml:"os_auth_url"`
}

func main() {

	var config Config
	_, err := toml.DecodeFile("/etc/barometer-dma/config.toml", &config)
	if err != nil {
		log.Println("Read error of config file")
	}

	var waitgroup sync.WaitGroup
	libvirt.EventRegisterDefaultImpl()

	redisClient := redis.NewClient(&redis.Options{
		Addr:     config.Common.RedisHost + ":" + config.Common.RedisPort,
		Password: config.Common.RedisPassword,
		DB:       config.Common.RedisDB,
	})
	infoPool = common.RedisPool{Client: redisClient}
	// Initialize redis db...
	infoPool.DelAll()

	conn, err := libvirt.NewConnect("qemu:///system")
	if err != nil {
		log.Fatalln("libvirt connect error")
	}
	defer conn.Close()

	vmIfInfoChan := make(chan string)
	{
		ctx := context.Background()
		waitgroup.Add(1)
		go func() {
			RunNeutronInfoFetch(ctx, &config, vmIfInfoChan)
			waitgroup.Done()
		}()
	}

	//Get active VM info
	GetActiveDomain(conn, vmIfInfoChan)
	{
		ctx := context.Background()
		waitgroup.Add(1)
		go func() {
			RunVirshEventLoop(ctx, conn, vmIfInfoChan)
			waitgroup.Done()
		}()
	}

	waitgroup.Wait()
}
