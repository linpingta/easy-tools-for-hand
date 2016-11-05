#!/bin/bash

usage(){
	echo "./project_maker.sh -p [project_name]"
	exit 1
}

while getopts ":p:f:hm:t:" opt; do
	case $opt in 
	p)
	echo "PROJECT_NAME: $OPTARG"
	PROJECT_NAME=$OPTARG
	;;
	h)
	usage
	;;
	\?)
	echo "Invalid Option: $OPTARG"
	usage
	;;
	esac
done

if [ -z "$PROJECT_NAME" ]; then
    echo "Project Name Empty, Exit"
    exit 1
fi

CUR_DIR=`pwd`
PROJECT_PATH=$CUR_DIR/$PROJECT_NAME

echo "Project $PROJECT_PATH Making..."

mkdir -p $PROJECT_PATH/src/{main,test}/{java,resources,scala}

# create an initial build.sbt file
echo 'name := "$PROJECT_NAME"
version := "1.0"
scalaVersion := "2.11.8"' > $PROJECT_PATH/build.sbt

echo "Project $PROJECT_PATH Made"
