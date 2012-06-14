# Appengine Git

> This project is currently untested and is not recommended for production use

A Git server running over http on Google Appengine
This project uses Dulwich - a pure Python interface to Git repos http://www.samba.org/~jelmer/dulwich/

### Running
1. Download Google Appengine, Python edition
    https://developers.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python

2. Extract appengine and run the appserver on the Appengine Git src folder
    google_appengine/dev_appserver.py AppengineGit/src

### Create a repository
1. open your browser to the server, by default at http://localhost:8080

2. open the browsers javascript console, and enter:

        rpc.send("repo.create", {"name":"repoName"})
    "200 NULL" should appear under the response heading

3. to push to the repository

        git remote add origin http://localhost:8080/repoName.git
        git push origin master
        

### List repositories on the server
1. open your browser to the server, by default at http://localhost:8080

2. open the browsers javascript console, and enter:

        rpc.send("repo.list", {})
    the http response code (200) should appear under the response heading, followed by a json encoded array of repository names.