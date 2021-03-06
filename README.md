[![Coverage Status](https://coveralls.io/repos/frogmaster/opentsdb-snmp/badge.svg?branch=multiprocess)](https://coveralls.io/r/frogmaster/opentsdb-snmp?branch=multiprocess)

# opentsdb-snmp

Simple program to push metrics from snmp to [opentsdb](http://opentsdb.net/)

# installation


requirements:

* python-netsnmp
* pyyaml
* python 2.7

Personally i like to install distro's python-netsnmp and virtualenv everything else...
Commands should be something like this, i may be forgetting something

    $ virtualenv --system-site-packages snmpenv
    $ . snmpenv/bin/activate
    $ pip install pyyaml
    $ python setup.py install
    
# running

    $ opentsdb-snmp --config=bar/conf.yml --interval=300 --readers=50 --loglevel=info --hostlist=foo/hostlist.yml

# configuration

Configuration is stored in YAML format and has four values: tsd, hosts_file, metrics_dir and metrics.
metrics from main config and from yml files in metrics_dir are merged using dict.update(), no errors 
are thrown on duplicates, so take care.

Example configuration file:

    hosts_file: "misc/sample_hostlist.yml"
    tsd: #list of tsd-s
      -
        host: "localhost" #host
        port: 5431 #port
      -
        host: "localhost"
    metrics_dir: "path/to/yml/files/containing/metrics" #see misc/example_metrics/complex_metric1.yml
    metrics: #it's cleaner to use metrics dir, but you can put metrics here

[example_metrics_file] (misc/example_metrics/complex_metric1.yml)

### hosts_file example:

    - 
      hostname: "foo"
      community: "bar"
      snmp_version: 2
      metrics: 
        - "ifInHCOutUcastPkts"
    - 
      hostname: "bar"
      community: "foo"
      snmp_version: 2
      metrics: 
        - "ifInUcastPkts"
        - ""ifOutOctets"


# resolvers

Resolver takes raw data and returns extra tags.
Things passed to resolver resolve() method are: index, device object
index in this context is snmp returned oid - metrics oid
For example:

When metrics oid is 
    
    1.2.3.4

and walk returns

    1.2.3.4.1.1
    1.2.3.4.1.2
    1.2.3.4.2.1
    ...

then indexes will be
    
    1.1
    1.2
    2.1


## Adding resolvers

Add the following files:

    REPO/src/opentsdb/snmp/resolvers/myresolver.py
    REPO/test/resolver_myresolver_tests.py

Add appropriate code...

Add entry point to resolvers in:

    REPO/setup.py

Run:

    > python setup.py develop
    > python setup.py test

And make sure the tests pass...

Add documentation to this file in next section

## Implemented resolvers 
### default
index x will be translated to index=x
index x.y...n will be translated to index1=x index2=y indexn=n
   
### ifname
Ifname is walked and cached in memory and
index will be translated to interface=ifname

### after_index
index x.1 will be tranlated to index=x direction=in
index x.2 will be translated to index=x direction=out

### d500_xdsl
index [x]xyy will be translated to interface [x]x/yy
(first x is not mandatory)
