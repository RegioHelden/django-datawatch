/home/vagrant/bashrc:
  file.managed:
    - name: /home/vagrant/.bashrc
    - source:
      - salt://files/bashrc
    - user: vagrant
    - group: vagrant
    - mode: 644
