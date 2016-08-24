#!/bin/bash

# try install required packages globally without sudo
{
   pip install -r requirements.txt
} ||

# catch
# install required packages globally with sudo
{
    sudo pip install -r requirements.txt
}


