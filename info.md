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
