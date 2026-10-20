"""Description of the items of the Judo REST API, per device family."""

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    UnitOfMass,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolume,
    UnitOfVolumeFlowRate,
)
from homeassistant.helpers.entity import EntityCategory

from .const import DEVICES, FAMILIES, FORMATS, TYPES
from .items import RestItem, StatusItem

################################################################################
# Listen mit Fehlermeldungen, Warnmeldungen und Statustexte
# Beschreibungstext ist ebenfalls möglich
# class StatusItem(): def __init__(self, number, text, description = None):
################################################################################

# fmt: off

# Hardness unit of commands 23 / 24, as listed on every softener page.
HARDNESS_UNIT: list[StatusItem] = [
    StatusItem(number=0, translation_key="unit_dh"),
    StatusItem(number=1, translation_key="unit_eh"),
    StatusItem(number=2, translation_key="unit_fh"),
    StatusItem(number=3, translation_key="unit_gpg"),
    StatusItem(number=4, translation_key="unit_ppm"),
    StatusItem(number=5, translation_key="unit_mmol"),
    StatusItem(number=6, translation_key="unit_mval"),
]

# Bits 0..3 of command 41 on the SAFE+: bit 0 "holiday mode active", then one
# bit each for U1, U2 and U3. The document's own example 410003 activates U1.
VACATION_MODE: list[StatusItem] = [
    StatusItem(number=0x00, translation_key="vacation_off"),
    StatusItem(number=0x03, translation_key="vacation_u1"),
    StatusItem(number=0x05, translation_key="vacation_u2"),
    StatusItem(number=0x09, translation_key="vacation_u3"),
]

UNIT_TYPE: list[StatusItem] = [
    StatusItem(number=0x32, translation_key="i_soft"),
    StatusItem(number=0x33, translation_key="i_soft_safe_plus"),
    StatusItem(number=0x34, translation_key="softwell_p"),
    StatusItem(number=0x35, translation_key="softwell_s"),
    StatusItem(number=0x36, translation_key="softwell_k"),
    StatusItem(number=0x37, translation_key="i_soft_tga"),
    StatusItem(number=0x38, translation_key="quicksoft_m"),
    StatusItem(number=0x39, translation_key="quicksoft_p"),
    StatusItem(number=0x3C, translation_key="i_fill"),
    StatusItem(number=0x3D, translation_key="i_dos_eco"),
    StatusItem(number=0x41, translation_key="i_dos_eco"),
    StatusItem(number=0x42, translation_key="i_soft_k_safe_plus"),
    StatusItem(number=0x43, translation_key="i_soft_k"),
    StatusItem(number=0x44, translation_key="zewa_prom_i_safe"),
    StatusItem(number=0x46, translation_key="quicksoft_cd"),
    StatusItem(number=0x47, translation_key="softwell_kp"),
    StatusItem(number=0x48, translation_key="softwell_ks"),
    StatusItem(number=0x49, translation_key="optiline_z"),
    StatusItem(number=0x4A, translation_key="optiline_e"),
    StatusItem(number=0x4B, translation_key="i_soft_pro_s"),
    StatusItem(number=0x4C, translation_key="i_soft_pro_l"),
    StatusItem(number=0x4D, translation_key="quicksoft_mp"),
    StatusItem(number=0x4E, translation_key="i_soft_c_safe"),
    StatusItem(number=0x4F, translation_key="i_soft_c"),
    StatusItem(number=0x50, translation_key="i_soft_k"),
    StatusItem(number=0x51, translation_key="i_soft_k_safe_plus"),
    StatusItem(number=0x52, translation_key="softwell_kp"),
    StatusItem(number=0x53, translation_key="i_soft"),
    StatusItem(number=0x54, translation_key="i_soft_k"),
    StatusItem(number=0x55, translation_key="i_soft_tga"),
    StatusItem(number=0x56, translation_key="i_soft_safe"),
    StatusItem(number=0x57, translation_key="i_soft_safe_plus"),
    StatusItem(number=0x58, translation_key="i_soft_pro"),
    StatusItem(number=0x59, translation_key="softwell_p"),
    StatusItem(number=0x5A, translation_key="softwell_k"),
    StatusItem(number=0x5B, translation_key="quicksoft_m"),
    StatusItem(number=0x5C, translation_key="quicksoft_p"),
    StatusItem(number=0x5D, translation_key="scansoft_m"),
    StatusItem(number=0x5E, translation_key="scansoft_p"),
    StatusItem(number=0x5F, translation_key="finesky_whs_c"),
    StatusItem(number=0x60, translation_key="finesky_whs_p"),
    StatusItem(number=0x61, translation_key="quicksoft_cd"),
    StatusItem(number=0x62, translation_key="softwell_kp"),
    StatusItem(number=0x63, translation_key="softwell_s"),
    StatusItem(number=0x64, translation_key="softwell_ks"),
    StatusItem(number=0x65, translation_key="optiline_z"),
    StatusItem(number=0x66, translation_key="optiline_e"),
    StatusItem(number=0x67, translation_key="i_soft_k_safe_plus"),
    StatusItem(number=0x68, translation_key="zewa_prom_i_safe"),
    StatusItem(number=0x6A, translation_key="aqua_tenera_e"),
    StatusItem(number=0x6B, translation_key="aqua_tenera_d"),
]

SALT_MASS: list[StatusItem] = [
    StatusItem(number=0, translation_key="mass_0kg"),
    StatusItem(number=1, translation_key="mass_1kg"),
    StatusItem(number=5, translation_key="mass_5kg"),
    StatusItem(number=10, translation_key="mass_10kg"),
    StatusItem(number=15, translation_key="mass_15kg"),
    StatusItem(number=20, translation_key="mass_20kg"),
    StatusItem(number=25, translation_key="mass_25kg"),
    StatusItem(number=50, translation_key="mass_50kg"),
]
# Water scenes of the i-soft PRO family (device types 0x58, 0x4b, 0x4c).
# Numbering is 0-based on the wire, confirmed by reading every scene back from
# a device: scene 3 is the only one answering with a date block, which the API
# document assigns to "Urlaub geniessen", and the hardness of each scene
# matches its name (0 dH for the heating system, bypass for garden and pool).
SCENE_LIST: list[StatusItem] = [
    StatusItem(number=0x00, translation_key="scene_everyday"),
    StatusItem(number=0x01, translation_key="scene_body_care"),
    StatusItem(number=0x02, translation_key="scene_garden"),
    StatusItem(number=0x03, translation_key="scene_holiday"),
    StatusItem(number=0x04, translation_key="scene_laundry"),
    StatusItem(number=0x05, translation_key="scene_pressure_washing"),
    StatusItem(number=0x06, translation_key="scene_pool"),
    StatusItem(number=0x07, translation_key="scene_heating"),
    StatusItem(number=0x08, translation_key="scene_custom_1"),
    StatusItem(number=0x09, translation_key="scene_custom_2"),
    StatusItem(number=0x0A, translation_key="scene_custom_3"),
]

# Durations command 36 accepts, as listed in the API document. The two bytes
# are hours and minutes and go on the wire unchanged, not little-endian.
SCENE_DURATION_LIST: list[StatusItem] = [
    StatusItem(number=0x000F, translation_key="duration_15_min"),
    StatusItem(number=0x001E, translation_key="duration_30_min"),
    StatusItem(number=0x002D, translation_key="duration_45_min"),
    StatusItem(number=0x0100, translation_key="duration_1_h"),
    StatusItem(number=0x0200, translation_key="duration_2_h"),
    StatusItem(number=0x0600, translation_key="duration_6_h"),
    StatusItem(number=0x0C00, translation_key="duration_12_h"),
    StatusItem(number=0xFFFF, translation_key="duration_unlimited"),
]

#####################################################
# Description of physical units via the status list #
#####################################################

PARAMS_FLOWRATE: dict = {
    "min": 0,
    "max": 5,
    "step": 0.1,
    "divider": 100,
    "precision": 2,
    "unit": UnitOfVolumeFlowRate.LITERS_PER_MINUTE,
    "stateclass": SensorStateClass.MEASUREMENT,
}

PARAMS_MASS: dict = {
    "min": 0,
    "max": 100,
    "step": 1,
    "divider": 1000,
    "precision": 2,
    "unit": UnitOfMass.KILOGRAMS,
    "stateclass": SensorStateClass.MEASUREMENT,
    "icon": "mdi:weight-kilogram"
}

PARAMS_DAYS: dict = {
    "min": 1,
    "max": 65535,
    "step": 1,
    "precision": 0,
    "unit": UnitOfTime.DAYS,
    "stateclass": SensorStateClass.MEASUREMENT,
    "icon": "mdi:timelapse"
}

# The device reports minutes, hours and days of its operating time as three
# separate fields of one counter. Split into three sensors they were
# misleading: "operating hours" only ever showed the 0..23 remainder.
PARAMS_OPERATING_TIME: dict = {
    "precision": 2,
    "unit": UnitOfTime.HOURS,
    "stateclass": SensorStateClass.TOTAL_INCREASING,
    "deviceclass": SensorDeviceClass.DURATION,
    "icon": "mdi:timelapse",
    # The counter advances by 1/60 h every minute, so at a 60 s scan interval
    # every single scan was a state change: ~1440 recorder rows a day for a
    # number that is only interesting to the hour. One hour cuts that to ~23.
    "deadband": 1.0,
}

PARAMS_GDH: dict = {
    "min": 1,
    "max": 18,
    "step": 1,
    "precision": 0,
    "unit": "°dH",
    "divider": 1,
    "stateclass": SensorStateClass.MEASUREMENT,
    "icon": "mdi:water-opacity"
}

PARAMS_QBM_H: dict = {
    "min": 0,
    "max": 100,
    "step": 1,
    "divider": 1000,
    "precision": 3,
    "unit": UnitOfVolume.CUBIC_METERS,
    "stateclass": SensorStateClass.TOTAL_INCREASING,
    "deviceclass": SensorDeviceClass.WATER,
    "icon": "mdi:water"
}

PARAMS_QBM_W: dict = {
    "min": 0,
    "max": 100,
    "step": 1,
    "divider": 1000,
    "precision": 3,
    "unit": UnitOfVolume.CUBIC_METERS,
    "stateclass": SensorStateClass.TOTAL_INCREASING,
    "deviceclass": SensorDeviceClass.WATER,
    "icon": "mdi:water-outline"
}


PARAMS_CONTACT: dict = {
    "icon": "mdi:phone"
}

PARAMS_CLOSE: dict = {
    "icon": "mdi:water-pump-off"
}
PARAMS_OPEN: dict = {
    "icon": "mdi:water-pump"
}

PARAMS_REG: dict = {
    "icon": "mdi:water-check-outline"
}

PARAMS_INFO: dict = {
    "icon": "mdi:information-box-outline"
}

PARAMS_FLOW: dict = {
    "precision": 0,
    "unit": "L/h",
    "stateclass": SensorStateClass.MEASUREMENT,
    "icon": "mdi:water-pump",
}

PARAMS_TEMPERATURE: dict = {
    "precision": 0,
    "unit": UnitOfTemperature.CELSIUS,
    "deviceclass": SensorDeviceClass.TEMPERATURE,
    "stateclass": SensorStateClass.MEASUREMENT,
}

PARAMS_SCENE: dict = {
    "icon": "mdi:water-sync",
    # Which item holds the duration to send along with the scene.
    "duration_item": "water_scene_duration",
}

PARAMS_SCENE_DURATION: dict = {
    "icon": "mdi:timer-sand",
    # Used until the user picks one; two hours rather than "unlimited", which
    # would leave a bypass scene running with leakage protection off.
    "default": "duration_2_h",
}

# A serial number must not be a MEASUREMENT: it would be recorded as a
# statistic and was rendered as "2.825.589.796,00".
PARAMS_SERIAL: dict = {
    "icon": "mdi:identifier",
    "precision": 0,
    "stateclass": None,
}

PARAMS_DATE: dict = {
    "icon": "mdi:calendar-check",
    "deviceclass": SensorDeviceClass.DATE,
    "stateclass": None,
}

PARAMS_MASS_REFILL: dict = {
    "icon": "mdi:weight-kilogram",
    "min": 0,
    "max": 50,
    "step": 0.05,
    "divider": 1000,
    "precision": 3,
    "unit": UnitOfMass.KILOGRAMS,
    "stateclass": SensorStateClass.MEASUREMENT,
    # The scale wobbles by a gram or two at rest, which produced a state change
    # on every scan. Report only once it moved by at least 50 g - the step this
    # entity can be set in anyway, and far below what one regeneration uses.
    "deadband": 0.05,
}
# The SAFE+ answers 3E, 3F, 40 and 41 with an empty payload: they can be
# written, not read. What these entities show is what was last written from
# Home Assistant, restored across restarts, and unknown until then.
PARAMS_MAX_DURATION: dict = {
    "min": 0,
    "max": 255,
    "step": 1,
    "precision": 0,
    "unit": UnitOfTime.MINUTES,
    "stateclass": None,
    "icon": "mdi:timer-alert-outline",
    "mode": "box",
}

# The SAFE+ page labels 3F "Max. Entnahmemenge" and 40 "Max. Volumenstrom",
# but its descriptions and examples have the two the other way round. The
# labels agree with the i-soft PRO page, whose descriptions match them (3F in
# litres, 40 in l/h), and with the ZEWA page, where "Volumenstrom" is always
# l/h and "Entnahmemenge" always litres. So the labels are taken as right.
PARAMS_MAX_VOLUME: dict = {
    "min": 0,
    "max": 65535,
    "step": 1,
    "precision": 0,
    "unit": UnitOfVolume.LITERS,
    "stateclass": None,
    "icon": "mdi:water-alert-outline",
    "mode": "box",
}

PARAMS_MAX_FLOW: dict = {
    "min": 0,
    "max": 65535,
    "step": 1,
    "precision": 0,
    "unit": UnitOfVolumeFlowRate.LITERS_PER_HOUR,
    "stateclass": None,
    "icon": "mdi:water-pump",
    "mode": "box",
}

PARAMS_HARDNESS_UNIT: dict = {
    "icon": "mdi:water-opacity",
}

# Command 41 carries the holiday mode and three leakage settings in one byte.
# It cannot be read back, so writing one of them means writing all of them:
# each entity names the byte and the bits it owns, and the byte is assembled
# from all of them. Until every part is known nothing is sent, so a holiday
# mode switched on from here can never silently reset the micro leakage
# settings made in the app.
PARAMS_VACATION: dict = {
    "icon": "mdi:beach",
    "bitfield": "leakage_settings",
    "mask": 0x0F,
}

PARAMS_MICRO_LEAKAGE_CLOSE: dict = {
    "icon": "mdi:pipe-valve",
    "bitfield": "leakage_settings",
    "mask": 0x20,
}

PARAMS_MICRO_LEAKAGE_TEST: dict = {
    "icon": "mdi:water-check",
    "bitfield": "leakage_settings",
    "mask": 0x40,
}

PARAMS_LEAKAGE_PROTECTION_OFF: dict = {
    "icon": "mdi:shield-off-outline",
    "bitfield": "leakage_settings",
    "mask": 0x80,
}

PARAMS_WATER_TODAY: dict = {
    "precision": 0,
    "unit": UnitOfVolume.LITERS,
    # Resets at midnight; HA reads a drop of a TOTAL_INCREASING value as a new
    # cycle.
    "stateclass": SensorStateClass.TOTAL_INCREASING,
    "deviceclass": SensorDeviceClass.WATER,
    "icon": "mdi:water-outline",
    # The day only moves in 3-hour buckets that fill up slowly; there is no
    # point in asking for it on every scan.
    "poll_interval": 300,
}

# Which family serves which item. See FamilyConstants in const.py.
SOFTENERS = frozenset({FAMILIES.I_SOFT, FAMILIES.SAFE_PLUS, FAMILIES.PRO})
# i-soft and SAFE+ pages: little-endian counters, commissioning date as unix
# time, statistics in fixed 3-hour buckets.
CLASSIC = frozenset({FAMILIES.I_SOFT, FAMILIES.SAFE_PLUS})
# SOFTwell knows the counters and the statistics, but no salt, no hardness and
# none of the controls.
WITH_COUNTERS = CLASSIC | {FAMILIES.SOFTWELL}
NOT_PRO = frozenset({FAMILIES.I_SOFT, FAMILIES.SAFE_PLUS, FAMILIES.SOFTWELL, FAMILIES.OTHER})
PRO = frozenset({FAMILIES.PRO})
SAFE_PLUS = frozenset({FAMILIES.SAFE_PLUS})

# pylint: disable=line-too-long

# fmt: off
REST_SYS_ITEMS: list[RestItem] = [
    RestItem( address_read="FF00", read_bytes = 1, read_index=0, mformat=FORMATS.STATUS, mtype=TYPES.SENSOR, device=DEVICES.SYS, resultlist=UNIT_TYPE, params=PARAMS_INFO, translation_key="device_type", entity_category=EntityCategory.DIAGNOSTIC),
    # Byte order differs by family: the PRO page's example only works
    # big-endian, every other page's only little-endian. Confirmed on an
    # i-soft PRO (big) and an i-soft SAFE+ on 3.02 (little, 205703 as in the app).
    RestItem( address_read="0600", read_bytes = 4, read_index=0, read_endian="big", mformat=FORMATS.SERIAL, mtype=TYPES.SENSOR, device=DEVICES.SYS, params=PARAMS_SERIAL, translation_key="device_number", entity_category=EntityCategory.DIAGNOSTIC, families=PRO),
    RestItem( address_read="0600", read_bytes = 4, read_index=0, mformat=FORMATS.SERIAL, mtype=TYPES.SENSOR, device=DEVICES.SYS, params=PARAMS_SERIAL, translation_key="device_number", entity_category=EntityCategory.DIAGNOSTIC, families=NOT_PRO),
    RestItem( address_read="0100", read_bytes = 3, read_index=0, mformat=FORMATS.SW_VERSION, mtype=TYPES.SENSOR, device=DEVICES.SYS, params=PARAMS_INFO, translation_key="software_version", entity_category=EntityCategory.DIAGNOSTIC),

    RestItem( address_read="5100", read_bytes = 2, read_index=0, address_write="3000", write_bytes = 1, write_index=0, mformat=FORMATS.NUMBER, mtype=TYPES.NUMBER, device=DEVICES.SYS, params=PARAMS_GDH,translation_key="water_hardeness", families=SOFTENERS),
    RestItem( address_read="5700", read_bytes = 1, read_index=0, address_write="5700", write_bytes = 1, write_index=0, mformat=FORMATS.NUMBER, mtype=TYPES.NUMBER, device=DEVICES.SYS, params=PARAMS_DAYS,translation_key="salt_warning", entity_category=EntityCategory.CONFIG, families=SOFTENERS),

#   RestItem( address_read="5600", read_bytes = 2, read_index=0, mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.SYS, params= PARAMS_MASS, translation_key="salt_storage_mass"),
    RestItem( address_read="5600", read_bytes = 2, read_index=0, address_write="5600", write_bytes = 2, write_index=0, mformat=FORMATS.NUMBER, mtype=TYPES.NUMBER, device=DEVICES.SYS, params=PARAMS_MASS_REFILL, translation_key="salt_storage_mass", entity_category=EntityCategory.CONFIG, families=SOFTENERS),
    RestItem( address_read="5600", read_bytes = 2, read_index=2, mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.SYS, params=PARAMS_DAYS, translation_key="salt_storage_days", families=SOFTENERS),

    RestItem( address_read="2800", read_bytes = 4, read_index=0, mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.SYS, params=PARAMS_QBM_H, translation_key="water_total", families=SOFTENERS),
    RestItem( address_read="2900", read_bytes = 4, read_index=0, mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.SYS, params=PARAMS_QBM_W, translation_key="water_treated", families=SOFTENERS | WITH_COUNTERS),

    RestItem( address_read="5800", read_bytes = 16, read_index=0, mformat=FORMATS.TEXT, mtype=TYPES.SENSOR, device=DEVICES.SYS, params=PARAMS_CONTACT, translation_key="service_contact", entity_category=EntityCategory.DIAGNOSTIC, families=SOFTENERS),
    # The day counter is big-endian on the PRO and little-endian elsewhere: an
    # i-soft SAFE+ reports 2102 days little-endian, exactly the days since the
    # commissioning date it reports itself.
    RestItem( address_read="2500", read_bytes = 4, read_index=0, read_endian="big", mformat=FORMATS.DURATION, mtype=TYPES.SENSOR, device=DEVICES.SYS, params=PARAMS_OPERATING_TIME, translation_key="operating_time", entity_category=EntityCategory.DIAGNOSTIC, families=PRO),
    RestItem( address_read="2500", read_bytes = 4, read_index=0, mformat=FORMATS.DURATION, mtype=TYPES.SENSOR, device=DEVICES.SYS, params=PARAMS_OPERATING_TIME, translation_key="operating_time", entity_category=EntityCategory.DIAGNOSTIC, families=WITH_COUNTERS),
    # Day, month, year on the PRO; unix time on the SAFE+, which only the
    # original integration's reading of it as a timestamp gets right.
    RestItem( address_read="0E00", read_bytes = 4, read_index=0, mformat=FORMATS.DATE, mtype=TYPES.SENSOR, device=DEVICES.SYS, params=PARAMS_DATE, translation_key="install_date", entity_category=EntityCategory.DIAGNOSTIC, families=PRO),
    RestItem( address_read="0E00", read_bytes = 4, read_index=0, mformat=FORMATS.TIMESTAMP_DATE, mtype=TYPES.SENSOR, device=DEVICES.SYS, params=PARAMS_DATE, translation_key="install_date", entity_category=EntityCategory.DIAGNOSTIC, families=WITH_COUNTERS),

    RestItem( address_read="FB00", read_bytes = 32, read_index=0, mformat=FORMATS.DAY_STATISTICS, mtype=TYPES.SENSOR, device=DEVICES.SYS, params=PARAMS_WATER_TODAY, translation_key="water_today", families=WITH_COUNTERS),

    RestItem(address_write="3C00", write_bytes = 0, write_index=0, mformat=FORMATS.BUTTON, mtype=TYPES.BUTTON, device=DEVICES.SYS, params=PARAMS_CLOSE, translation_key="leakage_protection_close", families=SOFTENERS),
    RestItem(address_write="3D00", write_bytes = 0, write_index=0, mformat=FORMATS.BUTTON, mtype=TYPES.BUTTON, device=DEVICES.SYS, params=PARAMS_OPEN, translation_key="leakage_protection_open", families=SOFTENERS),
    RestItem(address_write="350000", write_bytes = 0, write_index=0, mformat=FORMATS.BUTTON, mtype=TYPES.BUTTON, device=DEVICES.SYS, params=PARAMS_REG, translation_key="start_regeneration", families=SOFTENERS),

    RestItem( address_read="2300", read_bytes = 1, read_index=0, address_write="2400", write_bytes = 1, write_index=0, mformat=FORMATS.STATUS, mtype=TYPES.SELECT, device=DEVICES.SYS, resultlist=HARDNESS_UNIT, params=PARAMS_HARDNESS_UNIT, translation_key="hardness_unit", entity_category=EntityCategory.CONFIG, families=CLASSIC),

    RestItem(address_write="3E00", write_bytes = 1, write_index=0, mformat=FORMATS.NUMBER, mtype=TYPES.NUMBER, device=DEVICES.SYS, params=PARAMS_MAX_DURATION, translation_key="max_extraction_duration", entity_category=EntityCategory.CONFIG, families=SAFE_PLUS),
    RestItem(address_write="3F00", write_bytes = 2, write_index=0, mformat=FORMATS.NUMBER, mtype=TYPES.NUMBER, device=DEVICES.SYS, params=PARAMS_MAX_VOLUME, translation_key="max_extraction_volume", entity_category=EntityCategory.CONFIG, families=SAFE_PLUS),
    RestItem(address_write="4000", write_bytes = 2, write_index=0, mformat=FORMATS.NUMBER, mtype=TYPES.NUMBER, device=DEVICES.SYS, params=PARAMS_MAX_FLOW, translation_key="max_flow_rate", entity_category=EntityCategory.CONFIG, families=SAFE_PLUS),

    RestItem(address_write="4100", write_bytes = 1, write_index=0, mformat=FORMATS.STATUS, mtype=TYPES.BITFIELD_SELECT, device=DEVICES.SYS, resultlist=VACATION_MODE, params=PARAMS_VACATION, translation_key="vacation_mode", families=SAFE_PLUS),
    RestItem(address_write="4100", write_bytes = 1, write_index=0, mformat=FORMATS.STATUS, mtype=TYPES.BITFIELD_SWITCH, device=DEVICES.SYS, params=PARAMS_MICRO_LEAKAGE_CLOSE, translation_key="micro_leakage_close", entity_category=EntityCategory.CONFIG, families=SAFE_PLUS),
    RestItem(address_write="4100", write_bytes = 1, write_index=0, mformat=FORMATS.STATUS, mtype=TYPES.BITFIELD_SWITCH, device=DEVICES.SYS, params=PARAMS_MICRO_LEAKAGE_TEST, translation_key="micro_leakage_auto_test", entity_category=EntityCategory.CONFIG, families=SAFE_PLUS),
    RestItem(address_write="4100", write_bytes = 1, write_index=0, mformat=FORMATS.STATUS, mtype=TYPES.BITFIELD_SWITCH, device=DEVICES.SYS, params=PARAMS_LEAKAGE_PROTECTION_OFF, translation_key="leakage_protection_off", entity_category=EntityCategory.CONFIG, families=SAFE_PLUS),

    # Water scenes and command 69 exist on the PRO family only. The SAFE+ app
    # shows scenes too, but the device answers 6900 and 3700xx with 400.
    RestItem(address_read="6900", read_bytes = 1, read_index=0, address_write="3600", write_bytes = 3, write_index=0, mformat=FORMATS.SCENE, mtype=TYPES.SCENE, device=DEVICES.SYS, resultlist=SCENE_LIST, params=PARAMS_SCENE, translation_key="water_scene", families=PRO),
    # All of these come out of one 6900 answer, which the coordinator fetches
    # once per scan. Command 69 needs device software newer than 1.5.31.
    RestItem( address_read="6900", read_bytes = 2, read_index=4, mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.SYS, params=PARAMS_FLOW, translation_key="water_flow", families=PRO),
    RestItem( address_read="6900", read_bytes = 2, read_index=10, mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.SYS, params=PARAMS_TEMPERATURE, translation_key="water_temperature", families=PRO),

    RestItem(mformat=FORMATS.SCENE_DURATION, mtype=TYPES.SELECT_LOCAL, device=DEVICES.SYS, resultlist=SCENE_DURATION_LIST, params=PARAMS_SCENE_DURATION, translation_key="water_scene_duration", families=PRO),

#    RestItem(address_read="5600", read_bytes = 2, read_index=0,address_write="5600", write_bytes = 2, write_index=0, mformat=FORMATS.STATUS, mtype=TYPES.SELECT_NOIF, device=DEVICES.SYS, params= PARAMS_MASS_REFILL, resultlist=SALT_MASS, translation_key="salt_refill_mass"),
]

#REST_ST_ITEMS: list[RestItem] = [
    #RestItem( address_read="FB00", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.ST, params=PARAMS_QBM_H, translation_key="day_statistics"),
#]

DEVICELISTS: list = [
    REST_SYS_ITEMS,
    #REST_ST_ITEMS,
]

# fmt: on
