/*
 * Copyright 2017 NEC Corporation
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
	"flag"
	"github.com/BurntSushi/toml"
	"log"
	"os"
	"sync"
)

var serverTypeOpt = flag.String("type", "both", "server type: both(default), pubsub, rest")

// Config is ...
type Config struct {
	Server ServerConfig
}

// ServerConfig is ...
type ServerConfig struct {
	ListenPort string `toml:"listen_port"`

	AmqpHost     string `toml:"amqp_host"`
	AmqpUser     string `toml:"amqp_user"`
	AmqpPassword string `toml:"amqp_password"`
	AmqpPort     string `toml:"amqp_port"`

	CollectdConfDir string `toml:"collectd_confdir"`
}

func main() {

	var config Config
	_, err := toml.DecodeFile("/etc/barometer-dma/config.toml", &config)
	if err != nil {
		log.Fatalf("Read error of config file")
	}

	if f, err := os.Stat(config.Server.CollectdConfDir); os.IsNotExist(err) || !f.IsDir() {
		log.Fatalf("Path \"%s\" is not a directory", config.Server.CollectdConfDir)
	}

	var waitgroup sync.WaitGroup

	flag.Parse()

	if *serverTypeOpt == "both" || *serverTypeOpt == "pubsub" {
		ctx := context.Background()
		waitgroup.Add(1)
		go func() {
			defer waitgroup.Done()
			runSubscriber(ctx, &config)
		}()
		log.Printf("Waiting for publish.")
	}

	if *serverTypeOpt == "both" || *serverTypeOpt == "rest" {
		ctx := context.Background()
		waitgroup.Add(1)
		go func() {
			defer waitgroup.Done()
			runAPIServer(ctx, &config)
		}()
		log.Printf("Waiting for REST.")
	}

	waitgroup.Wait()
	log.Printf("Server stop.")
}
