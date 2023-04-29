#!/bin/bash

print_red(){
   echo -e "$(tput setaf 1)$1$(tput sgr 0)"
}

print_green(){
   echo -e "$(tput setaf 2)$1$(tput sgr 0)"
}

print_yellow(){
   echo -e "$(tput setaf 3)$1$(tput sgr 0)"
}

directory=${directory:-"./dumps"}

file=${file:-none}

while [ $# -gt 0 ]; do

   if [[ $1 == *"--"* ]]; then
        param="${1/--/}"
        declare $param="$2"
   fi

  shift
done

directory="$directory/"
# dump name is equal to the day month and year and hour and minutes
dump_name=$(date +"%Y-%m-%d-%H-%M")

#Execute the restore command inside the container
if ! (docker-compose exec db pg_dump -Fc -Z 9 --username devuser devdb -f /$dump_name.dump ) ; then
    print_red "\nError creating the dump.\n"
    exit
fi

#Copy the dump file from container to the host
if ! (docker-compose cp db:/$dump_name.dump $directory$dump_name.dump ) ; then
    print_red "\nError Copying the dump file from the container to the host. Maybe the path on the host does not exist?\n"
    exit
fi

print_green "\nSuccess! dump created on $directory$dump_name.dump \n"
