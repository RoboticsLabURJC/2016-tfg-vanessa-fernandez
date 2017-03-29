
#!/bin/sh
#
# Copyright (c) 2016
# Author: Victor Arribas <v.arribas.urjc@gmail.com>
# License: GPLv3 <http://www.gnu.org/licenses/gpl-3.0.html>

world=stop.world
#world=circuit.world

gzserver --verbose --minimal_comms $world &
sleep 5 # up to 20 for circuit.world

[ "$1" = "GUI" ] && gzclient &

python3 stop.py --Ice.Config=stop.cfg

killall gzserver
killall python3
[ "$1" = "GUI" ] && killall gzclient
