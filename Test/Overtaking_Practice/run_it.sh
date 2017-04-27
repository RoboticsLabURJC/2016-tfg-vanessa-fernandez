#!/bin/sh
#
# Copyright (c) 2016
# Author: Victor Arribas <v.arribas.urjc@gmail.com>
# License: GPLv3 <http://www.gnu.org/licenses/gpl-3.0.html>

world=Overtaking.world

gzserver --verbose --minimal_comms $world &
sleep 10 # up to 20 for circuit.world

[ "$1" = "GUI" ] && gzclient &

#python2 Overtaking.py --Ice.Config=Overtaking.cfg &
python2 Overtaking.py --Ice.Config=Overtaking.cfg

#python2 referee.py --Ice.Config=Overtaking.cfg

killall gzserver
#killall python2
[ "$1" = "GUI" ] && killall gzclient
