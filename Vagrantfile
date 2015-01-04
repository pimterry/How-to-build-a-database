# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|
  config.vm.box = "ubuntu/trusty64"  
  config.vm.forward_port 8080, 8080

  config.vm.provision "shell", inline: ('
    apt-get -y install python3 python3-pip python3-dev python-lxml
    pip3 install virtualenv

    su vagrant -c "virtualenv /home/vagrant/venv"
    su vagrant -c "venv/bin/pip install -r /vagrant/requirements.txt"

    echo ". venv/bin/activate" >> /home/vagrant/.bashrc    
    echo "cd /vagrant" >> /home/vagrant/.bashrc 
  ')
end