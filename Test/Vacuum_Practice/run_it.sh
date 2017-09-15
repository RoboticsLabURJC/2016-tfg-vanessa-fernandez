#!/bin/sh
#
# Copyright (c) 2016
# Author: Victor Arribas <v.arribas.urjc@gmail.com>
# License: GPLv3 <http://www.gnu.org/licenses/gpl-3.0.html>

world=Vacuum.world

gzserver --verbose --minimal_comms $world &
sleep 10 # up to 20 for circuit.world

[ "$1" = "GUI" ] && gzclient &

python2 vacuumCleaner.py --Ice.Config=vacuumCleaner.cfg &

python2 referee.py --Ice.Config=vacuumCleaner.cfg &

python2 graphicPercentaje.py --Ice.Config=vacuumCleaner.cfg

killall gzserver
killall python2
[ "$1" = "GUI" ] && killall gzclient
