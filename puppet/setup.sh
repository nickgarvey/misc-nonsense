#!/bin/bash
set -ex

if [[ $(lsb_release -cs) = "bionic" ]]; then
    curl 'https://apt.puppetlabs.com/puppet6-release-bionic.deb' >> puppet_repo.deb
else
    echo "Update script for new distro" >> /dev/stderr
    exit 1
fi

sudo dpkg -i puppet_repo.deb
sudo apt update
sudo apt install puppet-agent=6.\*

cat <<EOF > puppet.conf
[main]
server = puppet.nickgarvey.com
EOF

sudo mv puppet.conf /etc/puppetlabs/puppet/puppet.conf

sudo /opt/puppetlabs/bin/puppet agent -t
