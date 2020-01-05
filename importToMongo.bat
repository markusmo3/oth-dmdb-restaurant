@echo off
IF %1.==. GOTO Usage
echo "Calling mongoimport in a docker container..."
setlocal
cd data
docker build --build-arg PW=%1 --no-cache -f Dockerfile-mongoimport .
endlocal
GOTO End1

:Usage
ECHO usage: %0 ^<password^>
ECHO password is for the mongoimport command with the user importer
ECHO.
ECHO This batch probably doesn't work for any other user...
ECHO It directly uses my host of Atlas and the username 'importer'
ECHO If you want to write your own command line for it then just 
ECHO make sure to append the following to your mongoimport command:
ECHO   --type json --jsonArray --drop
ECHO and import the two files 'deduped_raw.json' and 'deduped_clean.json'
ECHO from the directory './data/work/'
GOTO End1

:End1