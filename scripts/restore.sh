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
        if [[ $param == "file" ]]; then
                declare $param="$2"
        fi
    fi

  shift
done

directory="$directory/"

selected_dump="$file"
files=( $directory*.dump )
shopt -s extglob
filenames_string="@(${files[0]}"

for((i=1;i<${#files[@]};i++))
do
    filenames_string+="|${files[$i]}"
done
filenames_string+=")"
selected_dump=""
print_yellow 'Please, select one of the following dumps to restore (enter the number):'
select file in "${files[@]}"
do
    case $file in
    $filenames_string)
        selected_dump=$file
        break;
        ;;
    *)
        file=""
        print_red "\nPlease choose a number from 1 to $((${#files[@]}))"
    esac
done

echo "Selected dump: $selected_dump"

#Copy the dump file to the container
if ! docker-compose cp "$selected_dump" db:/ ; then
    print_red "\nError when copying the $selected_dump file to the docker container\n"
    exit
fi

print_green "\nRestoring database...\n"

# Disallow database connections
if ! docker-compose exec db psql -d postgres -c "alter database devdb with ALLOW_CONNECTIONS false;" ; then
    print_red "\nError disallowing database connections.\n"
    exit
fi

# Terminate current connections expect the one we are using
if ! docker-compose exec db psql -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid <> pg_backend_pid() AND pg_stat_activity.datname='devdb'" ; then
    print_red "\nError terminating database connections.\n" 
    exit
fi

# Droping the database
if ! docker-compose exec db dropdb -f devdb --username=devuser --if-exists; then
    print_red "\nError dropping the devdb database.\n" 
    exit
fi

# Creating a new fresh database
if ! docker-compose exec db createdb devdb --username=devuser; then
    print_red "\nError creating devdb database.\n" 
    exit
fi

# Restore the database
if ! docker-compose exec db pg_restore --no-owner --no-privileges -U devuser --role=devuser -d devdb /${selected_dump##*/} ; then
    print_red "\nError restoring the dump file inside the container.\n"
    exit
fi

if [[ $delete == "true" ]]; then
    print_green "\nDeleting restored dump...\n"
    rm "$selected_dump"
fi

print_green "\nSuccess! dump restored.\n"
