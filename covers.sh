#!/bin/bash

if [ $# -ne 0 ]
then
    search_location="$1"
else
    search_location="/data/radio/"
fi
echo "Searching $search_location for files to add covers"

while IFS= read -r -d '' file
do
    image=$(echo "${file%.*}.jpg")
    if [[ -e "$image" ]]
    then
        echo "$file"
        AtomicParsley "$file" -t | grep 'covr'
        if [ $? != 0 ]
        then
            echo -e "\tAdding cover"
            AtomicParsley "$file" --artwork "$image" --overWrite
        fi
    fi
done < <(find "$search_location" -type f -iname "*.m4a" -print0)
