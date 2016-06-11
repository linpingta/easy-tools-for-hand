#!/bin/bash

usage(){
	echo "./project_maker.sh -p [project_name] -f [file_name] -m [model_name] -t [file_extension]"
	exit 1
}

while getopts ":p:f:hm:t:" opt; do
	case $opt in 
	p)
	echo "PROJECT_NAME: $OPTARG"
	PROJECT_NAME=$OPTARG
	;;
	f)
	echo "FILE_NAME: $OPTARG"
	FILE_NAME=$OPTARG
	;;
	m)
	echo "MODEL_NAME: $OPTARG"
	MODEL_NAME=$OPTARG
	;;
	t)
	echo "PROJECT_TYPE: $OPTARG"
	PROJECT_TYPE=$OPTARG
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

if [ -z "$FILE_NAME" ]; then
    echo "File Name Empty, Exit"
    exit 1
fi

CUR_DIR=`pwd`
PROJECT_PATH=$CUR_DIR/$PROJECT_NAME

echo "Project $PROJECT_PATH Making..."

mkdir -p $PROJECT_PATH/{bin,lib,conf,logs}
BIN_DIR=$PROJECT_PATH/bin
LIB_DIR=$PROJECT_PATH/lib
CONF_DIR=$PROJECT_PATH/conf
LOGS_DIR=$PROJECT_PATH/logs
if [ -n "$PROJECT_TYPE" ]; then
    BIN_FILE_NAME="$FILE_NAME.$PROJECT_TYPE"
else
    BIN_FILE_NAME="$FILE_NAME"
fi
touch $BIN_DIR/$BIN_FILE_NAME
touch $CONF_DIR/$FILE_NAME.conf
touch $LOGS_DIR/$FILE_NAME.log
if [ -n "$MODEL_NAME" ]; then
    MODEL_PATH=$PROJECT_PATH/lib/$MODEL_NAME
    mkdir -p $MODEL_PATH
    touch $MODEL_PATH/__init__.py 
fi

echo "Project $PROJECT_PATH Made"

