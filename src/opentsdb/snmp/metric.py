# This file is part of opentsdb-snmp.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.  This program is distributed in the hope that it
# will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser
# General Public License for more details.  You should have received a copy
# of the GNU Lesser General Public License along with this program.  If not,
# see <http://www.gnu.org/licenses/>.
import time
import logging


class Metric:
    'Metric class'
    def __init__(self, device, metric=None, tags={}, oid=None, multiply=None,
                 type=None, rate=None, ignore_zeros=False, resolver="default",
                 startidx=None, endidx=None, max_val=None, min_val=None,
                 replacement_val=None):
        self.name = metric
        self.tags = tags
        self.oid = oid
        self.startidx = startidx
        self.endidx = endidx
        self.device = device
        self.host = device.hostname
        self.max_val = max_val
        self.min_val = min_val
        self.replacement_val = replacement_val

        if multiply:
            self.multiply = float(multiply)
        else:
            self.multiply = multiply

        if (rate):
            self.value_modifier = device.value_modifiers["rate"]
        else:
            self.value_modifier = None

        if type == "walk":
            self.walk = True
            if resolver not in device.resolvers:
                raise "Resolver not found"
            self.resolver = device.resolvers[resolver]
        else:
            self.walk = False

    def _get_walk(self, snmp):
        data = snmp.walk(self.oid, startidx=self.startidx, endidx=self.endidx)
        return data

    def _process_walk_data(self, data):
        buf = []
        for idx, dp in data.items():
            if dp is None:
                next
            item = self._process_dp(dp, idx)
            if (item):
                buf.append(item)
        return buf

    def _process_dp(self, dp, key=None):
        if dp is None:
            return
        if self.max_val is not None and int(dp) > int(self.max_val):
            dp = self.replacement_val
        elif self.min_val is not None and int(dp) < int(self.min_val):
            dp = self.replacement_val
        if dp is None:
            return
        tags = self.tags
        if (key):
            resolved = self.resolver.resolve(key, device=self.device)
            if resolved:
                tags = dict(
                    tags.items()
                    + resolved.items()
                )
        tagstr = self._tags_to_str(tags)
        ts = time.time()
        if self.value_modifier:
            dp = self.value_modifier.modify(
                key=self.name + tagstr,
                ts=ts,
                value=dp
            )
        if dp is None:
            return None
        if self.multiply:
            dp = float(dp) * self.multiply
        buf = "put {0} {1} {2} {3}".format(
            self.name, int(ts), dp, tagstr, self.host
        )
        return buf

    def _tags_to_str(self, tagsdict):
        buf = "host=" + self.host
        for key, val in tagsdict.items():
            buf += " " + str(key) + "=" + str(val)
        return buf

    def _get_get(self, snmp):
        data = snmp.get(self.oid)
        return data

    def get_opentsdb_commands(self, snmp):
        logging.debug("getting metric %s from %s", self.name, self.host)
        if self.walk:
            raw = self._get_walk(snmp)
            return self._process_walk_data(raw)
        else:
            raw = self._get_get(snmp)
            return [self._process_dp(raw)]
