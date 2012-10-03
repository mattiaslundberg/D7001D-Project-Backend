#!/bin/bash

server=$1
echo server $server
my_key="-i $HOME/.ssh/12_LP1_KEY_D7001D_$LTU_USER.pem"
rmd="ssh -C -Y $my_key ubuntu@$server"

# TODO more
scp $my_key -r AWSSQS.py ubuntu@$server:~/

$rmd "sudo apt-get update -qq && sudo apt-get install vim -y"

echo "Done, exiting"

