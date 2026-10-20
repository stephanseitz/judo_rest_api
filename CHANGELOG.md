# Changelog

Release notes for every version, newest first. Versions up to 1.3.2 were released by [ischraub](https://github.com/ischraub/judo_rest_api) and [OStrama](https://github.com/OStrama/judo_rest_api); from 1.4.0 on they are also on the [releases page](https://github.com/stephanseitz/judo_rest_api/releases) of this fork.

## Version 1.4.2
Documentation only, no change to the integration itself.

* New README: what the integration does, supported devices, entities per device family, installation, configuration, the one-time setup of holiday mode and leakage settings, upgrading from the original integration, and troubleshooting.
* A banner at the top of the README.
* The version history moved from the README to this file.

## Version 1.4.1
Fixes from a review of the whole repository.

* A refused password now says "Invalid authentication" in the setup dialog. It used to say "Failed to connect", which sent you looking for a network problem although the device was answering.
* The device postfix can no longer be changed in the reconfigure dialog. It is part of every unique id: changing it orphaned all entities with their history and created a second set.
* Changing the host in the reconfigure dialog also moves the entry's unique id to the new host, and is refused when another entry already uses that host. Before, the old address stayed blocked for a new device while a second entry for the same device was let through.
* `hacs.json` declares Home Assistant 2024.11 as the minimum, so HACS says so before installing instead of the integration failing to load.
* The tests run on every push and pull request.
* Removed a VS Code workspace file of the original author that was installed with the integration, and the unused `info.md`.

## Version 1.4.0
Support for the **i-soft SAFE+** (device types 0x33, 0x57, and the i-soft K SAFE+ 0x42, 0x67), checked against a SAFE+ on device software 3.02. This fork lives at https://github.com/stephanseitz/judo_rest_api and builds on the work of OStrama and ischraub.

**Device families.** Every device used to get every entity, although the API document gives each family its own command set - and the same code does different things on different devices: on a ZEWA i-SAFE `5100` closes the leakage protection and `5700` starts the holiday mode, where a softener reads its target hardness and salt warning. The device type read at setup now picks the family, and a device only gets the entities its own page of the document lists:

| Family | Device types | Entities |
|---|---|---|
| i-soft SAFE+ | 0x33, 0x57, 0x42, 0x67 | softener entities, hardness unit, leakage limits, holiday mode, micro leakage settings, water today |
| i-soft | 0x32, 0x53, 0x43, 0x54, and softener types the document does not list | softener entities, hardness unit, water today |
| i-soft PRO | 0x58, 0x4b, 0x4c | as in 1.3: softener entities, water scenes, flow and temperature from command 69 |
| SOFTwell | 0x34, 0x59, 0x35, 0x63, 0x36, 0x5a, 0x47, 0x62, 0x48, 0x64 | counters, water treated, water today |
| everything else (ZEWA, i-dos, i-fill, unknown) | | device type, number and software version only |

Entities a device's family does not have are removed on upgrade. On a SAFE+ these are the water scene, scene duration, flow and temperature, which could never work: the device answers command 69 and the scene commands with 400.

**Decoding by family.** The PRO family stores the device number and the operating day counter big-endian and the commissioning date as day/month/year. The i-soft family - the SAFE+ among it - does not: there both counters are little-endian and the commissioning date is unix time. 1.3 applied the PRO layout to every device, which on a SAFE+ showed 13832 operating days instead of 2102 and no commissioning date at all. Checked against the Judo app: device number 205703, 2102 days since the commissioning on 17.01.2021.

**New entities on the i-soft SAFE+**
* **Hardness unit** (select, commands 23 / 24). Also on the i-soft family.
* **Max. extraction duration** (3E, minutes), **max. extraction volume** (3F, litres), **max. flow rate** (40, l/h). The SAFE+ page labels 3F and 40 one way and describes them the other way round; the labels agree with the PRO and ZEWA pages and are taken as right.
* **Holiday mode** (select Off / U1 / U2 / U3) and the switches **close on micro leakage**, **automatic micro leakage test** and **leakage protection globally OFF** - all four live in the one byte of command 41.
* **Water consumption today** in litres, from the day statistics (command FB), with the eight 3-hour buckets as attributes. Asked for every 5 minutes, not on every scan. Also on the i-soft and SOFTwell families.

**Write only.** The SAFE+ answers 3E, 3F, 40 and 41 with an empty payload: they can be set, not read. These entities show what was last set from Home Assistant, keep it across restarts, and are unknown until then. Command 41 always writes the holiday mode and the three leakage settings together, so nothing is sent until all four are known - otherwise switching on the holiday mode would silently reset the micro leakage settings made in the app. After installing, set the three switches once to match the Judo app (Einstellungen -> Kleinleckageprüfung; leakage protection globally OFF is off as long as the app says "Leckageschutz aktiv"), then the holiday mode. The first ones report "saved, but not sent yet"; the last one sends the byte.

**Fixes**
* A select that reads its value back now sets the chosen option. It used to add the option to the current value - harmless only because no such select existed yet.
* A value that lives in Home Assistant only - the scene duration of the PRO family - was lost on the next scan and fell back to its default.
* Downloading diagnostics failed: the loop over the items overwrote the config entry it was called with.
* The bench tool sends each statistics command the date argument it expects (day, week, month or year) and the year in the family's byte order.

**Upgrading from the original integration** (OStrama, 1.0.x): see the notes on 1.1.0 below. Most visibly, the three operating time sensors (minutes, hours, days) are replaced by one combined operating time sensor, and the commissioning date becomes a date without a time of day.

## Version 1.3.2
* `hacs.json` sets `hide_default_branch`, so HACS can only track releases and never the `main` branch. A repository that offers both can end up comparing the installed release against the branch head, which makes the update check look broken.

## Version 1.3.1
* Fixes a regression in 1.3.0: the water scene select went unavailable on device software older than 1.5.31, which took the control away entirely. Activating a scene does not depend on reading one, so the select stays operable and only the shown active scene stays unknown until the firmware supports command 69.
* The scene duration is named so that it sorts directly below the scene in the controls.

## Version 1.3.0
Built on the **current** API command list, `https://judo.eu/ftp-upload/download/REST-API/RESTAPI_Kommandos.pdf`, linked from https://judo.eu/produkte/api/. The November 2024 PDF this integration was written against is outdated and misses command 69 entirely.

* **The active water scene can be read** - command `69` returns a 16 byte device status. The scene select now shows what the device reports instead of what was last sent from here. **Requires device software newer than 1.5.31**; on older firmware the entity stays unavailable, because the API offers no other way to ask and showing the last command would claim more than it knows.
* Two new sensors out of the same answer: **current water flow** in L/h and **water temperature**.
* The scene duration is no longer a configuration entity, so it sits next to the scene in the controls.
* HTTP **429** is retried. Judo documents it as "device control did not reply within 1.5 s" and answers with `Retry-After: 2`, which this now waits.
* Each read command is fetched **once per scan**, not once per entity. Four entities come out of commands `5600` and `6900`, and this device drops connections when requests arrive in quick succession.

## Version 1.2.0
Water scenes for the i-soft PRO family (device types 0x58, 0x4b, 0x4c).

Two new entities:

* **Water scene** - a select with the eleven scenes the device knows: everyday, body care, garden watering, holiday, laundry, pressure washing, filling the pool, filling the heating system and three custom ones. Selecting one activates it on the device.
* **Scene duration** - 15/30/45 minutes, 1/2/6/12 hours or unlimited. It is not stored on the device, so it lives in Home Assistant and is restored after a restart. Default is 2 hours rather than unlimited, which would leave a bypass scene running with leakage protection off.

The scene select is **write only**: the API has no command that reports which scene is running, so what it shows is the scene last activated from Home Assistant. It does not tell you whether that scene is still running, or whether somebody changed it at the device.

Scene numbering was confirmed against a device rather than taken from the document, which contradicts itself about it. `tools/README.md` has the evidence and the field layout of the scene settings, which the probe tool can read out without changing anything:

```
python3 tools/judo_rest_probe.py <ip> -p <password> --scenes
```

## Version 1.1.8
Two decoding corrections for the i-soft PRO family, checked against what the Judo app shows for the same device.

* The software version has a numeric third component on this family. The third byte is a printable letter on an i-soft (`6b1502` reads 2.21k) but a number on an i-soft PRO (`0C0001` reads 1.0.12). 1.1.1 dropped the byte when it was not printable, so `110401` showed as "1.04" where the Judo app shows **1.4.17**. All three forms now decode correctly.
* The device number is read big-endian. The i-soft PRO page of the API document is the only one whose example is not copy-pasted from another page, and `10D36F28` = 282292008 only works big-endian while every other page's example only works little-endian. Note this is not the alphanumeric "Geräte ID" the app shows - that is a different identifier, and neither reading of the number appears in it.

Still open: the app reports an operating time of 783 days where the device's own counter reads 521 (big-endian) or 2306 (little-endian). 521 is the number of days since the commissioning date the same device reports, to the day; 783 would predate it. See `tools/README.md` for the experiment that settles the byte order.

## Version 1.1.7
* The password field in the setup dialog no longer pre-fills the factory setting. Someone who set their own password on the connectivity module and clicks through the form used to store "Connectivity" silently; the entry then fails with 401 and nothing says why. The field is required now, and the factory setting is offered as a hint under it instead. The reconfigure dialog keeps pre-filling the stored password - a password the user set must never be replaced by a default.
* Diagnostics no longer redacts the user name. It is not a secret, and a wrong one was just as invisible as a wrong password.

## Version 1.1.6
* Reverts the re-authentication prompt from 1.1.5. Credentials are entered once when the integration is set up and stay in force until the user changes them through the reconfigure dialog; the integration must not ask for them again because the device had a bad night. A transient 401 - the module answered one whole nightly scan with 401 and was fine afterwards - would have pushed a credentials dialog at a password that was never wrong.
* What stays from 1.1.5 is the part that was actually useful: a 401 says so. The setup error now reads "Judo device refused the configured credentials" instead of "Cannot reach Judo device", which no longer sends you looking for a network problem. The entry keeps retrying like after any other failure.

## Version 1.1.5
* A 401 is now reported as what it is. Before, a refused password surfaced as "Cannot reach Judo device", which sends you looking for a network problem although the device is answering perfectly well. Setup now raises `ConfigEntryAuthFailed` and Home Assistant offers a re-authentication dialog to enter the credentials again.
* During normal operation a re-authentication is only requested after three consecutive scans that failed authentication from start to finish, so a single transient 401 does not pop a dialog. A transient 401 is still retried once.
* 1.1.4 also asked the base URL whenever a 401 came back, on the theory that it would make the module hand out a fresh session. That was speculative and tripled the requests of a failing scan, which risks driving a device that locks out after failed attempts further into it. Removed.

## Version 1.1.4
* A single REST call is retried once on a transient failure (timeout, connection error, HTTP 401/403/5xx). The connectivity module answered every command of one nightly scan with 401 and was fine again afterwards; without a retry that single hiccup took the whole scan down and put an error in the log. On 401 the base URL is touched first, which makes the module hand out a fresh session.
* This repository now publishes GitHub releases. Without them HACS tracks the default branch and labels the installed version with the short commit SHA instead of a version number.
* `hacs.json` carries a readable display name.

## Version 1.1.3
* `operating_time` now declares a `deadband` of 1 hour. The counter advances by 1/60 h every minute, so at a 60 s scan interval every single scan was a state change: ~1440 recorder rows a day for a number that is only interesting to the hour. Now ~23. Simulated over a week the reported value stayed within 15 minutes of the real counter - the deadband bounds the lag, it does not accumulate.
* `water_total` and `water_treated` deliberately keep no deadband: they resolve to one litre and change often while water runs, but that is the data the water dashboard needs.

## Version 1.1.2
* Items can now declare a `deadband`: a change smaller than that is not reported, so it produces neither a state change nor a recorder row. The deadband is measured against the last reported value rather than the last reading, so slow genuine drift still accumulates until it crosses the threshold - the value is quantised, not lost, and the reported value never lags by more than one deadband.
  * `salt_storage_mass`: 50 g. The scale wobbles by a gram or two while nothing is being used, which produced a state change on every single scan. 50 g is the step the entity can be set in anyway and far below the ~250 g one regeneration uses. Against a measured series this cut 11 events in 25 minutes down to 1.

## Version 1.1.1
Follow-up to 1.1.0, from testing against an i-soft PRO.

* `device_type` and `service_contact` had gone unavailable. The length check introduced in 1.1.0 was too strict for them: the device answers `FF00` with one byte and `5800` with fewer than the declared 16. The check now only applies exactly to numeric fields, where a short payload silently loses its high-order bytes; text takes whatever arrives. `device_type` is declared as the one byte it is.
* Because `device_type` failed, the device stayed on the fallback name "Judo Device". Device info is now pushed into the device registry once the values arrive, instead of only being read when an entity is added.
* `device_number` is decoded as a string, so it can no longer render as "2825589796.0" nor be recorded as a statistic.
* Diagnostics now reports the raw payload and the error of items that failed to decode - previously exactly the items you want to look at were the ones missing from it.

## Version 1.1.0
Stability and decoding fixes.

**Corrected values** - if you track these in statistics, the history before this version is wrong:
* `install_date` was decoded as a unix timestamp and reported a date in the 1970s. Command `0E00` is day / month / year, with the year big-endian. It is now a proper date sensor.
* `operating_days` read its counter little-endian and reported e.g. 2306 instead of 521 days.
* All sensors showed two decimals because the parameter was spelled `preciosion` instead of `precision`, so the configured precision never applied.
* `device_number` was a MEASUREMENT and was recorded as a statistic. It is an identifier now.
* The software version appended a replacement glyph when the firmware does not put a printable letter in the version bytes.
* A truncated answer from the device was decoded silently and produced a value off by orders of magnitude (e.g. 8.94 m3 instead of 1057.5 m3). Payloads are now length-checked and a bad answer makes the entity unavailable instead.

**Stability**
* Requests use aiohttp instead of blocking `requests` calls, share one session and are serialised with a lock, so a write no longer collides with a running scan.
* A scan stops at a time budget derived from the poll interval instead of being cancelled halfway through.
* Read errors raise `UpdateFailed`; an unreachable device raises `ConfigEntryNotReady` so HA retries instead of loading a broken integration.
* `logging.basicConfig()` no longer reconfigures the logging of the whole HA process.

**Multiple devices**
* The device postfix is now part of the unique ids and the device identifiers. Two config entries no longer overwrite each other's readings and no longer collapse into one device. Existing unique ids are migrated automatically.
* The config flow tests the connection, rejects a duplicate host and a postfix that is already in use.

**Entities**
* `operating_minutes`, `operating_hours` and `operating_days` were three sensors for three fields of one counter, so "operating hours" only ever showed the 0..23 remainder. They are replaced by a single `operating_time` sensor in hours (TOTAL_INCREASING). The three old entities are removed from the registry automatically on upgrade.

**Diagnostics**
* The raw payloads moved from the entity attributes into the diagnostics download (device page -> three dots -> "Download diagnostics"). In the attributes they changed on every scan, which wrote a new recorder row per entity per scan.

## Version 1.0.3
Added control for changing salt mass. The control shows the current salt mass. When refilling, the mass that was refilled has to be added to the shown mass.
