#!/usr/bin/env python

import sys,os,re

os.system('find ./ -name "*.pyc" | xargs -n1 rm')
os.system('find ./ -name ".DS_Store" | xargs -n1 rm')
os.system('rm -rf jamendo/bittorrent/clients/BitTornado/build')
os.system('rm -rf jamendo/bittorrent/clients/BitTornado/dist')
os.system('rm -rf build/')
os.system('rm -rf dist/')