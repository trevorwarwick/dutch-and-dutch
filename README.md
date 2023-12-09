# dutch-and-dutch
Python script(s) for very simple control of Dutch &amp; Dutch 8C active loudspeakers

The current script supports putting the speakers in and out of Standby mode, and also
dumping the stored parameters. 

To integrate it in Home Assistant, copy the script into the config/custom-components
directory, and add the following to HA's configuration.yaml. You will need to replace
SPEAKERDNSNAME with the fqdn of one of your speakers, or its IP address if that is fixed.
Reload the HA config, and it will provide you with a new switch that you can put into
the appropriate part of your dashboard(s).
```
command_line:
  - switch:
      name: Dutch 8C Sleep Mode
      unique_id: dutch_8c
      command_on: python3 custom_components/dutch.py SPEAKERDNSNAME wake
      command_off: python3 custom_components/dutch.py SPEAKERDNSNAME sleep
```
