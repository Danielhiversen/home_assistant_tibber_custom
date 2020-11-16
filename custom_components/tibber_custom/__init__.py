"""Tibber custom"""
import datetime
import logging
from random import randint

import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from dateutil import tz
from homeassistant.const import EVENT_HOMEASSISTANT_START
from homeassistant.helpers import discovery
from homeassistant.util import dt as dt_util, slugify

DOMAIN = "tibber_custom"

DEPENDENCIES = ["tibber"]

_LOGGER = logging.getLogger(__name__)


def setup(hass, config):
    """Setup component."""
    matplotlib.use("Agg")

    cons_data = []

    async def ha_started(_):
        discovery.load_platform(hass, "camera", DOMAIN, {}, config)
        for home in hass.data["tibber"].get_homes(only_active=True):
            await _generate_fig(home)

    async def generate_fig(_):
        for home in hass.data["tibber"].get_homes(only_active=True):
            await _generate_fig(home)

    async def _generate_fig(home):
        name = home.info["viewer"]["home"]["appNickname"]
        if name is None:
            name = home.info["viewer"]["home"]["address"].get("address1", "")

        if home.has_real_time_consumption:
            realtime_state = hass.states.get(
                f"sensor.real_time_consumption_{slugify(name)}"
            )
        else:
            realtime_state = None

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
        fig = plt.figure(figsize=(1200 / 200, 700 / 200), dpi=200)
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

        if not realtime_state:
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
                print(_hour)
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

        ax.set_ylim((min(prices) - 0.005, max(prices) + 0.0075))
        ax.set_xlim((dates[0], dates[-1]))
        ax.set_facecolor("white")
        ax.xaxis.set_major_formatter(x_fmt)
        fig.autofmt_xdate()

        if realtime_state is not None:
            nonlocal cons_data
            hour_to_fetch = 24
            for hour in cons_data:
                print(hour)
                if hour.get("consumption") is None:
                    cons_data.remove(hour)
                    continue
                hour_to_fetch = (
                    now - dt_util.parse_datetime(hour.get("from"))
                ).seconds // 3600
            print("hour_to_fetch", hour_to_fetch)
            if hour_to_fetch > 2:
                for key in await home.get_historic_data(hour_to_fetch):
                    if key in cons_data:
                        continue
                    cons_data.append(key)
            print(cons_data)

            dates_cons = []
            cons = []
            total_cons = 0
            for hour in cons_data:
                date = dt_util.parse_datetime(hour.get("from")) + datetime.timedelta(
                    minutes=30
                )
                _cons = hour.get("consumption")
                if date < dates[0] or _cons is None:
                    continue
                dates_cons.append(date)
                total_cons += _cons
                cons.append(_cons)
                print(hour)

            ax2 = ax.twinx()
            ax2.grid(False)
            ax2.xaxis.set_major_formatter(x_fmt)
            # ax2.bar(dates_cons, cons, color='#039be5', width=0.065/2, edgecolor='#c3d5e8', alpha=0.25)
            ax2.vlines(
                x=dates_cons,
                ymin=0,
                ymax=cons,
                color="#039be5",
                edgecolor="#c3d5e8",
                alpha=0.6,
                linewidth=8,
            )

            acc_cons = realtime_state.attributes.get("accumulatedConsumption")
            print(realtime_state.attributes)
            if acc_cons:
                last_hour = None
                for hour in cons_data:
                    cons = hour.get("consumption")
                    if cons is None:
                        continue
                    last_hour = dt_util.parse_datetime(hour.get("from"))
                print(
                    "----------",
                    last_hour,
                    acc_cons - total_cons,
                    total_cons,
                    acc_cons,
                    (now - last_hour),
                )
                if (
                    last_hour is not None
                    and (now - last_hour).total_seconds() < 3600 * 2
                    and acc_cons - total_cons > 0
                ):
                    ax2.vlines(
                        [last_hour + datetime.timedelta(hours=1, minutes=30)],
                        0,
                        [acc_cons - total_cons],
                        color="#68A7C6",
                        linewidth=8,
                        edgecolor="#c3d5e8",
                        alpha=0.45,
                    )
                    # plt.plot([last_hour + datetime.timedelta(hours=1)], [acc_cons - total_cons], "o", markersize=5, color='#007acc', alpha=0.4)
                    # ax2.bar([last_hour + datetime.timedelta(hours=1)], [acc_cons - total_cons], color='#68A7C6', width=0.065/2, edgecolor='#c3d5e8', alpha=0.15)

        try:
            await hass.async_add_executor_job(fig.savefig(path, dpi=200))
        except Exception:  # noqa: E731
            pass
        plt.close(fig)
        plt.close("all")

    hass.helpers.event.async_track_time_change(
        generate_fig, minute=range(2, 59, 7), second=randint(0, 59)
    )
    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, ha_started)
    return True
