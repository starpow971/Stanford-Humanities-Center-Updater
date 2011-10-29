#!/bin/bash

cd $(dirname $0)

python dumper.py

python populater.py

python workshop_populater.py