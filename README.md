# Tibber prices
![Validate with hassfest](https://github.com/Danielhiversen/home_assistant_tibber_prices/workflows/Validate%20with%20hassfest/badge.svg)
[![GitHub Release][releases-shield]][releases]
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Display Tibber prices as a graph.

If you use this link to signup for Tibber, you get 50 euro to buy smart home products in the Tibber store: https://invite.tibber.com/6fd7a447

[Buy me a coffee :)](http://paypal.me/dahoiv)

{% if version_installed.replace(".","") | int <= 22  %}
## Configuration by integration page

Option to implement using integrations page has been introduced.
{% endif %}

{%- if selected_tag == "master" %}
## This is a development version!
This is **only** intended for test by developers!
{% endif %}

{%- if prerelease %}
## This is a beta version
Please be careful and do NOT install this on production systems. Also make sure to take a backup/snapshot before installing.
{% endif %}


## Configuration 

In configuration.yaml:

```
tibber_prices:
```


[releases]: https://github.com/Danielhiversen/home_assistant_tibber_prices/releases
[releases-shield]: https://img.shields.io/github/release/Danielhiversen/home_assistant_tibber_prices.svg?style=popout
[downloads-total-shield]: https://img.shields.io/github/downloads/Danielhiversen/home_assistant_tibber_prices/total
[hacs-shield]: https://img.shields.io/badge/HACS-Default-orange.svg
[hacs]: https://hacs.xyz/docs/default_repositories
