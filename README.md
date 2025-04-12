# cnheat

**Python module for interacting with the Cambium Networks cnHeat API** — manage sites, radios, antennas, predictions, users, and subscriptions programmatically.

This library provides a simple and powerful Python interface to the Cambium cnHeat API, enabling you to automate RF planning, data management, and network operations with minimal effort.

---

## 🚀 Features

- 🔐 Authenticate using client ID and secret
- 🏗 Create, list, rename, and delete sites
- 📡 Add and configure radios using antenna templates
- 📊 Generate and manage heatmap predictions
- 👥 Add or remove users with permission control
- 📦 Manage subscriptions and renewal status
- 📁 Convert API responses to lists or dictionaries
- ✅ Includes helper methods for working with `site_id`, `antenna_id`, and `radio_id` cleanly

---

## 📦 Installation

Install from PyPI:

```bash
pip install cnheat

🔧 Basic Usage
from cnheat import cnHeat

cn = cnHeat(client_id="your_id", client_secret="your_secret")
sites = cn.get_sites()
print(sites)
