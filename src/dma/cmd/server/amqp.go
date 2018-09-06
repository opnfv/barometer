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
	"github.com/streadway/amqp"
	"log"
	"os"
	"strings"
)

func failOnError(err error, msg string) {
	if err != nil {
		log.Fatalf("%s: %s", msg, err)
	}
}

func runSubscriber(ctx context.Context, config *Config) {
	confDirPath := config.Server.CollectdConfDir
	amqpURL := "amqp://" + config.Server.AmqpUser + ":" + config.Server.AmqpPassword + "@" + config.Server.AmqpHost + ":" + config.Server.AmqpPort + "/"
	conn, err := amqp.Dial(amqpURL)
	failOnError(err, "Failed to connect to RabbitMQ")

	defer conn.Close()

	ch, err := conn.Channel()
	failOnError(err, "Failed to open a channel")
	defer ch.Close()

	err = ch.ExchangeDeclare(
		"collectd-conf", // name
		"fanout",        // type
		false,           // durable
		false,           // auto-deleted
		false,           // internal
		false,           // no-wait
		nil,             // arguments
	)
	failOnError(err, "Failed to declare an exchange")

	q, err := ch.QueueDeclare(
		"",    // name
		false, // durable
		false, // delete when unused
		true,  // exclusive
		false, // no-wait
		nil,   // arguments
	)
	failOnError(err, "Failed to declare a queue")

	err = ch.QueueBind(
		q.Name,          // queue name
		"",              // routing key
		"collectd-conf", // exchange
		false,
		nil)
	failOnError(err, "Failed to bind a queue")

	msgs, err := ch.Consume(
		q.Name, // queue
		"",     // consumer
		true,   // auto-ack
		false,  // exclusive
		false,  // no-local
		false,  // no-wait
		nil,    // args
	)
	failOnError(err, "Failed to register a consumer")

EVENTLOOP:
	for {
		select {
		case <-ctx.Done():
			break EVENTLOOP
		case d, ok := <-msgs:
			if ok {
				dataText := strings.SplitN(string(d.Body), "/", 2)

				dst, err := os.Create(confDirPath + "/" + dataText[0])
				failOnError(err, "File create NG")
				defer dst.Close()

				dst.Write(([]byte)(dataText[1]))

				err = createCollectdConf()
				failOnError(err, "collectd conf NG")

				log.Printf(" [x] %s", d.Body)
			}
		}
	}

}
