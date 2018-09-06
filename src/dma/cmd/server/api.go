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
	"fmt"
	"github.com/labstack/echo"
	"io"
	"net/http"
	"os"
	"time"
)

func runAPIServer(ctx context.Context, config *Config) {
	confDirPath := config.Server.CollectdConfDir
	e := echo.New()

	e.GET("/", func(c echo.Context) error {
		return c.String(http.StatusOK, "GET OK")
	})
	e.POST("/collectd/conf", func(c echo.Context) error {

		file, err := c.FormFile("file")
		if err != nil {
			return c.String(http.StatusInternalServerError, "file send NG")
		}

		src, err := file.Open()
		if err != nil {
			return c.String(http.StatusInternalServerError, "file open NG")
		}
		defer src.Close()

		dst, err := os.Create(confDirPath + "/" + file.Filename)
		if err != nil {
			return c.String(http.StatusInternalServerError, "file create NG")
		}
		defer dst.Close()

		// Copy
		if _, err = io.Copy(dst, src); err != nil {
			return c.String(http.StatusInternalServerError, "file write NG")
		}

		err = createCollectdConf()
		if err != nil {
			errstr := fmt.Sprintf("collectd conf NG:%v", err)
			return c.String(http.StatusInternalServerError, errstr)
		}
		return c.String(http.StatusCreated, "collectd conf OK")
	})

	// Start server
	go func() {
		urlStr := ":" + config.Server.ListenPort
		if err := e.Start(urlStr); err != nil {
			e.Logger.Info("shutting down the server")
		}
	}()

	// Wait for context.Done() to gracefully shutdown the server with
	// a timeout of 10 seconds.
	<-ctx.Done()
	ctxShutdown, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	if err := e.Shutdown(ctxShutdown); err != nil {
		e.Logger.Fatal(err)
	}

}
