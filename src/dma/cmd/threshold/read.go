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
	"fmt"
	"github.com/go-redis/redis"
	"os"
	"strconv"
	"strings"
	"time"
)

// e.g. collectd/instance-00000001/virt/if_octets-tapd21acb51-35
const redisKey = "collectd/*/virt/if_octets-*"

func zrangebyscore(config *Config, client *redis.Client, key string) []int {

	unixNow := int(time.Now().Unix())

	val, err := client.ZRangeByScore(key, redis.ZRangeBy{
		Min: strconv.Itoa(unixNow - config.Threshold.Interval),
		Max: strconv.Itoa(unixNow),
	}).Result()

	datalist := []int{}

	if err == redis.Nil {
		fmt.Println("this key is not exist")
		os.Exit(1)
	} else if err != nil {
		panic(err)
	} else {
		for _, strVal := range val {
			split := strings.Split(strVal, ":")
			txVal := split[2]
			floatVal, err := strconv.ParseFloat(txVal, 64)
			if err != nil {
				os.Exit(1)
			}
			datalist = append(datalist, int(floatVal))
		}
	}
	return datalist
}

func read(config *Config) []rawData {
	thresConfig := config.Threshold

	client := redis.NewClient(&redis.Options{
		Addr:     thresConfig.RedisHost + ":" + thresConfig.RedisPort,
		Password: thresConfig.RedisPassword,
		DB:       thresConfig.RedisDB,
	})

	keys, err := client.Keys(redisKey).Result()
	if err != nil {
		panic(err)
	}

	rdlist := []rawData{}

	for _, key := range keys {
		rdlist = append(rdlist, rawData{key, zrangebyscore(config, client, key)})
	}

	return rdlist
}
