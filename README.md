# Smart Meter Reader for EVN / Netz Niederösterreich

This Python project enables reading energy consumption data from a smart meter equipped with a dedicated customer
interface and sending the data to Home Assistant (or any other broker) via MQTT. It is specifically developed for smart
meters installed in Lower Austria by EVN / Netz Niederösterreich, which are equipped with an M-Bus customer interface
("[Kundenschnittstelle](https://www.netz-noe.at/Download-(1)/Smart-Meter/218_9_SmartMeter_Kundenschnittstelle_lektoriert_14.aspx)").

The smart meter M-Bus interface allows unidirectional communication with an external device. The smart meter periodically pushes data every 5 seconds which can be received via an M-Bus converter. The data format follows the DLMS/COSEM protocol. Since available parsers/translators didn't work reliably for me or just seemed too complex and bulky for this purpose, this project contains a simple configurable standalone parser for extracting the data. The configurability may allow reusing the project for smart meters from other providers as well.

The script is meant to be run on a Raspberry Pi (or similar) connected to the smart meter via an M-Bus USB converter.

```mermaid
block-beta
    sm["Smart\nMeter"] space
    mbus["M-Bus USB\nConverter"] space
    rpi["Raspberry\nPi"] space
    ha["Home\nAssistant"] space
    sm-- "RJ12" -->mbus
    mbus-- "USB" -->rpi
    rpi-- "MQTT" -->ha
```

# Prerequisites

## Supported Smart Meters

This project is created and tested for the smart meter **Sagemcom T210-D** from Netz NÖ. The following smart meters from Netz NÖ should also work:

- Sagemcom S210
- Kaifa M110
- Kaifa MA309

Since the frame and data formats are configurable, smart meters from other providers might also work with some configuration changes.

In the following installation steps a smart meter from Netz NÖ is assumed.

## Prepare Smart Meter

You need to request unlocking of the smart meter interface from your provider and obtain an encryption key to be able to
receive and decrypt the data. See [Netz NÖ
Kundenschnittstelle](https://www.netz-noe.at/Download-(1)/Smart-Meter/218_9_SmartMeter_Kundenschnittstelle_lektoriert_14.aspx) for further details.


## Required Hardware

- Raspberry Pi
- M-Bus USB Converter (search for "MBUS USB Slave Converter" on Amazon or Aliexpress)
- RJ12 Cable

## Hardware Setup

Pins 3 and 4 (the two middle pins) of the RJ12 connector need to be connected with the M-Bus input of the M-Bus USB Converter (polarity doesn't matter since it is a differential signal). Connect the RJ12 cable with the smart meter P1 interface and the M-Bus USB Converter with the Raspberry Pi.

## Home Assistant (optional)

The script publishes the received data to an MQTT broker, which in my case is running on my Home Assistant server. This requires the [MQTT Integration](https://www.home-assistant.io/integrations/mqtt/) to be installed and setup in Home Assistant. However, any other MQTT broker may also be used.


# Getting Started

The project contains a [setup.sh](setup.sh) script which allows quick and easy setup on a Raspberry Pi.

## Clone the Repository

Clone the repository to `/home/pi/smartmeterreader`:

```
git clone https://github.com/lgraho/smartmeterreader.git
```

## Configure

Set the following parameters in [config.yaml](config.yaml):

- `encryption_key`: The key you got from your provider (e.g. Netz NÖ) as a hexadecimal string.
- `mqtt`: Configuration for connecting and sending data to an MQTT broker.
   - `broker`: The IP address of your MQTT broker (e.g. your Home Assistant server).
   - `user`: The username for connecting to the broker.
   - `password`: The password for connecting to the broker.

See [Configuration](#configuration) for a description of the other available configuration items.

## Run Setup Script

Go to the project directory:

```
cd /home/pi/smartmeterreader
```

Make the setup script executable:

```
chmod +x ./setup.sh
```

Run the script:

```
./setup.sh
```

The setup script installs all required dependencies, creates a virtual Python environment, and sets up the program as a `systemd` background service.

## Run as a Service

The `systemd` service can be started with:

```
./scripts/start_service.sh
```

This also enables the service to be started automatically in the background on each boot.

## Run manually

You can run the script also manually:

```
./venv/bin/python ./smartmeterreader/main.py
```

## Check Status

You can check the status of the service with:

```
systemctl status smartmeter
```

And the log with:

```
journalctl -f -u smartmeter
```

(Press `Ctrl + C` to exit again.)


# Configuration

The configuration can be found in [config.yaml](config.yaml). It is split into several sections which are described in more detail here.

## M-Bus

The section `mbus` defines the serial port and baudrate of the M-Bus interface. The default values should already work.

## Encryption Key

The `encryption_key` is a hexadecimal string needed to decrypt the received encrypted data. This needs to be set to your personal encryption key obtained from your provider.

## MQTT

The section `mqtt` defines the MQTT connection settings and the MQTT topic the data shall be published to.

## Home Assistant (optional)

On startup, the script publishes specific discovery topics to minimize configuration effort on the side of Home Assistant (see [MQTT Discovery](https://www.home-assistant.io/integrations/mqtt/#mqtt-discovery)). These topics are defined in the section `homeassistant` of the configuration file.

If you are not using Home Assistant or you want to disable automatic discovery, simply remove the `homeassistant` section from the configuration file.


# Data Format Definition

The M-Bus frame and APDU (Application Protocol Data Unit) data formats are defined in a separate file [data_format.yaml](data_format.yaml). This allows easier adjustments to other similar protocol formats without having to modify the actual code. The file contains the following two sections.

## Frame Format

The format of the M-Bus frames is defined in the section `frame_format`. Here the frame size, the preamble used to detect the start of a frame and and the frame segments to be extracted can be configured.

## APDU Format

The format of the APDU payload data is defined in the section `apdu_format`. This
section defines a list of data fields to be extracted from the decrypted data. It is extracted by searching for the
respective data field by the defined OBIS code and unpacking the contained data items using the format string (see
[Python struct library](https://docs.python.org/3/library/struct.html)).


# Scripts

The project contains some convenience scripts in  the folder [scripts/](scripts/):

Start the service:

```
./scripts/start_service.sh
```

Stop the service:

```
./scripts/stop_service.sh
```

Check if the the service is running:

```
./scripts/status_service.sh
```


# License

This project is licensed under the GNU General Public License v3.0 License. See the [LICENSE](LICENSE) file for details.