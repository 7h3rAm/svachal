---
lang: "en"
classoption: oneside
code-block-font-size: \scriptsize
geometry: "a4paper"
geometry: "margin=2cm"
header-includes:
  - \usepackage{float}
  - \floatplacement{figure}{H}
  - \usepackage{xcolor}
  - \hypersetup{breaklinks=true,
                bookmarks=true,
                pdftitle="{{ writeup.metadata.name|replace(':', '')|replace('#', '') }}",
                pdfauthor="svachal (@7h3rAm)",
                pdfsubject='Writeup for {{ writeup.metadata.infra }} VM {{ writeup.metadata.name|replace(':', '')|replace('#', '') }}',
                pdfkeywords="{{ writeup.metadata.categories|join(' ') }}",
                colorlinks=true,
                linkcolor=cyan,
                urlcolor=blue}
  - \usepackage{fvextra}
  - \DefineVerbatimEnvironment{Highlighting}{Verbatim}{breaklines,breakanywhere=true,commandchars=\\\{\}}
  - \usepackage{mathtools}
---

# [[{{ writeup.metadata.infra }}] {{ writeup.metadata.name }}]({{writeup.metadata.url}})

**Date**: {{ writeup.metadata.datetime|datetimefilter("%d/%b/%Y") }}  
**Categories**: {{ writeup.metadata.categories|ghsearchlinks("https://github.com/7h3rAm/writeups") }}  
**Tags**: {{ writeup.metadata.tags|ghsearchlinks("https://github.com/7h3rAm/writeups") }}  
{% if writeup.metadata.infocard %}
**InfoCard**:  
![writeup.metadata.infocard]({{ writeup.metadata.infocard }})
{% endif %}

## Overview
{% if writeup.overview %}
{{ writeup.overview.description }}

### Killchain
{% if writeup.overview.killchain %}
![writeup.overview.killchain](./killchain.png)
{% endif %}

{% if writeup.overview.ttps and writeup.overview.ttps|length %}

### TTPs
{% for portmap in writeup.overview.ttps %}
{{ loop.index }}\. `{{ portmap }}`: {{ writeup.overview.ttps[portmap].split(" ")|anchorformatttps("https://github.com/7h3rAm/writeups") }}  
{% endfor %}

{% endif %}
{% endif %}

\newpage
{% if writeup.enumeration %}## Phase #1: Enumeration
{% if writeup.enumeration.steps %}
{% for step in writeup.enumeration.steps %}
{% set step_loop = loop %}
{{ loop.index }}\. {{ step.description|trim }}  
{% if step.command %}
``` {.python .numberLines}
{{ step.command }}
```
{% endif %}
{% if step.screenshot and step.screenshot|length and step.screenshot[0] %}
{% for screenshot in step.screenshot %}

![writeup.enumeration.steps.{{ step_loop.index }}.{{ loop.index }}]({{ screenshot }})  
{% endfor %}
{% endif %}

{% endfor %}
{% endif %}

{% if writeup.enumeration.findings %}### Findings
{% if writeup.enumeration.findings.openports %}#### Open Ports
``` {.python .numberLines}
{{ writeup.enumeration.findings.openports|join("\n") }}
{% endif %}
```
{% if writeup.enumeration.findings.files %}#### Files
``` {.python .numberLines}
{{ writeup.enumeration.findings.files|join("\n") }}
```
{% endif %}
{% if writeup.enumeration.findings.users %}#### Users
``` {.python .numberLines}
{% for service in writeup.enumeration.findings.users %}
{{ service }}: {{ writeup.enumeration.findings.users[service]|join(", ") }}
{% endfor %}
```
{% endif %}
{% endif %}
{% endif %}

\newpage
{% if writeup.exploitation %}## Phase #2: Exploitation
{% if writeup.exploitation.steps %}
{% for step in writeup.exploitation.steps %}
{% set step_loop = loop %}
{{ loop.index }}\. {{ step.description|trim }}  
{% if step.command %}
``` {.python .numberLines}
{{ step.command }}
```
{% endif %}
{% if step.screenshot and step.screenshot|length and step.screenshot[0] %}
{% for screenshot in step.screenshot %}

![writeup.exploitation.steps.{{ step_loop.index }}.{{ loop.index }}]({{ screenshot }})  
{% endfor %}
{% endif %}

{% endfor %}
{% endif %}
{% endif %}

## Phase #2.5: Post Exploitation
``` {.python .numberLines}
{% if writeup.postexploit.id %}
{{ writeup.postexploit.user }}@{{ writeup.postexploit.hostname }}> id
{{ writeup.postexploit.id|trim }}
{{ writeup.postexploit.user }}@{{ writeup.postexploit.hostname }}>  
{% endif %}
{% if writeup.postexploit.uname %}
{{ writeup.postexploit.user }}@{{ writeup.postexploit.hostname }}> uname
{{ writeup.postexploit.uname|trim }}
{{ writeup.postexploit.user }}@{{ writeup.postexploit.hostname }}>  
{% endif %}
{% if writeup.postexploit.ifconfig %}
{{ writeup.postexploit.user }}@{{ writeup.postexploit.hostname }}> ifconfig
{{ writeup.postexploit.ifconfig|trim }}
{{ writeup.postexploit.user }}@{{ writeup.postexploit.hostname }}>  
{% endif %}
{% if writeup.postexploit.users %}
{{ writeup.postexploit.user }}@{{ writeup.postexploit.hostname }}> users
{{ writeup.postexploit.users|join("\n") }}
{% endif %}
```

\newpage
{% if writeup.privesc %}## Phase #3: Privilege Escalation
{% if writeup.privesc.steps %}
{% for step in writeup.privesc.steps %}
{% set step_loop = loop %}
{{ loop.index }}\. {{ step.description|trim }}  
{% if step.command %}
``` {.python .numberLines}
{{ step.command }}
```
{% endif %}
{% if step.screenshot and step.screenshot|length and step.screenshot[0] %}
{% for screenshot in step.screenshot %}

![writeup.privesc.steps.{{ step_loop.index }}.{{ loop.index }}]({{ screenshot }})  
{% endfor %}
{% endif %}

{% endfor %}
{% endif %}
{% endif %}

\newpage
{% if writeup.learning and writeup.learning|length and writeup.learning[0] %}## Learning/Recommendation
{% for learning in writeup.learning %}
* {{ learning }}
{% endfor %}
{% endif %}

{% if writeup.loot %}## Loot
{% if writeup.loot.hashes and writeup.loot.hashes|length > 0 and writeup.loot.hashes[0] != None %}### Hashes
``` {.python .numberLines}
{{ writeup.loot.hashes|obfuscate|join("\n") }}
```
{% endif %}
{% if writeup.loot.credentials and writeup.loot.credentials|length > 0 and writeup.loot.credentials[0] != None %}### Credentials
``` {.python .numberLines}
{% for service in writeup.loot.credentials %}
{{ service }}: {{ writeup.loot.credentials[service]|obfuscate|join(", ") }}
{% endfor %}
```
{% endif %}
{% if writeup.loot.flags and writeup.loot.flags|length > 0 and writeup.loot.flags[0] != None %}### Flags
``` {.python .numberLines}
{{ writeup.loot.flags|obfuscate|join("\n") }}
```
{% endif %}
{% endif %}

{% if writeup.metadata.url or writeup.metadata.references %}## References
{% if writeup.metadata.url %}
[+] <{{ writeup.metadata.url }}>  
{% endif %}
{% for reference in writeup.metadata.references %}
[+] <{{ reference }}>  
{% endfor %}
{% endif %}
