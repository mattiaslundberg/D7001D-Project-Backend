#!/bin/bash

server=$1
echo server $server
my_key="-i $HOME/.ssh/12_LP1_KEY_D7001D_$LTU_USER.pem"
rmd="ssh -C -o StrictHostKeyChecking=no -Y $my_key ubuntu@$server"

# Upload all but testdata...
scp -o StrictHostKeyChecking=no $my_key * ubuntu@$server:~/

# We need libboost-serialization-dev for process.
#$rmd "sudo apt-get update -qq && sudo apt-get install vim libboost-serialization-dev -y"
$rmd "sudo chmod +x * && "

echo "Done, exiting"
