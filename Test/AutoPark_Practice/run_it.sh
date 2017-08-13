
#!/bin/sh
#
# Copyright (c) 2016
# Author: Victor Arribas <v.arribas.urjc@gmail.com>
# License: GPLv3 <http://www.gnu.org/licenses/gpl-3.0.html>

world=autopark.world

gzserver --verbose --minimal_comms $world &
sleep 5 # up to 20 for autopark.world

[ "$1" = "GUI" ] && gzclient &

python2 autopark.py --Ice.Config=autopark.cfg &

python2 referee.py --Ice.Config=autopark.cfg

killall gzserver
killall python2
[ "$1" = "GUI" ] && killall gzclient
