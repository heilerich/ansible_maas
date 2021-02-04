#!/bin/sh
ansible-galaxy collection build
ansible-galaxy collection install --force heilerich-maas-1.0.0.tar.gz
rm heilerich-maas-1.0.0.tar.gz
