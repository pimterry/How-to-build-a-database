# How to build a database

Setup
-----

1. Install Vagrant from https://www.vagrantup.com/downloads.html
2. Install Virtualbox from https://www.virtualbox.org/wiki/Downloads
3. Run `vagrant up` to set up a preconfigured Vagrant VM
4. Run `vagrant ssh` to log into the VM
5. Run `python main.py`, to run the DB server in the foreground
6. From your local (host) machine connect to `http://localhost:8080`. If everything is working you should initially get a 404 here.
   
Alternatively, install Python 3 (tested with 3.4.0) and run `pip install -r requirements.txt` to install the required dependencies. This will probably require you to set up a local compilation toolchain so you can build binary dependencies, and as such the vagrant method is preferred.
