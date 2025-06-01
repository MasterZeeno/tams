#!/usr/bin/env bash

width=100
margin=2
content_width=$((width - margin))

cat log.txt | fmt -w "$content_width" \
| awk -v margin="$margin" -v width="$width" '
{
  pad = sprintf("%*s", margin, "")
  if (length($0) < width - margin) {
    n = split($0, a, " ")
    if (n > 1) {
      extra = width - margin - length($0)
      for (i = 1; i <= extra; i++) {
        a[1 + ((i - 1) % (n - 1))] = a[1 + ((i - 1) % (n - 1))] " "
      }
      line = a[1]
      for (i = 2; i <= n; i++) line = line " " a[i]
      print pad line
    } else print pad $0
  } else print pad $0
}' > log2.txt