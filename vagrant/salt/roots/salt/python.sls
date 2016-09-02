python3:
  pkg:
    - installed
    - names:
      - python3-dev
      - python3

python-pip:
  pkg:
    - installed
    - names:
      - python-pip
      - python3-pip
    - require:
      - pkg: python3

virtualenv:
  pip:
    - installed
    - bin_env: '/usr/bin/pip3'
    - require:
      - pkg: python-pip

/home/vagrant/virtualenv:
  file:
    - directory
    - user: vagrant
    - group: vagrant
    - makedirs: True

  virtualenv:
    - managed
    - system_site_packages: False
    - distribute: True
    - requirements: /vagrant/requirements.txt
    - user: vagrant
    - no_chown: True
    - require:
      - pkg: postgresql
      - pip: virtualenv
      - file: /home/vagrant/virtualenv
