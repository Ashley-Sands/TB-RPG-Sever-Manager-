# Things, that we must be thorughtfull of, otherwise this could all go horribly wrong
# and im not made of money, in fact i only have my $100 free azure credits.

    # the plan, is to orchestrate the tb_rpg game network
    # the network is made up of a backend database, and
    # lobby and game instance containers (managed)
    # and a front end reverse proxy, with it own
    # private auth and lobby-directory containers (self-managed) 
    # 
    # (kubernetes would be idle for this part of the network)
    -------------------------------------------------------------
    # 1. find how many containers are running when we initialized
    # 2. find how many proxies are running
    # 3. find the amount of required containers
    # 4. find the amount od required proxies
    # 5. spin up/down containers as required
    # 6. spin up/down proxies are required
    #
    
    
## Create a DB Server 

az vm create -g RPG_Network_WE -n MASTER-mariadb --tags MNetwork=RPG dbType=Master --size standard_b1s --location westeurope --vnet-name VNet-WE --subnet db-net --image ubuntults

 