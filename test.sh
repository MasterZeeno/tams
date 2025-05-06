#!/usr/bin/env bash

pkgs=(python3 python3-pip chromium-chromedriver)

for pkg in "${pkgs[@]}"; do
  echo "$pkg" | sed -E 's/(^| )((chromium|python3)-)/\1/Ig'
done


