
#!/bin/sh
#
# Copyright (c) 2016
# Author: Victor Arribas <v.arribas.urjc@gmail.com>
# License: GPLv3 <http://www.gnu.org/licenses/gpl-3.0.html>

world=autopark.world
#world=circuit.world

gzserver --verbose --minimal_comms $world &
sleep 5 # up to 20 for circuit.world

[ "$1" = "GUI" ] && gzclient &

python3 autopark.py --Ice.Config=autopark.cfg

killall gzserver
[ "$1" = "GUI" ] && killall gzclient
