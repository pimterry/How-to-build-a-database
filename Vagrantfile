# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/trusty64"  
  config.vm.box_url = "https://atlas.hashicorp.com/ubuntu/boxes/trusty64/versions/14.04/providers/virtualbox.box"

  config.vm.network :forwarded_port, host: 8080, guest: 8080
  config.vm.network :forwarded_port, host: 8082, guest: 8082
  config.vm.network :forwarded_port, host: 8081, guest: 8081

  config.vm.provision "shell", inline: ('
    apt-get -y install python3 python3-pip python3-dev python-lxml
    pip3 install virtualenv

    su vagrant -c "virtualenv /home/vagrant/venv"
    su vagrant -c "venv/bin/pip install -r /vagrant/requirements.txt"

    echo ". venv/bin/activate" >> /home/vagrant/.bashrc    
    echo "cd /vagrant" >> /home/vagrant/.bashrc 
  ')
end