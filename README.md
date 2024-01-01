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

If it doesn't work as expected, I'd suggest making sure that the script works from
the command line within HA. This is more convoluted then you'd hope. 

- If you don't already have an SSH server installed:
  - Install HACS, Home Assistant Community addonS manager
  - Using HACS, install the "SSH & Web Terminal" addon and get to the point where you can SSH into your HA instance and have a shell running.
- Connect to your HA via SSH
- Use "docker ps" to get a list of running containers
- Start another shell in the container with the name "homeassistant"
- Now you can try running the script in the same context that it will be called from the HA dashboard

For example:
```
  ~ # docker ps
CONTAINER ID   IMAGE                                                            COMMAND               CREATED       STATUS                 PORTS                                   NAMES
cc3e56226628   ghcr.io/hassio-addons/ssh/aarch64:17.0.1                         "/init"               2 days ago    Up 2 days                                                      addon_a0d7b954_ssh
bc0f3b5de227   ghcr.io/home-assistant/raspberrypi3-64-homeassistant:2023.12.4   "/init"               3 days ago    Up 3 days                                                      homeassistant
b7490f14cc7a   ghcr.io/esphome/esphome-hassio:2023.12.5                         "/init"               6 days ago    Up 6 days                                                      addon_5c53de3b_esphome
2f0ce7bcc746   ghcr.io/home-assistant/aarch64-hassio-audio:2023.12.0            "/init"               10 days ago   Up 10 days                                                     hassio_audio
e3e598e4e5d9   ghcr.io/home-assistant/aarch64-hassio-supervisor:latest          "/init"               12 days ago   Up 12 days                                                     hassio_supervisor
a0139b205207   ghcr.io/hassio-addons/vscode/aarch64:5.14.2                      "/init"               2 weeks ago   Up 2 weeks (healthy)                                           addon_a0d7b954_vscode
642804a15e05   ghcr.io/home-assistant/aarch64-hassio-multicast:2023.06.2        "/init"               2 weeks ago   Up 2 weeks                                                     hassio_multicast
233f00544b74   ghcr.io/home-assistant/aarch64-hassio-dns:2023.06.2              "/init"               2 weeks ago   Up 2 weeks                                                     hassio_dns
6a766ac6ffa7   ghcr.io/home-assistant/aarch64-hassio-cli:2023.11.0              "/init"               2 weeks ago   Up 2 weeks                                                     hassio_cli
24c0540c3490   ghcr.io/home-assistant/aarch64-hassio-observer:2023.06.0         "/usr/bin/observer"   3 weeks ago   Up 2 weeks             0.0.0.0:4357->80/tcp, :::4357->80/tcp   hassio_observer
~ # docker exec -it bc0f3b5de227 sh
/config #   python3 custom_components/dutch.py 8c-9999.local wake
```

  
