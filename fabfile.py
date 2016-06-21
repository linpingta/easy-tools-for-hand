from fabric.api import local, lcd, put, get
from fabric.api import env
import os

env.hosts=['username@host:port']
env.password = 'remotepasswd if necessary'

base_dir = 'your_remote_path'

def git_status():
	local('git branch')
	local('git status')

def git_commit(branch="master", message="update"):
	local('git add -A')
	local('git commit -m %s' % message)
	local('git push origin %s' % branch)

def scp_from_remote(*files):
	[ get(os.path.join(base_dir, file), file) for file in files ]

def scp_to_remote(*files):
	[ put(file, os.path.join(base_dir, file)) for file in files ]
