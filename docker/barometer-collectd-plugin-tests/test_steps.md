# Running Tests

## Setps

To create the dockerfile which keeps the test cases loaded:

```bash
    $cd \path\to\barometer
```

Then run this command to build the container:

```bash
     sudo docker build -t opnfv/barometer-collectd-tests --network=host \
     -f docker/barometer-collectd-plugin-tests/Dockerfile .
```

Then run the test cases dockerfile with the command :

```bash
    sudo docker run -ti --net=host \
    -v `pwd`/src/collectd/collectd_sample_configs-master:/opt/collectd/etc/collectd.conf.d \
    -v /var/run:/var/run -v /tmp:/tmp --privileged opnfv/barometer-collectd-plugin-tests
```

## Dependencies
## Output


This is currently a WIP things that will be added :
    - storing output for the tests in different plugin files in a results folder
    - adding tests
    - reading from plugins.txt
