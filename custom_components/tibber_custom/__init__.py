"""Tibber custom"""
import datetime
import logging

import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from dateutil import tz
from homeassistant.const import EVENT_HOMEASSISTANT_START
from homeassistant.helpers import discovery
from homeassistant.util import dt as dt_util

DOMAIN = "tibber_custom"

DEPENDENCIES = ["tibber"]

_LOGGER = logging.getLogger(__name__)


def setup(hass, config):
    """Setup component."""
    matplotlib.use("Agg")

    def ha_started(_):
        discovery.load_platform(hass, "camera", DOMAIN, {}, config)
        for home in hass.data["tibber"].get_homes(only_active=True):
            _generate_fig(home)

    def generate_fig(_):
        for home in hass.data["tibber"].get_homes(only_active=True):
            _generate_fig(home)

    def _generate_fig(home):
        name = home.info["viewer"]["home"]["appNickname"]
        if name is None:
            name = home.info["viewer"]["home"]["address"].get("address1", "")
        path = hass.config.path(f"www/prices_{name}.png")

        prices = []
        dates = []
        now = dt_util.now()
        for key, price_total in home.price_total.items():
            key = dt_util.as_local(dt_util.parse_datetime(key))
            if key.date() < now.date():
                continue
            prices.append(price_total)
            dates.append(key)

        if len(prices) < 10:
            return

        now = dt_util.now()
        hour = now.hour
        dt = datetime.timedelta(minutes=now.minute)

        plt.close("all")
        plt.style.use("ggplot")
        x_fmt = mdates.DateFormatter("%H", tz=tz.gettz("Europe/Berlin"))
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.grid(which="major", axis="x", linestyle="-", color="gray", alpha=0.25)
        plt.tick_params(
            axis="both",
            which="both",
            bottom=False,
            top=False,
            labelbottom=True,
            left=False,
            right=False,
            labelleft=True,
        )
        ax.plot(
            [dates[hour] + dt, dates[hour] + dt],
            [min(prices) - 3, max(prices) + 3],
            "r",
            alpha=0.35,
            linestyle="-",
        )
        ax.plot(dates, prices, "#039be5")

        ax.fill_between(dates, 0, prices, facecolor="#039be5", alpha=0.25)
        plt.text(
            dates[hour] + dt,
            prices[hour],
            "{:.2f}".format(prices[hour]) + home.currency,
            fontsize=14,
        )
        min_length = 7 if len(dates) > 24 else 5
        last_hour = -1 * min_length
        for _hour in range(1, len(prices) - 1):
            if abs(_hour - last_hour) < min_length or abs(_hour - hour) < min_length:
                continue
            if (prices[_hour - 1] > prices[_hour] < prices[_hour + 1]) or (
                prices[_hour - 1] < prices[_hour] > prices[_hour + 1]
            ):
                last_hour = _hour
                plt.text(
                    dates[_hour],
                    prices[_hour],
                    str(round(prices[_hour], 2))
                    + home.currency
                    + "\nat {:02}:00".format(_hour % 24),
                    fontsize=10,
                    va="bottom",
                )

        ax.set_xlim(
            (
                dates[0] - datetime.timedelta(minutes=3),
                dates[-1] + datetime.timedelta(minutes=3),
            )
        )
        ax.set_ylim((min(prices) - 0.005, max(prices) + 0.005))
        ax.set_facecolor("white")
        ax.xaxis.set_major_formatter(x_fmt)
        fig.autofmt_xdate()
        try:
            fig.savefig(path)
        except Exception:  # noqa: E731
            pass
        plt.close(fig)
        plt.close("all")

    hass.helpers.event.track_time_change(
        generate_fig, minute=[0, 11, 21, 31, 41, 51], second=15
    )
    hass.bus.listen_once(EVENT_HOMEASSISTANT_START, ha_started)
    return True
