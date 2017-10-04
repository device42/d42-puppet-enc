# Device42 as Puppet ENC


## What
A simple integration that allows you to set up and manage External Node Classification for Puppet using Device42.  

## Why
As a single point of truth for your network, Device42 is a perfect candidate for providing External Node Classification for your Puppet infrastructure.  

D42 as a Puppet ENC allows you to manage the classifications of all your Puppet nodes in one place.  

## Setup (basic, WIP):
- Create a custom field for devices on D42 called "node_classes" that stores JSON.  This field can be called whatever you like, but should be unique.
- Fill in `settings.yaml` with values that match your setup, including the name of your custom field.
- Run `pip install -r requirements.txt`
- Put your node classification (as JSON) into the "node_classes" custom field on D42. [Writing ENC from Puppetlabs](https://docs.puppet.com/puppet/4.10/nodes_external.html?#enc-output-format)
- Switch your Puppet Master's configuration to use ENC
  - ex:
    ''' for Puppetserver version 2.7
      ENC is configured in /etc/puppetlabs/puppet/puppet.conf
      [master]
      	external_nodes = /home/puppetmaster/d42enc/enc.sh
      	node_terminus = exec
    '''

## Example:
Test the output of the ENC.  
```$ bash enc.sh -n puppet.example.com --verbose
fetching node classification for: puppet.example.com
d42 appliance host: 192.168.0.1
node_classes_field is set to: node_classes
---
classes:
  environment: production
  listexample:
  - 0
  - 1
  - 2
  - 3
  common:
  example:
    parameters: work

```
*Note: do not use --verbose when ENC is actually in use.  Output needs to be __only__ YAML containing the node classification*
Content of node_classes on device named puppet.example.com on D42:
```
{
  "classes": {
    "common": null,
    "example": {
      "parameters": "work"
    },
    "listexample": [0,1,2,3],
    "environment": "production"
  }
}
```


## Upcoming Features / TODO
- Blog tutorial
- Make "node_classes" D42 custom field accept raw YAML instead of JSON.
- Testing alongide the standard (Pupppet D42 Integration)[https://github.com/device42/puppet_to_device42_sync_py]
