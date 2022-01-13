# svachal

[![License: CC BY-SA 4.0](https://raw.githubusercontent.com/7h3rAm/7h3rAm.github.io/master/static/files/ccbysa4.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

This is an automation framework for machine writeups. It defines a YAML based writeup template that can be used while working on a machine. Once the writeup is complete, the YAML writeup file can be used to render a `.md` and `.pdf` report alongwith stats and summary for all completed writeups. It works in conjuction with [machinescli](https://github.com/7h3rAm/machinescli) project, so all machine metadata is natively accessible:

## Install

You will need to configure [`machinescli`](https://github.com/7h3rAm/machinescli) before using `svachal`.  First, setup a `projects` directory to initialize a working virtualenv:

```
mkdir -pv $HOME/toolbox/projects && cd $HOME/toolbox/projects
python3 -m venv --copies venv
source venv/bin/activate
```

Next, get your HTBAPIKEY from [HackTheBox](https://www.hackthebox.com/home/settings), go to your username tab > Classic HTB > Settings > API Key. Then, follow the steps below and run `machinescli` to create the shared `machines.json` file:

```
$ cd $HOME/toolbox/projects
$ git clone https://github.com/7h3rAm/machinescli && cd machinescli
$ pip install -r requirements.txt
$ mkdir -pv $HOME/toolbox/bootstrap
$ export HTBAPIKEY=<APIKEYHERE>
$ python3 machinescli.py --update
```

Next, clone `svachal` repository, setup virtual environment and install requirements:

```
$ cd $HOME/toolbox/projects
$ git clone https://github.com/7h3rAm/svachal && cd svachal
$ pip install -r requirements.txt
$ python3 svachal.py -h
```

`svachal` expects GitHub to be the primary portal for writeups storage and sharing. As such, it needs a repo URL for links within writeups to correctly point to right resources. Initialize `svachal` for first run by creating a writeups directory and run with `-w` and `-g` arguments:

```
$ mkdir -pv $HOME/toolbox/projects/writeups && cd $HOME/toolbox/projects/writeups
$ git init
$ git add .
$ git commit -m 'Initial commit'
$ git remote add github http://github.com/<USERNAME>/writeups
$ git push github master
$ python3 $HOME/toolbox/projects/svachal.py -w $HOME/toolbox/projects/writeups -g http://github.com/<USERNAME>/writeups -s "https://app.hackthebox.eu/machines/200"
writeup:
  metadata:
    status: private
    datetime: 20220101
    infra: HackTheBox
    name: Rope
    points: 50
    path: htb.rope
    url: https://app.hackthebox.eu/machines/200
    infocard: ./infocard.png
    references:
      -
    categories:
      - linux
      - hackthebox
    tags:
      - enumerate_
      - exploit_
      - privesc_
  overview:
    description: |
      This is a writeup for HackTheBox VM [`Rope`](https://app.hackthebox.eu/machines/200). Here's an overview of the `enumeration` → `exploitation` → `privilege escalation` process:

[+] writeup file '/home/kali/toolbox/projects/writeups/htb.rope/writeup.yml' created for target 'htb.rope'
[+] created '/home/kali/toolbox/projects/writeups/htb.rope/ratings.png' file for target 'htb.rope'
[+] created '/home/kali/toolbox/projects/writeups/htb.rope/matrix.png' file for target 'htb.rope'
```

## Usage
![Usage](svachal01.png)

## Usecases
1. Start a new writeup:
![Start](svachal02.png)

1. Finish a writeup:
![Finish](svachal03.png)

1. Summarize all writeups:
![Summarize](svachal04.png)

1. Override default writeup directory and GitHub repo URL:
```console
$ svachal -w $HOME/<reponame> -g "https://github.com/<username>/<reponame>
```

## Summarized Writeup Graphs

![Top writeup categories](top_categories.png)

![Top writeup ports](top_ports.png)

![Top writeup protocols](top_protocols.png)

![Top writeup services](top_services.png)


## Argument Autocomplete
Source the `.bash-completion` file within a shell to trigger auto-complete for arguments. This will require the following alias (change path as needed): 
```console
alias svachal='python3 $HOME/toolbox/projects/svachal/svachal.py -w $HOME/toolbox/projects/writeups -g http://github.com/<USERNAME>/writeups'
```

> You will need a [Nerd Fonts patched font](https://github.com/ryanoasis/nerd-fonts/tree/master/patched-fonts) for OS icons and other symbols to be rendered correctly.
