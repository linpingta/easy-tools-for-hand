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
	echo "INPUT_FILE_NAME: $OPTARG"
	INPUT_FILE_NAME=$OPTARG
	;;
	m)
	echo "MODEL_NAME: $OPTARG"
	MODEL_NAME=$OPTARG
	;;
	t)
	echo "FILE_TYPE: $OPTARG"
	FILE_TYPE=$OPTARG
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

mkdir -p $PROJECT_PATH/{lib,conf,logs,data,test}
PARENT_DIR=$PROJECT_PATH
LIB_DIR=$PROJECT_PATH/lib
CONF_DIR=$PROJECT_PATH/conf
LOGS_DIR=$PROJECT_PATH/logs
if [ -n "$FILE_NANE" ]; then
    FILE_NAME="$INPUT_FILE_NAME"
else
    FILE_NAME="$PROJECT_NAME"
fi
if [ -n "$FILE_TYPE" ]; then
    PARENT_FILE_NAME="$FILE_NAME.$FILE_TYPE"
else
    PARENT_FILE_NAME="$FILE_NAME.py"
    FILE_TYPE="py"
fi
touch $PARENT_DIR/$PARENT_FILE_NAME
touch $CONF_DIR/$FILE_NAME.conf
touch $LOGS_DIR/$FILE_NAME.log
if [ -n "$MODEL_NAME" ]; then
    MODEL_PATH=$PROJECT_PATH/lib/$MODEL_NAME
    mkdir -p $MODEL_PATH
    touch $MODEL_PATH/__init__.py 
fi

if [ "$FILE_TYPE" = "py" ]; then
    echo $FILE_TYPE
    echo $CUR_DIR
fi

echo "Project $PROJECT_PATH Made"

