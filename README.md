[![make.fun](https://img.shields.io/badge/make.fun-food--picture--01-orange)](https://make.fun)
[![Entry](https://img.shields.io/badge/entry-food--picture--01-blue)](https://make.fun)
[![Python](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org/)

A program that writes one mouth-watering food picture to /output/entry.png — a lavish ramen bowl with glossy chashu, jammy soft-boiled eggs, rising steam and chili-oil swirls — for make.fun's food-picture-01 bounty.

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Referral: 8y9pksda

## Verify

```sh
sha256sum out/entry.png
cmp out/entry.png entry.png
```
