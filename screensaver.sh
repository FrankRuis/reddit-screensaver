#!/bin/bash
# timeout in ms
timeout=60000
to_sleep=$((timeout+1000))
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# sleep until the desired idle time
while sleep $((to_sleep/1000)); do
    # check the screen idle time
    idle=$(DISPLAY=:0 xprintidle)
    if (( idle > timeout )); then
        # start feh if it is not running yet
        if ! pgrep "feh" > /dev/null; then
            DISPLAY=:0 feh -ZXYrzFD 25 "$DIR/img" --zoom fill --reload 180 &
            # and a key binding to kill feh on left mouse click
            echo '"pkill -n feh; pkill -n xbindkeys"'>"$DIR/xbindkeys.temp"
            echo "b:1">>"$DIR/xbindkeys.temp"
            DISPLAY=:0 xbindkeys -n -f "$DIR/xbindkeys.temp"
            sudo rm "$DIR/xbindkeys.temp"
        fi
        to_sleep=$((timeout+1000))
    else
        to_sleep=$((timeout-idle+1000))
    fi
done
