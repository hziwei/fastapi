#!/usr/bin/env bash

# argv

# functions

function _main
{
  status=`curl -X 'GET' \
  'http://localhost:8000/test/api/v1/healthcheck' \
  -H 'accept: application/json'|grep ok`
  [ ${#status} -eq 0 ] && exit 1

  exit 0
}

# main

_main "$@"