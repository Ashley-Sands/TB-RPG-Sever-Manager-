# Usfull RPG network CLI commands

## Create a DB Server 
### Note: i forgot the ssh in this command :/

az vm create -g RPG_Network_WE -n MASTER-mariadb --tags MNetwork=RPG dbType=Master --size standard_b1s --location westeurope --vnet-name VNet-WE --subnet db-net --image ubuntults

 