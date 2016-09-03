python:
  pkg:
    - installed
    - names:
      - python-dev
      - python

python-pip:
  pkg:
    - installed
    - names:
      - python-pip
    - require:
      - pkg: python

virtualenv:
  pip:
    - installed
    - bin_env: '/usr/bin/pip'
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
