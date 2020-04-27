#!/bin/bash
set -ex

if [[ $# -ne 1 ]]; then
    echo "usage: $0 new_hostname"
    exit 1
fi

sudo hostnamectl set-hostname "$1"

if [[ $(lsb_release -cs) = "bionic" ]]; then
    curl 'https://apt.puppetlabs.com/puppet6-release-bionic.deb' >> puppet_repo.deb
    sudo dpkg -i puppet_repo.deb
    sudo apt update
    sudo apt install -y puppet-agent=6.\*
    CONF_FILE="/etc/puppetlabs/puppet/puppet.conf"
    PATH="$PATH:/opt/puppetlabs/bin"
elif [[ $(lsb_release -cs) = "focal" ]]; then
    # package doesn't exist on focal yet, just install puppet 5 from repo
    sudo apt install -y puppet
    CONF_FILE="/etc/puppet/puppet.conf"
else
    echo "Update script for new distro" >> /dev/stderr
    exit 1
fi

cat <<EOF > puppet.conf
[main]
server = puppet.nickgarvey.com
EOF

sudo mv puppet.conf "$CONF_FILE"

sudo puppet agent -t || true && exit

FINGERPRINT=$(sudo puppet agent --fingerprint --noop | awk '{print $2}')

if [[ ! $FINGERPRINT =~ [A-F0-9:]+ ]]; then
	echo "Couldn't get fingerprint? got: $FINGERPRINT"
	exit 1
fi

ssh ubuntu@puppet.nickgarvey.com "sudo puppetserver ca list | grep $FINGERPRINT || exit 1; sudo puppetserver ca sign --certname '$1'"
sudo puppet agent -t
