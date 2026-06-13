# Skaffold

[Skaffold](#) is a Python library made for interfacing and scripting for the Framework Skaffold System Controller

## Introduction
This library provides a scripting API to write and run custom programs on the Control Daemon and the input modules of the Framework Laptop 16 without needing to reflash the firmware for every change.

## Features
### ***v1.0**
* Running code on the input modules without needing reflash
* Access to QMK's `raw_hid` API to allow dynamic RGB indicators based on commands from the server
* RGB control model designed with modularity in mind.
* Access to all sorts of sensors from the server's firmware.

***v1.1**
* Additional Daemon for extra Python API implementations like Discord or OBS API

*Upcoming

## DISCLAMER
This project is nowhere near done yet. The afformentioned Framework Skaffold System Controller doesn't even have a github page yet.




## Roadmap
### What *is* ready?
Again I reiterate that this project isn't even close to completion. Thusly, things listed here may not *actually* be ready

* Client Script Builtin Suite

### TODO
---

#### **Next**
* Add a Changelog (This TODO list will move there)

#### **Coming Up**
* Client Script Translator
* Client Script Assembler
* Server Script Builtin Suite (Likely similar to Client Suite)
* Server Script Translator
* Server Script Assembler
* Firmware Interface System
---
#### Docs (Triage)
Based on [Diataxis](https://diataxis.fr/)
* Examples
* Reference
* Tutorials
* How-to Guides
* Explaination

#### **Post Release v1.0**

**v1.1**
* Server Python Daemon
---
***v2.0**
* Revamp of Layout Model to round measurements to different grids including: pixels, cells, keys, and a standard size unit

***v2.1**
* Solution to the problem created by multiple keys being stacked vertically adjacent within the same row of keys
---
**Later**
* Debugging System

## License

[GNU GPLv3.0-only](https://choosealicense.com/licenses/gpl-3.0/)