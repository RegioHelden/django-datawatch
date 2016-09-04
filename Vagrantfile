# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = 'ubuntu/trusty64'

  config.vm.network :private_network, ip: "192.168.29.29"
  config.ssh.forward_agent = true

  # virualbox config
  config.vm.provider "virtualbox" do |vb|
    vb.cpus = 4
    vb.customize ['modifyvm', :id, '--memory', 2048]
    vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    vb.customize ['modifyvm', :id, '--name', 'ddw']
    config.vbguest.auto_update = true
  end
  config.vm.hostname = "ddw"

  # /etc/hosts entries
  config.hostmanager.enabled = true
  config.hostmanager.manage_host = true
  config.hostmanager.aliases = %w(ddw.dev)

  # folder synchronisation
  config.vm.synced_folder ".", "/vagrant", type: "nfs"
  config.vm.synced_folder 'vagrant/salt/roots', '/srv'

  # configuration
  config.vm.provision :salt do |salt|
    salt.masterless = true
    salt.minion_config = "vagrant/salt/minion.conf"
    salt.run_highstate = true
    salt.bootstrap_options = "-c /tmp/ -P"
    salt.verbose = true
    salt.colorize = true
    salt.log_level = "info"
  end
end
