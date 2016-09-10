python:
  pkg:
    - installed
    - names:
      - python-dev
      - python
      - python3
      - python3-dev

python-pip:
  pkg:
    - installed
    - names:
      - python-pip
      - python3-pip
    - require:
      - pkg: python
      - pkg: python3

virtualenv:
  pip:
    - installed
    - bin_env: '/usr/bin/pip'
    - require:
      - pkg: python-pip
      - pkg: python3-pip

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
    - python: python
    - require:
      - pkg: postgresql
      - pip: virtualenv
      - file: /home/vagrant/virtualenv


/home/vagrant/virtualenv3:
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
    - python: python3
    - require:
      - pkg: postgresql
      - pip: virtualenv
      - file: /home/vagrant/virtualenv3
