# Skaffold

[Skaffold](#) is a Python library made for interfacing and scripting for the Framework Skaffold System Controller

## Introduction
This library provides a scripting API to write and run custom programs on the Control Daemon and the input modules of the Framework Laptop 16 without needing to reflash the firmware for every change.

## Features
* Running code on the input modules without needing reflash
* Access to QMK's `raw_hid` API to allow dynamic RGB indicators based on commands from the server
* RGB control model designed with modularity in mind.
* Access to all sorts of sensors from the master's firmware.

## DISCLAMER
This project is nowhere near done yet. The afformentioned Framework Skaffold System Controller doesn't even have a github page yet.

PS: Sorry that the file structure is so abysmal.

### What *is* ready?
Again I reiterate that this project isn't even close to completion. Thusly, things listed here may not *actually* be ready

---

* The builtin suite of classes packaged with scripts run on the device (client scripts).


## TODO

* Client Script Translator
* Client Script Assembler
* Server Script Builtin Suite (Likely similar to Client Suite)
* Server Script Translator
* Server Script Assembler
* Firmware Interface System

## License

[MIT](https://choosealicense.com/licenses/mit/)