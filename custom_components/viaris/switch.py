"""Switches for viaris"""
from __future__ import annotations

from dataclasses import dataclass
import logging

from .const import (
    START_STOP_CONN1_KEY,
    START_STOP_CONN2_KEY,
    CONF_SERIAL_NUMBER,
)
from homeassistant.components.switch import SwitchEntityDescription, SwitchEntity
from homeassistant.helpers.entity import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant import config_entries
from homeassistant.components import mqtt
from .entity import ViarisEntity
from . import ViarisEntityDescription
from homeassistant.helpers.json import json_dumps

_LOGGER = logging.getLogger(__name__)


@dataclass
class ViarisSwitchEntityDescription(ViarisEntityDescription, SwitchEntityDescription):
    """Switch entity description for Viaris."""

    domain: str = "switch"
    optimistic: bool = True


SWITCHES: tuple[ViarisSwitchEntityDescription, ...] = (
    ViarisSwitchEntityDescription(
        key=START_STOP_CONN1_KEY,
        name="Start connector 1 charging",
        entity_category=EntityCategory.CONFIG,
        device_class=None,
        entity_registry_enabled_default=True,
        icon="mdi:flash",
        disabled=False,
    ),
    ViarisSwitchEntityDescription(
        key=START_STOP_CONN2_KEY,
        name="Start connector 2 charging",
        entity_category=EntityCategory.CONFIG,
        device_class=None,
        entity_registry_enabled_default=True,
        icon="mdi:flash",
        disabled=False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Config entry setup."""
    async_add_entities(
        ViarisSwitch(config_entry, description)
        for description in SWITCHES
        if not description.disabled
    )


class ViarisSwitch(ViarisEntity, SwitchEntity):
    """Representation of a Viaris switch."""

    entity_description: ViarisSwitchEntityDescription
    sensor_thread = None

    def __init__(
        self,
        config_entry: config_entries.ConfigEntry,
        description: ViarisSwitchEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(config_entry, description)

        self.entity_description = description
        self._optimistic = self.entity_description.optimistic
        if (
            self.entity_description.key == START_STOP_CONN1_KEY
            or self.entity_description.key == START_STOP_CONN2_KEY
        ):
            self._available = True
        self.serial_number = config_entry.data[CONF_SERIAL_NUMBER]

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    def set_available(self, value):
        """Set value"""
        self._available = value

    @property
    def assumed_state(self):
        """Return true if we do optimistic updates."""
        return self._optimistic

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        self.entity_description.payload_on = json_dumps(
            {
                "idTrans": 49685,
                "header": {"timestamp": 1665381726837, "heapFree": 0},
                "data": {
                    "uid": 1,
                    "source": "app",
                    "priority": 0,
                    "action": 1,
                    "user": "",
                    "group": 0,
                },
            }
        )
        if self.entity_description.key == START_STOP_CONN1_KEY:
            await mqtt.async_publish(
                self.hass,
                self._topic_startstop_conn1_pub,
                self.entity_description.payload_on,
            )
            _LOGGER.info(self._topic_startstop_conn1_pub)
            _LOGGER.info(self.entity_description.payload_on)

            if self._optimistic:
                # Optimistically assume that switch has changed state.
                self._attr_is_on = True
            self.async_write_ha_state()
        else:
            if self.entity_description.key == START_STOP_CONN2_KEY:
                await mqtt.async_publish(
                    self.hass,
                    self._topic_startstop_conn2_pub,
                    self.entity_description.payload_on,
                )
                _LOGGER.info(self._topic_startstop_conn2_pub)
                _LOGGER.info(self.entity_description.payload_on)

                if self._optimistic:
                    # Optimistically assume that switch has changed state.
                    self._attr_is_on = True
                self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        self.entity_description.payload_off = json_dumps(
            {
                "idTrans": 49685,
                "header": {"timestamp": 1665381726837, "heapFree": 0},
                "data": {
                    "uid": 1,
                    "source": "app",
                    "priority": 0,
                    "action": 0,
                    "user": "",
                    "group": 0,
                },
            }
        )
        if self.entity_description.key == START_STOP_CONN1_KEY:
            await mqtt.async_publish(
                self.hass,
                self._topic_startstop_conn1_pub,
                self.entity_description.payload_off,
            )
            _LOGGER.info(self._topic_startstop_conn1_pub)
            _LOGGER.info(self.entity_description.payload_off)

            if self._optimistic:
                # Optimistically assume that switch has changed state.
                self._attr_is_on = False
            self.async_write_ha_state()
        else:
            if self.entity_description.key == START_STOP_CONN2_KEY:
                await mqtt.async_publish(
                    self.hass,
                    self._topic_startstop_conn2_pub,
                    self.entity_description.payload_off,
                )
                _LOGGER.info(self._topic_startstop_conn2_pub)
                _LOGGER.info(self.entity_description.payload_off)

                if self._optimistic:
                    # Optimistically assume that switch has changed state.
                    self._attr_is_on = False
                self.async_write_ha_state()

    async def async_added_to_hass(self):
        self.async_write_ha_state()
