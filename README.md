<p align="center">
  <img src="https://raw.githubusercontent.com/stephanseitz/judo_rest_api/main/visuals/banner.png" alt="Judo REST API for Home Assistant – local control of JUDO water softeners" width="100%">
</p>

<p align="center">
  <a href="https://hacs.xyz/docs/faq/custom_repositories"><img src="https://img.shields.io/badge/HACS-Custom-41BDF5.svg" alt="HACS Custom"></a>
  <a href="https://github.com/stephanseitz/judo_rest_api/releases"><img src="https://img.shields.io/github/v/release/stephanseitz/judo_rest_api" alt="Release"></a>
  <a href="https://github.com/stephanseitz/judo_rest_api/actions/workflows/tests.yml"><img src="https://github.com/stephanseitz/judo_rest_api/actions/workflows/tests.yml/badge.svg" alt="Tests"></a>
  <img src="https://img.shields.io/badge/Home%20Assistant-2024.11%2B-blue" alt="Home Assistant 2024.11+">
</p>

Monitor and control a **Judo water softener** locally through the REST API of its [connectivity module](https://judo.eu/produkte/connectivity-modul-wlan/) – no cloud, no app needed.

Built on the [official command list](https://judo.eu/ftp-upload/download/REST-API/RESTAPI_Kommandos.pdf) and checked against a real **i-soft SAFE+** (device software 3.02).

---

## Contents
- [Supported devices](#supported-devices)
- [Entities](#entities)
- [Installation](#installation)
- [Configuration](#configuration)
- [Holiday mode and leakage settings](#holiday-mode-and-leakage-settings)
- [Upgrading from the original integration](#upgrading-from-the-original-integration)
- [Troubleshooting](#troubleshooting)
- [Credits](#credits)

---

## Supported devices

The device type is read at setup. Each device only gets the entities its own page of the API document lists – the same command does different things on different devices.

| Family | Device types | Status |
|---|---|---|
| **i-soft SAFE+**, i-soft K SAFE+ | `0x33` `0x57` `0x42` `0x67` | ✅ fully supported, tested on a device |
| **i-soft PRO**, PRO L | `0x58` `0x4B` `0x4C` | ✅ supported, incl. water scenes |
| i-soft, i-soft K, and softener types the document does not list | `0x32` `0x53` `0x43` `0x54` … | ☑️ supported according to the document |
| SOFTwell P / S / K / KP / KS | `0x34` `0x59` `0x35` `0x63` `0x36` `0x5A` `0x47` `0x62` `0x48` `0x64` | ☑️ counters and statistics only |
| ZEWA i-SAFE, i-dos, i-fill, unknown | – | ℹ️ device info only |

---

## Entities

| Entity | Type | SAFE+ | PRO | i-soft | SOFTwell |
|---|---|:-:|:-:|:-:|:-:|
| Water total / soft water | sensor | ✅ | ✅ | ✅ | soft only |
| Water consumption today (3-hour buckets as attributes) | sensor | ✅ | | ✅ | ✅ |
| Target water hardness | number | ✅ | ✅ | ✅ | |
| Hardness unit | select | ✅ | | ✅ | |
| Salt stock (kg), salt range (days), salt warning | number / sensor | ✅ | ✅ | ✅ | |
| Open / close leakage protection, start regeneration | button | ✅ | ✅ | ✅ | |
| Max. extraction duration / volume / flow rate | number ✍️ | ✅ | | | |
| Holiday mode (off / U1 / U2 / U3) | select ✍️ | ✅ | | | |
| Close on micro leakage, automatic micro leakage test, leakage protection globally off | switch ✍️ | ✅ | | | |
| Water scene and scene duration | select | | ✅ | | |
| Current flow, water temperature | sensor | | ✅ | | |
| Operating time, commissioning date, device number, software version, service contact | diagnostic | ✅ | ✅ | ✅ | partly |

✍️ = **write only.** The device accepts these settings but cannot report them. Home Assistant shows what was last set from here and keeps it across restarts; until then the entity is *unknown*.

---

## Installation

### HACS (recommended)
1. HACS → ⋮ → **Custom repositories**
2. Repository `https://github.com/stephanseitz/judo_rest_api`, type **Integration**
3. Download **Judo Rest API**, then restart Home Assistant
4. **Settings → Devices & services → Add integration → Judo Rest API**

### Manual
Copy `custom_components/judo_rest_api` into `<config>/custom_components/` and restart Home Assistant. Everything else in this repository (`tests/`, `tools/`) is not needed.

---

## Configuration

| Field | Default | Note |
|---|---|---|
| Host | – | IP address of the connectivity module |
| Port | `80` | only if changed on the module |
| User name | `admin` | factory setting of the module |
| Password | – | factory setting is `Connectivity` |
| Device postfix | *empty* | only for a second device; each entry needs its own. Cannot be changed later. |
| Poll interval | `60` s | minimum 10 s. The module serves one request at a time; shorter intervals cause timeouts. |

Host, port, credentials and poll interval can be changed later under **⋮ → Reconfigure**.

---

## Holiday mode and leakage settings

*i-soft SAFE+ only.* Holiday mode and the three leakage switches share **one byte** (command `41`), which the device cannot report. Sending one setting always sends all four, so nothing is sent until all four are known – otherwise switching on the holiday mode would silently reset the micro leakage settings made in the Judo app.

**One-time setup**
1. Set the three switches to match the Judo app (*Einstellungen → Kleinleckageprüfung*):
   - *Automatic micro leakage test* – off if *Automatische Kleinleckageprüfung* says "deaktiviert", otherwise on
   - *Close on micro leakage* – off if *Meldung bei Kleinleckage* says "Melden" (report only), on if it also closes
   - *Leakage protection globally off* – **off** as long as the app's status page says "Leckageschutz: aktiv"
2. Set *Holiday mode* to **Off**.

The first settings report *"saved, but not sent yet"*; the last one sends the byte. From then on every change is sent right away.

> ⚠️ *Leakage protection globally off* does exactly that. Leave it off unless you mean it.

---

## Upgrading from the original integration

Switching from [OStrama/judo_rest_api](https://github.com/OStrama/judo_rest_api) keeps the configuration and nearly all entities with their history (same domain). Remove the old repository in HACS before downloading this one, and make a backup first.

What changes:
- The three sensors *operating minutes / hours / days* become one **operating time** sensor.
- The commissioning date becomes a date without a time of day.
- Entities a device does not support are removed.
- Home Assistant may raise a repair about the statistics of the *device number* – it is an identifier, not a measurement; the repair can be dismissed.

Full release notes: [CHANGELOG.md](CHANGELOG.md).

---

## Troubleshooting

- **Diagnostics:** device page → ⋮ → *Download diagnostics* – shows every command with its raw answer and how it was decoded. Passwords are removed.
- **Debug log:**
  ```yaml
  logger:
    logs:
      custom_components.judo_rest_api: debug
  ```
- **Raw answers of a device:** `python3 tools/judo_rest_probe.py <ip> -p <password> --statistics` – read only, see [tools/README.md](tools/README.md).

Bugs and questions: [issues](https://github.com/stephanseitz/judo_rest_api/issues).

---

## Credits

Based on the work of [OStrama](https://github.com/OStrama/judo_rest_api) (original integration) and [ischraub](https://github.com/ischraub/judo_rest_api) (stability and decoding), with ideas from [siedi](https://github.com/siedi/ha_judo_rest_api), [zeroflow](https://github.com/zeroflow/judo_rest_api) and [Eddy-89](https://github.com/Eddy-89/judo_ksafe_era).

## Disclaimer

Not affiliated with JUDO Wasseraufbereitung GmbH. Built in spare time from publicly available information. Use at your own risk – the authors are not liable for any damage resulting from its use.
