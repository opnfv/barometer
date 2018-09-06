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

func evaluate(config *Config, rdlist []rawData) []evalData {
	edlist := []evalData{}

	for _, rd := range rdlist {
		maxVal := 0
		for _, val := range rd.datalist {
			if maxVal < val {
				maxVal = val
			}
		}

		if maxVal > config.Threshold.Min {
			edlist = append(edlist, evalData{rd.key, 1})
		} else {
			edlist = append(edlist, evalData{rd.key, 0})
		}
	}
	return edlist
}
