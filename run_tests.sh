#!/usr/bin/env bash

coverage erase
coverage run --omit "*tests*" -m unittest2 discover
coverage report
