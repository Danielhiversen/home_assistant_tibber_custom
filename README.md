# Tibber Custom :zap: 
![Validate with hassfest](https://github.com/Danielhiversen/home_assistant_tibber_custom/workflows/Validate%20with%20hassfest/badge.svg)
[![GitHub Release][releases-shield]][releases]
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Display Tibber prices and your consumption as a graph.
Tibber is available in Germany, Norway and Sweden
Tibber has helped tens of thousands of new customers each month in Sweden, Norway & Germany to lower their energy bill and consumption. Tibber is using digital technology to make electricity consumption smarter.
The consumption is only shown if you have a realtime meter (Tibber Pulse or Watty)

If you use this link to signup for Tibber, you get 50 euro to buy smart home products in the Tibber store: https://invite.tibber.com/6fd7a447


[Buy me a coffee :)](http://paypal.me/dahoiv)

![imgage](/ex2.png)

![imgage](/ex1.png)

## Install
https://hacs.xyz/docs/faq/custom_repositories

## Configuration 

The Tibber component needs to be configurated first: https://www.home-assistant.io/integrations/tibber/

In configuration.yaml:

```
tibber_custom:
```

You will then get a `camera.YOUR_ADRRESS` that displays the current graphic.


[releases]: https://github.com/Danielhiversen/home_assistant_tibber_custom/releases
[releases-shield]: https://img.shields.io/github/release/Danielhiversen/home_assistant_tibber_custom.svg?style=popout
[downloads-total-shield]: https://img.shields.io/github/downloads/Danielhiversen/home_assistant_tibber_custom/total
[hacs-shield]: https://img.shields.io/badge/HACS-Default-orange.svg
[hacs]: https://hacs.xyz/docs/default_repositories
