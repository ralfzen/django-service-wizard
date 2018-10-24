#!/bin/bash

set -e  # stops the script on error

usage="$(basename "$0") [-h | --help] [--ci] -- runs project's tests
where:
    -h | --help  show this help text
    --ci  runs tests in CI mode (it will show extra info)
    "

ci=false

# Parse options. Note that options may be followed by one colon to indicate
# they have a required argument
if ! options=$(getopt -o h -l ci,help -- "$@")
then
    # Error, getopt will put out a message for us
    exit 1
fi

set -- $options

while [ $# -gt 0 ]
do
    # Consume next (1st) argument
    case $1 in
    -h|--help)
      echo "$usage"; exit ;;
    --ci)
      ci="true" ;;
    (--)
      shift; break;;
    (-*)
      echo "$0: error - unrecognized option $1" 1>&2; exit 1;;
    (*)
      break;;
    esac
    # Fetch next argument as 1st
    shift
done

set -o xtrace  # shows what's being executed

pip install -r requirements/ci.txt
if [ "$ci" = true ] ; then
    cat .flake8
fi
flake8 .
if [ "$ci" = true ] ; then
    coverage run --source='.' manage.py test -v 2
    coverage report -m
else
    python manage.py test -v 2  # --keepdb to run faster or --debug-mode to DEBUG=True
fi
python manage.py makemigrations --check --dry-run
