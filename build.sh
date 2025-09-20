#!/usr/bin/bash
aaa=$1 
objdump -D ./uploads/$aaa.o > ./download/$aaa.S 