#!/bin/bash

echo "=========================="
echo " DevOps Lab - System Info"
echo "=========================="

echo ""
echo "Hostname:"
hostname

echo ""
echo "Operating System:"
sw_vers

echo ""
echo "Architecture:"
uname -m

echo ""
echo "Current User:"
whoami

echo ""
echo "Current Directory:"
pwd

echo ""
echo "Disk Usage:"
df -h /

echo ""
echo "Memory:"
sysctl -n hw.memsize

echo ""
echo "Git Version:"
git --version

echo ""
echo "Homebrew Version:"
brew --version