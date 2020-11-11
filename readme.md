# svachal

[![License: CC BY-SA 4.0](https://raw.githubusercontent.com/7h3rAm/7h3rAm.github.io/master/static/files/ccbysa4.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

This is an automation framework for machine writeups. It defines a YAML based writeup template that can be used while working on a machine. Once the writeup is complete, the YAML writeup file can be used to render a `.md` and `.pdf` report alongwith stats and summary for all completed writeups. It works in conjuction with [machinescli](https://github.com/7h3rAm/machinescli) project, so all machine metadata is natively accessible:

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
alias svachal='python3 $HOME/svachal/svachal.py'
```

> You will need a [Nerd Fonts patched font](https://github.com/ryanoasis/nerd-fonts/tree/master/patched-fonts) for OS icons and other symbols to be rendered correctly.
