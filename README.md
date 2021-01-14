# MQTT Clients for use with TTI

This repository contains classes, examples, and implementations that allow for the quick connections on MQTT streams on The Things Industries cluster. Currentlt, we are writing to CSV so that these scripts can be used as a simple data backup. 

## Getting started

The scripts require Python 3.8 or higher. Create an virtual environment and pip install the dependencies from the requirements.txt file. 

Create API keys for the respective LoRaWAN application at the TTI console and export the key as environmental variable such as 

```
export MQTT_PW=NNXS. ...
```

