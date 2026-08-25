<?php

$ip = trim(shell_exec("hostname -I | awk '{print $1}'"));


echo "Frontend pc : http://localhost:5173" . PHP_EOL;
echo "Backend pc : http://localhost:5000" . PHP_EOL;
echo "Frontend accessible depuis mobile : http://$ip:5173" . PHP_EOL;
echo "Backend accessible depuis mobile : http://$ip:5000" . PHP_EOL;
