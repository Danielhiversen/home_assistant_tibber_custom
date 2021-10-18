import datetime
import logging
from pathlib import Path

import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from dateutil import tz
from homeassistant.components.local_file.camera import LocalFile
from homeassistant.util import dt as dt_util, slugify

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    Path(hass.config.path("www/")).mkdir(parents=True, exist_ok=True)

    dev = []
    for home in hass.data["tibber"].get_homes(only_active=True):
        dev.append(TibberCam(home, hass))
    async_add_entities(dev)


class TibberCam(LocalFile):
    def __init__(self, home, hass):
        matplotlib.use("Agg")

        self._name = home.info["viewer"]["home"]["appNickname"]
        if self._name is None:
            self._name = home.info["viewer"]["home"]["address"].get("address1", "")
        self._path = hass.config.path(f"www/prices_{self._name}.png")
        self._home = home
        self.hass = hass
        self._cons_data = []
        self._last_update = dt_util.now() - datetime.timedelta(hours=1)
        self.realtime_state = None
        # hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, self._generate_fig)

        super().__init__(self._name, self._path)

    async def async_camera_image(self):
        """Return bytes of camera image."""
        await self._generate_fig()
        return await self.hass.async_add_executor_job(self.camera_image)

    async def _generate_fig(self):
        if (dt_util.now() - self._last_update) < datetime.timedelta(minutes=1):
            return

        if (self._home.last_data_timestamp - dt_util.now()).total_seconds() > 11 * 3600:
            await self._home.update_info_and_price_info()

        self._last_update = dt_util.now()
        if self._home.has_real_time_consumption:
            self.realtime_state = self.hass.states.get(
                f"sensor.real_time_consumption_{slugify(self._name)}"
            )
            if self.realtime_state is None:
                self.realtime_state = self.hass.states.get(
                    f"sensor.power_{slugify(self._name)}"
                )
        else:
            self.realtime_state = None

        prices = []
        dates = []
        now = dt_util.now()
        for key, price_total in self._home.price_total.items():
            key = dt_util.as_local(dt_util.parse_datetime(key))
            if key.date() < now.date():
                continue
            prices.append(price_total)
            dates.append(key)

        if len(prices) < 10:
            _LOGGER.warning("No prices")
            return

        now = dt_util.now()
        hour = now.hour
        dt = datetime.timedelta(minutes=now.minute)

        # Dark Colors
        fig_facecolor = "#1e1e1e"
        ax_facecolor = "#1e1e1e"
        ax_grid_x = "gray"
        ax_grid_y = "gray"
        ax_plot_price = "#386994"
        ax_fill_prices = "#039be5"
        plt_price_now_high_color = "red"
        plt_price_now_low_color = "green"
        plt_price_high_low_color = "white"
        plt_tick_color = "#7c7c7c"

        plt.close("all")
        plt.style.use("ggplot")
        x_fmt = mdates.DateFormatter("%H", tz=tz.gettz("Europe/Berlin"))
        fig = plt.figure(figsize=(1200 / 200, 700 / 200), dpi=200, facecolor=fig_facecolor)
        ax = fig.add_subplot(111, frameon=False, facecolor=ax_facecolor)

        ax.grid(which="major", axis="x", linestyle="-", color=ax_grid_x, alpha=0.25)
        ax.grid(which="major", axis="y", linestyle="-", color=ax_grid_y, alpha=0.25)

        plt.tick_params(
            axis="both",
            which="both",
            bottom=False,
            top=False,
            labelbottom=True,
            left=False,
            right=False,
            labelleft=True,
            color=plt_tick_color
        )

        # Set color on current line and text depending on price-level
        if (prices[hour]>1):
            now_color=plt_price_now_high_color
        else:
            now_color=plt_price_now_low_color

        ax.plot(
            [dates[hour] + dt, dates[hour] + dt],
            [min(prices) - 3, max(prices) + 3],
            now_color,
            alpha=0.75,
            linestyle="-",
            zorder=3,
        )

        plt.text(
            dates[hour] + dt,
            prices[hour],
            "{:.2f}".format(prices[hour]) + self._home.currency,
            fontsize=14,
            zorder=3,
            color=now_color
        )

        # Draw price curve and fill in if no consumption is present
        ax.plot(dates, prices, ax_plot_price)

        if not self.realtime_state:
            ax.fill_between(dates, 0, prices, facecolor=ax_fill_prices, alpha=0.25)

        
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
                    + self._home.currency
                    + "\nat {:02}:00".format(_hour % 24),
                    fontsize=10,
                    va="bottom",
                    zorder=3,
                    color=plt_price_high_low_color
                )

        ax.set_ylim((min(prices) - 0.08, max(prices) + 0.08))
        ax.set_xlim((dates[0], dates[-1]))
        ax.set_facecolor(ax_facecolor)
        ax.xaxis.set_major_formatter(x_fmt)
        fig.autofmt_xdate()

        if self.realtime_state is not None:
            hour_to_fetch = 24
            for _hour in self._cons_data:
                if _hour.get("consumption") is None:
                    self._cons_data.remove(_hour)
                    continue
                hour_to_fetch = (
                    now - dt_util.parse_datetime(_hour.get("from"))
                ).total_seconds() / 3600
            if hour_to_fetch > 2:
                cons_data = await self._home.get_historic_data(int(hour_to_fetch))
                cons_data = [] if cons_data is None else cons_data
                for key in cons_data:
                    if key in self._cons_data:
                        continue
                    self._cons_data.append(key)
            dates_cons = []
            cons = []
            for _hour in self._cons_data:
                _cons = _hour.get("consumption")
                if _cons is None:
                    continue

                date = dt_util.parse_datetime(_hour.get("from")) + datetime.timedelta(
                    minutes=30
                )
                if date < dates[0]:
                    continue
                dates_cons.append(date)
                cons.append(_cons)
            ax2 = ax.twinx()
            ax2.grid(False)
            ax2.xaxis.set_major_formatter(x_fmt)
            ax2.vlines(
                x=dates_cons,
                ymin=0,
                ymax=cons,
                color="#039be5",
                edgecolor="#c3d5e8",
                alpha=0.6,
                linewidth=8,
                zorder=5,
            )

            acc_cons_hour = self.realtime_state.attributes.get(
                "accumulatedConsumptionLastHour"
            )
            if acc_cons_hour:
                timestamp = dt_util.parse_datetime(
                    self.realtime_state.attributes.get("timestamp")
                ).replace(minute=30, second=0)
                ax2.vlines(
                    [timestamp],
                    0,
                    [acc_cons_hour],
                    color="#68A7C6",
                    linewidth=8,
                    edgecolor="#c3d5e8",
                    alpha=0.35,
                    zorder=5,
                )

        try:
            await self.hass.async_add_executor_job(fig.savefig, self._path)
        except Exception:  # noqa: E731
            _LOGGER.debug("Failed to generate image", exc_info=True)

        plt.close(fig)
        plt.close("all")
