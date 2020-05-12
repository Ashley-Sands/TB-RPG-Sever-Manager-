# Things, that we must be thorughtfull of, otherwise this could all go horribly wrong
# and im not made of money, in fact i only have my $100 free azure credits.

    # the plan, is to orchestrate the tb_rpg game network
    # the network is made up of a backend database, and
    # lobby and game instance containers (managed)
    # and front end reverse proxy, with it own
    # private auth and lobby-directory containers (self-managed) 
    # (kubernetes would be idle for this part of the network)
    -------------------------------------------------------------
    # - phase 1
    # As the db is up and running to start with it will spawn a game 
    # instance so we have one instance for each queued game.
    # - phase 2
    # spawn a lobby when a users joins
    # - phase 3
    # increase the vm's
    #
    #
    

# Usfull RPG network CLI commands

## Create a DB Server 
### Note: i forgot the ssh in this command :/

az vm create -g RPG_Network_WE -n MASTER-mariadb --tags MNetwork=RPG dbType=Master --size standard_b1s --location westeurope --vnet-name VNet-WE --subnet db-net --image ubuntults

 