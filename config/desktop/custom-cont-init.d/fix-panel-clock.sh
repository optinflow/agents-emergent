#!/usr/bin/with-contenv bash
# LinuxServer custom-cont-init.d hook: fixes the XFCE panel clock plugin
# rendering date+time on two overlapping lines by forcing a compact,
# single-line format. Safe to run on every container start (idempotent).
(
  plugin_ids=""
  for i in $(seq 1 20); do
    plugin_ids=$(xfconf-query -c xfce4-panel -p /plugins -l 2>/dev/null | grep -oE 'plugin-[0-9]+' | sort -u)
    [ -n "$plugin_ids" ] && break
    sleep 2
  done
  for p in $plugin_ids; do
    if xfconf-query -c xfce4-panel -p "/plugins/$p/digital-format" >/dev/null 2>&1; then
      xfconf-query -c xfce4-panel -p "/plugins/$p/digital-format" -n -t string -s "%Y-%m-%d %H:%M" 2>/dev/null
      xfconf-query -c xfce4-panel -p "/plugins/$p/digital-format" -s "%Y-%m-%d %H:%M" 2>/dev/null
    fi
  done
) &
