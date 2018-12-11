#!/bin/bash
if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
else
	s="Running "$1
	# add command for choices like WB CRS echo "$2"
	echo "$s"
	python ../manage.py shell_plus < $1
	echo "Fini..."
fi
