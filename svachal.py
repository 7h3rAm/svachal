#!/usr/bin/env python3

import os
import sys
import shutil
import argparse
import datetime
import subprocess

import yaml
import jinja2 as jinja
import markdown2 as markdown

import utils
import yml2dot


class Svachal:
  def __init__(self, writeupdir, githubrepourl):
    self.config = {}

    self.config["writeupdir"] = writeupdir
    self.config["githubrepourl"] = githubrepourl
    # update the template.writeup.md and template.readme.md file with correct pdf metadata and github repo url

    self.config["basedir"] = os.path.dirname(os.path.realpath(__file__))

    self.config["machinesjson"] = "%s/.machines.json" % (utils.expand_env(var="$HOME"))

    self.config["metayml"] = "%s/meta.yml" % (self.config["writeupdir"])
    self.config["summaryyml"] = "%s/summary.yml" % (self.config["writeupdir"])

    self.config["templatedir"] = self.config["basedir"]
    self.config["templatefile"] = "template.writeup.md"
    self.config["templateyml"] = "%s/template.writeup.yml" % (self.config["basedir"])

    self.config["topcount"] = 10
    self.config["ttpscsv"] = "%s/ttps.csv" % (self.config["writeupdir"])

    self.machinesstats = utils.load_json(self.config["machinesjson"])

    self.y2d = yml2dot.YML2DOT(fontsize="large", addrootnode=False, rankdirlr=False, randomnodecolor=False, savehtml=False)
    self.summary = None

  def md2pdf(self, destdir, mdname, pdfname):
    results = subprocess.run(['pandoc', '%s/%s' % (destdir, mdname), '-o', '%s/%s' % (destdir, pdfname), '--from', 'markdown+yaml_metadata_block+raw_html', '--highlight-style', 'tango', '--pdf-engine=xelatex'], cwd=destdir, stdout=subprocess.PIPE).stdout.decode('utf-8')

  def yml2md(self, ymlfile, templatefile, templatedir, destdir, destfile, ignoreprivate=False):
    dictyml = utils.load_yaml(ymlfile)

    if not ignoreprivate:
      if dictyml.get("writeup") and dictyml["writeup"]["metadata"]["status"].lower().strip() == "private":
        #utils.warn("writeup file '%s' is not marked for publishing (status == private)" % (ymlfile))
        return

    env = jinja.Environment(loader=jinja.FileSystemLoader(templatedir), trim_blocks=True, lstrip_blocks=True)
    env.filters["datetimefilter"] = utils.datetimefilter
    env.filters["ghsearchlinks"] = utils.ghsearchlinks
    env.filters["anchorformat"] = utils.anchorformat
    env.filters["mdurl"] = utils.mdurl
    env.filters["obfuscate"] = utils.obfuscate
    env.filters["monojoin"] = utils.monojoin
    env.filters["customsort"] = utils.customsort
    template = env.get_template(templatefile)
    rendermd = template.render(dictyml)
    destfilepath = "%s/%s" % (destdir, destfile)
    utils.file_save(destfilepath, rendermd)
  
    if "summary.yml" not in ymlfile:
      if dictyml["writeup"].get("overview") and dictyml["writeup"]["overview"]["killchain"]:
        try:
          parentdir = "/".join(ymlfile.split("/")[:-1])
          dotfile = "%s/killchain.dot" % (parentdir)
          killchain = self.y2d.process(dictyml["writeup"]["overview"]["killchain"], dotfile)
        except Exception as ex:
          print("exception! failed to create overview killchain '%s'. please check below for more details:" % (destfile))
          print(repr(ex))

      try:
        self.md2pdf(destdir, destfile, "writeup.pdf")
      except Exception as ex:
        print("exception! md file '%s' could not be converted to pdf. please check below for more details:" % (destfile))
        print(repr(ex))

    return destfilepath

  def plot(self):
    utils.to_xkcd(
      plotdict=dict(sorted(sorted(self.summary["plot"]["ports"].items(), key=lambda x: x[1], reverse=True)[:self.config["topcount"]])),
      filename="%s/top_ports.png" % (self.config["writeupdir"]),
      title="Top Ports",
      rotate=True
    )
    utils.to_xkcd(
      plotdict=dict(sorted(sorted(self.summary["plot"]["protocols"].items(), key=lambda x: x[1], reverse=True)[:self.config["topcount"]])),
      filename="%s/top_protocols.png" % (self.config["writeupdir"]),
      title="Top Protocols",
      rotate=True
    )
    utils.to_xkcd(
      plotdict=dict(sorted(sorted(self.summary["plot"]["services"].items(), key=lambda x: x[1], reverse=True)[:self.config["topcount"]])),
      filename="%s/top_services.png" % (self.config["writeupdir"]),
      title="Top Services",
      rotate=True
    )

    utils.to_xkcd(
      plotdict=dict(sorted(sorted(self.summary["plot"]["categories"].items(), key=lambda x: x[1], reverse=True)[:self.config["topcount"]])),
      filename="%s/top_categories.png" % (self.config["writeupdir"]),
      title="Top Categories",
      rotate=True
    )

    plotdict = {k: v for k, v in self.summary["plot"]["ttps"].items() if k.startswith("enumerate_")}
    utils.to_xkcd(
      plotdict=dict(sorted(sorted(plotdict.items(), key=lambda x: x[1], reverse=True)[:self.config["topcount"]])),
      filename="%s/top_ttps_enumerate.png" % (self.config["writeupdir"]),
      title="Top TTPs - Phase #1 Enumeration",
      rotate=True
    )
    plotdict = {k: v for k, v in self.summary["plot"]["ttps"].items() if k.startswith("exploit_")}
    utils.to_xkcd(
      plotdict=dict(sorted(sorted(plotdict.items(), key=lambda x: x[1], reverse=True)[:self.config["topcount"]])),
      filename="%s/top_ttps_exploit.png" % (self.config["writeupdir"]),
      title="Top TTPs - Phase #2 Exploitation",
      rotate=True
    )
    plotdict = {k: v for k, v in self.summary["plot"]["ttps"].items() if k.startswith("privesc_")}
    utils.to_xkcd(
      plotdict=dict(sorted(sorted(plotdict.items(), key=lambda x: x[1], reverse=True)[:self.config["topcount"]])),
      filename="%s/top_ttps_privesc.png" % (self.config["writeupdir"]),
      title="Top TTPs - Phase #3 Privilege Escalation",
      rotate=True
    )

  def url2metadata(self, url):
    def search_by_key(data, machines, key="url"):
      if machines and len(machines):
        for entry in machines:
          if key in ["name"]:
            if data in entry[key].lower().strip():
              return entry
          if key in ["url"]:
            if data == entry[key].lower().strip():
              return entry
          elif key in ["id"]:
            if data == entry[key]:
              return entry
    url = url.lower().strip()
    stats, infra = None, ""
    writeupyml = utils.load_yaml(self.config["templateyml"])
    writeupyml["writeup"]["metadata"]["infocard"] = "./infocard.png"
    writeupyml["writeup"]["metadata"]["references"] = [""]
    writeupyml["writeup"]["metadata"]["status"] = "private"
    writeupyml["writeup"]["metadata"]["tags"] = ["enumerate_", "exploit_", "privesc_"]
    writeupyml["writeup"]["metadata"]["datetime"] = datetime.datetime.today().strftime("%Y%m%d")
    writeupyml["writeup"]["metadata"]["url"] = url
    writeupyml["writeup"]["metadata"]["name"] = "unknown"
    writeupyml["writeup"]["metadata"]["points"] = None
    writeupyml["writeup"]["metadata"]["categories"] = []
    writeupyml["writeup"]["metadata"]["infra"] = "misc"
    writeupyml["writeup"]["metadata"]["path"] = "misc.unknown"
    stats = search_by_key(url, self.machinesstats["machines"], key="url")
    if stats:
      writeupyml["writeup"]["metadata"]["name"] = "'%s'" % (stats["name"])
      writeupyml["writeup"]["metadata"]["points"] = stats["points"] if stats["points"] else None
      writeupyml["writeup"]["metadata"]["matrix"] = stats["matrix"]
      writeupyml["writeup"]["metadata"]["categories"].append(stats["os"].lower())
      if stats["oscplike"]:
        writeupyml["writeup"]["metadata"]["categories"].append("oscp")
      if stats["infrastructure"] in ["htb", "hackthebox"]:
        writeupyml["writeup"]["metadata"]["infra"] = "HackTheBox"
        writeupyml["writeup"]["metadata"]["categories"].append("hackthebox")
        writeupyml["writeup"]["metadata"]["path"] = "htb.%s" % (utils.cleanup_name(stats["shortname"]))
      elif stats["infrastructure"] in ["vh", "vulnhub"]:
        writeupyml["writeup"]["metadata"]["infra"] = "VulnHub"
        writeupyml["writeup"]["metadata"]["categories"].append("vulnhub")
        writeupyml["writeup"]["metadata"]["path"] = "vulnhub.%s" % (utils.cleanup_name(stats["shortname"]))
    return writeupyml["writeup"]["metadata"]

  def metadata2yml(self, metadata):
    formattedyml = """writeup:
  metadata:
    status: %s
    datetime: %s
    infra: %s
    name: %s
    points: %s
    path: %s
    url: %s
    infocard: %s
    references:
%s
    categories:
%s
    tags:
%s
  overview:
    description: |
      This is a writeup for %s VM [`%s`](%s). Here's an overview of the `enumeration` → `exploitation` → `privilege escalation` process:""" % (
        metadata["status"] if metadata["status"] else "",
        metadata["datetime"] if metadata["datetime"] else "",
        metadata["infra"] if metadata["infra"] else "",
        metadata["name"] if metadata["name"] else "",
        metadata["points"] if metadata["points"] else "",
        metadata["path"] if metadata["path"] else "",
        metadata["url"] if metadata["url"] else "",
        metadata["infocard"] if metadata["infocard"] else "",
        "\n".join(["      - %s" % (x) for x in metadata["references"]]) if metadata["references"] else "      - ",
        "\n".join(["      - %s" % (x) for x in metadata["categories"]]) if metadata["categories"] else "      - ",
        "\n".join(["      - %s" % (x) for x in metadata["tags"]]) if metadata["tags"] else "      - ",
        metadata["infra"] if metadata["infra"] else "",
        metadata["name"] if metadata["name"] else "",
        metadata["url"] if metadata["url"] else "",
      )
    return formattedyml

  def opcode_start(self, args, manual=False):
    if manual:
      if len(args.split(".", 1)) != 2:
        return
      metadata = {}
      metadata["status"] = "private"
      metadata["tags"] = ["enumerate_", "exploit_", "privesc_"]
      metadata["datetime"] = datetime.datetime.today().strftime("%Y%m%d")
      metadata["infra"] = args.split(".", 1)[0].upper()
      metadata["name"] = args.split(".", 1)[1].title()
      metadata["points"] = None
      metadata["path"] = args.lower()
      metadata["url"] = None
      metadata["infocard"] = None
      metadata["references"] = None
      metadata["categories"] = ["oscp", "vulnhub/htb/thm", "linux/windows/bsd"]
      self.config["destdirname"] = args
    else:
      url = args
      metadata = self.url2metadata(url)
      print(self.metadata2yml(metadata))
      print()
      self.config["destdirname"] = metadata["path"]

    self.config["destdirpath"] = "%s/%s" % (self.config["writeupdir"], self.config["destdirname"])
    self.config["writeupyml"] = "%s/writeup.yml" % (self.config["destdirpath"])
    if not os.path.isfile(self.config["writeupyml"]):
      utils.mkdirp(self.config["destdirpath"])
      writeupyml = utils.file_open(self.config["templateyml"])
      updatedwriteupyml = "%s\n%s" % (self.metadata2yml(metadata), "\n".join(writeupyml.split("\n")[23:]))
      utils.file_save(self.config["writeupyml"], updatedwriteupyml)
      utils.info("writeup file '%s' created for target '%s'" % (self.config["writeupyml"], self.config["destdirname"]))
      for machine in self.machinesstats["machines"]:
        if machine["url"] == metadata["url"]:
          utils.to_sparklines(machine["difficulty_ratings"] if machine["difficulty_ratings"] else [], filename="%s/ratings.png" % (self.config["destdirpath"]))
          utils.info("created '%s/ratings.png' file for target '%s'" % (self.config["destdirpath"], self.config["destdirname"]))
          url = "https://quickchart.io/chart?bkg=rgba(255,255,255,0.2)&width=270&height=200&c={ type: 'radar', data: {fill: 'False', labels: ['Enumeration', 'Real-Life', 'CVE', ['Custom', 'Exploitation'], 'CTF-Like'], datasets: [{ label: 'User rated', data: %s, backgroundColor:'rgba(154,204,20,0.2)', borderColor:'rgb(154,204,20)', pointBackgroundColor:'rgb(154,204,20)' }, { label: 'Maker rated', data: %s, backgroundColor:'rgba(86,192,224,0.2)', borderColor:'rgb(86,192,224)', pointBackgroundColor:'rgb(86,192,224)' }] }, options: { layout:{ padding:25}, plugins: { legend: false,}, scale: { angleLines: { display: true, color: 'rgb(21,23,25)' }, ticks: { callback: function() {return ''}, backdropColor: 'rgba(0, 0, 0, 0)' }, gridLines: { color: 'rgb(51,54,60)', } }, } }" % (machine["matrix"]["aggregate"], machine["matrix"]["maker"])
          res = utils.get_http_res(url, requoteuri=True)
          filename = "%s/matrix.png" % (self.config["destdirpath"])
          with open(filename, "wb") as fp:
            fp.write(res.content)
          utils.info("created '%s/matrix.png' file for target '%s'" % (self.config["destdirpath"], self.config["destdirname"]))
    else:
      utils.warn("writeup file '%s' already exists for target '%s'" % (self.config["writeupyml"], self.config["destdirname"]))

  def opcode_finish(self):
    self.config["destdirpath"] = "."
    self.config["writeupyml"] = "%s/writeup.yml" % (self.config["destdirpath"])
    if not os.path.isfile(self.config["writeupyml"]):
      utils.error("could not find writeup file '%s'" % (self.config["writeupyml"]))
    else:
      self.yml2md(self.config["writeupyml"], self.config["templatefile"], self.config["templatedir"], self.config["destdirpath"], "writeup.md", ignoreprivate=True)

  def opcode_rebuildall(self):
    writeupdirs = [x.replace("/writeup.yml", "").split("/")[-1] for x in utils.search_files_yml(self.config["writeupdir"])]
    total = len(writeupdirs)
    privatewriteups = []
    for idx, wd in enumerate(sorted(writeupdirs, key=str.casefold)):
      destdirpath = "%s/%s" % (self.config["writeupdir"], wd)
      writeupyml = "%s/writeup.yml" % (destdirpath)
      destfilepath = self.yml2md(writeupyml, self.config["templatefile"], self.config["templatedir"], destdirpath, "writeup.md")
      print("(%03d/%03d) '%s' → '%s'" % (idx+1, total, writeupyml, destfilepath))
      if not destfilepath:
        privatewriteups.append(writeupyml)
    utils.info("rebuilt %d writeups @ %s (private: %d)" % (total-len(privatewriteups), self.config["writeupdir"], len(privatewriteups)))

  def opcode_summarize(self):
    metadict = utils.load_yaml(self.config["metayml"])
    self.summary = {
      "stats": {
        "counts": "",
        "owned": "",
      },
      "counts": {
        "totalvh": 0,
        "totalhtb": 0,
        "totalnix": 0,
        "totalwindows": 0,
        "total": 0,
        "writeups": 0,
        "percent": 0.0,
        "writeupsnix": 0,
        "writeupswindows": 0,
        "percentnix": 0.0,
        "percentwindows": 0.0,
        "writeupsvh": 0,
        "writeupshtb": 0,
        "percentvh": 0.0,
        "percenthtb": 0.0,
      },
      "loot": {
        "hashes": [],
        "credentials": [],
      },
      "plot": {
        "ports": {},
        "protocols": {},
        "services": {},
        "ttps": {},
        "categories": {},
      },
      "readme": [],
      "ttpsitw": {},
      "techniques": {
        "enumerate": metadict["meta"]["ttps"]["enumerate"],
        "exploit": metadict["meta"]["ttps"]["exploit"],
        "privesc": metadict["meta"]["ttps"]["privesc"],
      },
      "tips": metadict["meta"]["tips"],
      "tools": metadict["meta"]["tools"],
      "methodology": metadict["meta"]["methodology"],
    }

    for key in self.machinesstats["counts"]:
      self.summary["counts"][key] = self.machinesstats["counts"][key]

    writeupdirs = [x.replace("/writeup.yml", "").split("/")[-1] for x in utils.search_files_yml(self.config["writeupdir"])]
    total, private, machines = len(writeupdirs), [], []
    for idx, wd in enumerate(sorted(writeupdirs, key=str.casefold)):
      destdirpath = "%s/%s" % (self.config["writeupdir"], wd)
      writeupyml = "%s/writeup.yml" % (destdirpath)
      print("%s summarizing '%s'" % (utils.blue_bold("(%03d/%03d)" % (idx+1, total)), writeupyml))
      dictyml = utils.load_yaml(writeupyml)

      writeupmdurl = "%s/blob/master/%s/writeup.md" % (self.config["githubrepourl"], dictyml["writeup"]["metadata"]["path"])
      writeuppdfurl = "%s/blob/master/%s/writeup.pdf" % (self.config["githubrepourl"], dictyml["writeup"]["metadata"]["path"])
      killchainurl = "%s/blob/master/%s/killchain.png" % (self.config["githubrepourl"], dictyml["writeup"]["metadata"]["path"])

      dictyml["writeup"]["machine"] = {}
      dictyml["writeup"]["machine"]["name"] = dictyml["writeup"]["metadata"]["name"]
      dictyml["writeup"]["machine"]["url"] = dictyml["writeup"]["metadata"]["url"]
      dictyml["writeup"]["machine"]["writeupmdurl"] = writeupmdurl
      dictyml["writeup"]["machine"]["writeuppdfurl"] = writeuppdfurl
      dictyml["writeup"]["machine"]["killchainurl"] = killchainurl
      dictyml["writeup"]["machine"]["ratingsurl"] = None
      dictyml["writeup"]["machine"]["matrixurl"] = None
      dictyml["writeup"]["machine"]["private"] = True if dictyml["writeup"]["metadata"]["status"].lower().strip() == "private" else False
      dictyml["writeup"]["machine"]["verbose_id"] = "%s#%s" % (dictyml["writeup"]["metadata"]["infra"].lower().strip(), dictyml["writeup"]["metadata"]["name"].lower().strip())
      dictyml["writeup"]["machine"]["oscplike"] = True
      dictyml["writeup"]["machine"]["owned_user"] = True if dictyml["writeup"]["metadata"]["status"].lower().strip() == "public" else False
      dictyml["writeup"]["machine"]["owned_root"] = True if dictyml["writeup"]["metadata"]["status"].lower().strip() == "public" else False
      if "linux" in dictyml["writeup"]["metadata"]["categories"]:
        dictyml["writeup"]["machine"]["os"] = "Linux"
      elif "windows" in dictyml["writeup"]["metadata"]["categories"]:
        dictyml["writeup"]["machine"]["os"] = "Windows"
      elif "bsd" in dictyml["writeup"]["metadata"]["categories"]:
        dictyml["writeup"]["machine"]["os"] = "BSD"
      else:
        dictyml["writeup"]["machine"]["os"] = "Unknown"

      tracked = False
      for machine in self.machinesstats["machines"]:
        if machine["url"] == dictyml["writeup"]["metadata"]["url"]:
          dictyml["writeup"]["machine"] = machine
          dictyml["writeup"]["machine"]["writeupmdurl"] = writeupmdurl
          dictyml["writeup"]["machine"]["writeuppdfurl"] = writeuppdfurl
          dictyml["writeup"]["machine"]["killchainurl"] = killchainurl
          dictyml["writeup"]["machine"]["private"] = True if dictyml["writeup"]["metadata"]["status"].lower().strip() == "private" else False
          if dictyml["writeup"]["machine"].get("difficulty_ratings") and dictyml["writeup"]["machine"]["difficulty_ratings"]:
            dictyml["writeup"]["machine"]["ratingsurl"] = "%s/blob/master/%s/ratings.png" % (self.config["githubrepourl"], dictyml["writeup"]["metadata"]["path"])
            dictyml["writeup"]["machine"]["matrixurl"] = "%s/blob/master/%s/matrix.png" % (self.config["githubrepourl"], dictyml["writeup"]["metadata"]["path"])
          else:
            dictyml["writeup"]["machine"]["ratingsurl"] = None
            dictyml["writeup"]["machine"]["matrixurl"] = None
          tracked = True
          break
      machines.append(dictyml["writeup"]["machine"])

      if dictyml["writeup"]["metadata"]["status"].lower().strip() == "private":
        private.append(dictyml)
        continue

      if "vulnhub" in dictyml["writeup"]["metadata"]["categories"] and "linux" in dictyml["writeup"]["metadata"]["categories"]:
        self.summary["counts"]["writeupsvh"] += 1
        self.summary["counts"]["writeupsnix"] += 1
      if "vulnhub" in dictyml["writeup"]["metadata"]["categories"] and "windows" in dictyml["writeup"]["metadata"]["categories"]:
        self.summary["counts"]["writeupsvh"] += 1
        self.summary["counts"]["writeupswindows"] += 1
      if "htb" in dictyml["writeup"]["metadata"]["categories"] and "linux" in dictyml["writeup"]["metadata"]["categories"]:
        self.summary["counts"]["writeupshtb"] += 1
        self.summary["counts"]["writeupsnix"] += 1
      if "htb" in dictyml["writeup"]["metadata"]["categories"] and "windows" in dictyml["writeup"]["metadata"]["categories"]:
        self.summary["counts"]["writeupshtb"] += 1
        self.summary["counts"]["writeupswindows"] += 1
      self.summary["counts"]["writeups"] = self.summary["counts"]["writeupsvh"] + self.summary["counts"]["writeupshtb"]
      self.summary["counts"]["percent"] = "%.2f" % ((self.summary["counts"]["writeups"] / self.summary["counts"]["totaloscplike"]) * 100)
      self.summary["counts"]["percentvh"] = "%.2f" % ((self.summary["counts"]["writeupsvh"] / self.summary["counts"]["vhoscplike"]) * 100)
      self.summary["counts"]["percenthtb"] = "%.2f" % ((self.summary["counts"]["writeupshtb"] / self.summary["counts"]["htboscplike"]) * 100)
      self.summary["counts"]["percentnix"] = "%.2f" % ((self.summary["counts"]["writeupsnix"] / self.summary["counts"]["totalnix"]) * 100)
      self.summary["counts"]["percentwindows"] = "%.2f" % ((self.summary["counts"]["writeupswindows"] / self.summary["counts"]["totalwindows"]) * 100)

      # uncomment lines below if matrix.png has to be updated
      #if machine.get("matrix"):
      #  utils.to_sparklines(machine["difficulty_ratings"] if machine["difficulty_ratings"] else [], filename="%s/ratings.png" % (destdirpath))
      #  url = "https://quickchart.io/chart?bkg=rgba(255,255,255,0.2)&width=270&height=200&c={ type: 'radar', data: {fill: 'False', labels: ['Enumeration', 'Real-Life', 'CVE', ['Custom', 'Exploitation'], 'CTF-Like'], datasets: [{ label: 'User rated', data: %s, backgroundColor:'rgba(154,204,20,0.2)', borderColor:'rgb(154,204,20)', pointBackgroundColor:'rgb(154,204,20)' }, { label: 'Maker rated', data: %s, backgroundColor:'rgba(86,192,224,0.2)', borderColor:'rgb(86,192,224)', pointBackgroundColor:'rgb(86,192,224)' }] }, options: { layout:{ padding:25}, plugins: { legend: false,}, scale: { angleLines: { display: true, color: 'rgb(21,23,25)' }, ticks: { callback: function() {return ''}, backdropColor: 'rgba(0, 0, 0, 0)' }, gridLines: { color: 'rgb(51,54,60)', } }, } }" % (machine["matrix"]["aggregate"], machine["matrix"]["maker"])
      #  res = utils.get_http_res(url, requoteuri=True)
      #  filename = "%s/matrix.png" % (destdirpath)
      #  with open(filename, "wb") as fp:
      #    fp.write(res.content)

      for tag in dictyml["writeup"]["metadata"]["tags"]:
        if tag.startswith("enumerate_"):
          if None in self.summary["techniques"]["enumerate"][tag]["references"]:
            self.summary["techniques"]["enumerate"][tag]["references"] = []
          if "writeups" not in self.summary["techniques"]["enumerate"][tag]:
            self.summary["techniques"]["enumerate"][tag]["writeups"] = []
          self.summary["techniques"]["enumerate"][tag]["writeups"].append({
            "status": dictyml["writeup"]["metadata"]["status"],
            "datetime": dictyml["writeup"]["metadata"]["datetime"],
            "name": dictyml["writeup"]["metadata"]["name"],
            "url": dictyml["writeup"]["metadata"]["url"],
            "infra": dictyml["writeup"]["metadata"]["infra"],
            "points": dictyml["writeup"]["metadata"]["points"] if dictyml["writeup"]["metadata"].get("points") else None,
            "tags": dictyml["writeup"]["metadata"]["tags"],
            "writeup": writeuppdfurl,
            "overview": '<img src="%s" width="100" height="100" />' % (killchainurl),
          })
        if tag.startswith("exploit_"):
          if None in self.summary["techniques"]["exploit"][tag]["references"]:
            self.summary["techniques"]["exploit"][tag]["references"] = []
          if "writeups" not in self.summary["techniques"]["exploit"][tag]:
            self.summary["techniques"]["exploit"][tag]["writeups"] = []
          self.summary["techniques"]["exploit"][tag]["writeups"].append({
            "status": dictyml["writeup"]["metadata"]["status"],
            "datetime": dictyml["writeup"]["metadata"]["datetime"],
            "name": dictyml["writeup"]["metadata"]["name"],
            "url": dictyml["writeup"]["metadata"]["url"],
            "infra": dictyml["writeup"]["metadata"]["infra"],
            "points": dictyml["writeup"]["metadata"]["points"] if dictyml["writeup"]["metadata"].get("points") else None,
            "tags": dictyml["writeup"]["metadata"]["tags"],
            "writeup": writeuppdfurl,
            "overview": '<img src="%s" width="100" height="100" />' % (killchainurl if dictyml["writeup"].get("overview") else killchainurl),
          })
        if tag.startswith("privesc_"):
          if None in self.summary["techniques"]["privesc"][tag]["references"]:
            self.summary["techniques"]["privesc"][tag]["references"] = []
          if "writeups" not in self.summary["techniques"]["privesc"][tag]:
            self.summary["techniques"]["privesc"][tag]["writeups"] = []
          self.summary["techniques"]["privesc"][tag]["writeups"].append({
            "status": dictyml["writeup"]["metadata"]["status"],
            "datetime": dictyml["writeup"]["metadata"]["datetime"],
            "name": dictyml["writeup"]["metadata"]["name"],
            "url": dictyml["writeup"]["metadata"]["url"],
            "infra": dictyml["writeup"]["metadata"]["infra"],
            "points": dictyml["writeup"]["metadata"]["points"] if dictyml["writeup"]["metadata"].get("points") else None,
            "tags": dictyml["writeup"]["metadata"]["tags"],
            "writeup": writeuppdfurl,
            "overview": '<img src="%s" width="100" height="100" />' % (killchainurl if dictyml["writeup"].get("overview") else killchainurl),
          })

      if dictyml["writeup"]["overview"].get("ttps"):
        for protokey in dictyml["writeup"]["overview"]["ttps"]:
          port, l4, proto, service = None, None, None, None
          try:
            port, l4, proto, service = protokey.split("/", 3)
          except:
            try:
              port, l4, proto = protokey.split("/", 2)
            except:
              port, l4 = protokey.split("/", 1)

          pl4 = "%s/%s" % (port, l4)
          if pl4 in self.summary["plot"]["ports"]:
            self.summary["plot"]["ports"][pl4] += 1
          else:
            self.summary["plot"]["ports"][pl4] = 1

          if proto:
            if proto in self.summary["plot"]["protocols"]:
              self.summary["plot"]["protocols"][proto] += 1
            else:
              self.summary["plot"]["protocols"][proto] = 1

          if service:
            if service in self.summary["plot"]["services"]:
              self.summary["plot"]["services"][service] += 1
            else:
              self.summary["plot"]["services"][service] = 1

      for cat in dictyml["writeup"]["metadata"]["categories"]:
        if cat in self.summary["plot"]["categories"]:
          self.summary["plot"]["categories"][cat] += 1
        else:
          self.summary["plot"]["categories"][cat] = 1

      for tag in dictyml["writeup"]["metadata"]["tags"]:
        if tag in self.summary["plot"]["ttps"]:
          self.summary["plot"]["ttps"][tag] += 1
        else:
          self.summary["plot"]["ttps"][tag] = 1

      self.summary["readme"].append({
        "status": dictyml["writeup"]["metadata"]["status"],
        "datetime": dictyml["writeup"]["metadata"]["datetime"],
        "name": dictyml["writeup"]["metadata"]["name"],
        "url": dictyml["writeup"]["metadata"]["url"],
        "infra": dictyml["writeup"]["metadata"]["infra"],
        "points": dictyml["writeup"]["metadata"]["points"] if dictyml["writeup"]["metadata"].get("points") else None,
        "tags": dictyml["writeup"]["metadata"]["tags"],
        "writeup": writeuppdfurl,
        "overview": '<img src="%s" width="100" height="100" />' % (killchainurl if dictyml["writeup"].get("overview") else killchainurl),
        "machine": dictyml["writeup"]["machine"],
      })

      if dictyml["writeup"]["overview"].get("ttps"):
        for protokey in dictyml["writeup"]["overview"]["ttps"]:
          port, l4, proto, service = None, None, None, None
          try:
            port, l4, proto, service = protokey.split("/", 3)
          except:
            try:
              port, l4, proto = protokey.split("/", 2)
            except:
              port, l4 = protokey.split("/", 1)
          ttpsitw = dictyml["writeup"]["overview"]["ttps"][protokey].split(" ")

          protokey = "/".join(protokey.split("/")[2:])
          if protokey == "":
            protokey = None

          if port not in self.summary["ttpsitw"]:
            self.summary["ttpsitw"][port] = {
              "port": port,
              "l4": l4,
              "ttps": [],
              "ttpsitw": ttpsitw,
              "protokeys": [protokey] if protokey else [],
              "writeups": [{"name": dictyml["writeup"]["metadata"]["name"], "verbose_id": dictyml["writeup"]["machine"]["verbose_id"], "url": writeuppdfurl}] if dictyml["writeup"]["machine"] else [],
            }
          else:
            self.summary["ttpsitw"][port]["ttpsitw"].extend(ttpsitw)
            if protokey:
              self.summary["ttpsitw"][port]["protokeys"].append(protokey)
            self.summary["ttpsitw"][port]["writeups"].append({"name": dictyml["writeup"]["metadata"]["name"], "verbose_id": dictyml["writeup"]["machine"]["verbose_id"], "url": writeuppdfurl})

          self.summary["ttpsitw"][port]["ttpsitw"] = sorted(list(set(self.summary["ttpsitw"][port]["ttpsitw"])), key=str.casefold)
          self.summary["ttpsitw"][port]["protokeys"] = sorted(list(set(self.summary["ttpsitw"][port]["protokeys"])), key=str.casefold)

      loot = []
      if dictyml["writeup"]["loot"].get("credentials"):
        for credtype in dictyml["writeup"]["loot"]["credentials"]:
          for entry in dictyml["writeup"]["loot"]["credentials"][credtype]:
            try:
              username, password = entry.split("/", 1)
            except:
              username, password = None, entry
            uniqkey = "%s,%s,%s" % (username, password, credtype)
            if uniqkey not in loot:
              self.summary["loot"]["credentials"].append({
                "username": username,
                "password": password,
                "credtype": credtype,
              })
              loot.append(uniqkey)

      if dictyml["writeup"]["loot"].get("hashes"):
        self.summary["loot"]["hashes"].extend([x for x in dictyml["writeup"]["loot"]["hashes"]])
      self.summary["loot"]["hashes"] = sorted(list(set(self.summary["loot"]["hashes"])), key=str.casefold)

    for ttp in self.summary["techniques"]["enumerate"]:
      if self.summary["techniques"]["enumerate"][ttp].get("ports"):
        for port in self.summary["techniques"]["enumerate"][ttp]["ports"]:
          if not port:
            continue
          port, l4 = port.split("/")
          if port not in self.summary["ttpsitw"]:
            self.summary["ttpsitw"][port] = {
              "port": port,
              "l4": l4,
              "ttps": [ttp],
              "ttpsitw": [],
              "protokeys": [],
              "writeups": [],
            }
          elif ttp not in self.summary["ttpsitw"][port]["ttps"]:
            self.summary["ttpsitw"][port]["ttps"].append(ttp)
    for ttp in self.summary["techniques"]["exploit"]:
      if self.summary["techniques"]["exploit"][ttp].get("ports"):
        for port in self.summary["techniques"]["exploit"][ttp]["ports"]:
          if not port:
            continue
          port, l4 = port.split("/")
          if port not in self.summary["ttpsitw"]:
            self.summary["ttpsitw"][port] = {
              "port": port,
              "l4": l4,
              "ttps": [ttp],
              "ttpsitw": [],
              "protokeys": [],
              "writeups": [],
            }
          elif ttp not in self.summary["ttpsitw"][port]["ttps"]:
            self.summary["ttpsitw"][port]["ttps"].append(ttp)
    for ttp in self.summary["techniques"]["privesc"]:
      if self.summary["techniques"]["privesc"][ttp].get("ports"):
        for port in self.summary["techniques"]["privesc"][ttp]["ports"]:
          if not port:
            continue
          port, l4 = port.split("/")
          if port not in self.summary["ttpsitw"]:
            self.summary["ttpsitw"][port] = {
              "port": port,
              "l4": l4,
              "ttps": [ttp],
              "ttpsitw": [],
              "protokeys": [],
              "writeups": [],
            }
          elif ttp not in self.summary["ttpsitw"][port]["ttps"]:
            self.summary["ttpsitw"][port]["ttps"].append(ttp)

    utils.show_machines(machines)

    self.plot()
    self.summary["stats"]["counts"] = self.stats_counts()
    self.summary["stats"]["owned"] = self.stats_owned(machines)

    ttpitwcsv = ["%s/%s,%s,%s,%s,%s" % (
      port,
      self.summary["ttpsitw"][port]["l4"],
      ";".join([x.replace(";", "") for x in self.summary["ttpsitw"][port]["protokeys"]]),
      ";".join(self.summary["ttpsitw"][port]["ttps"]),
      ";".join(self.summary["ttpsitw"][port]["ttpsitw"]),
      ";".join(["%s (%s)" % (x["name"], x["verbose_id"]) for x in self.summary["ttpsitw"][port]["writeups"]])) for port in self.summary["ttpsitw"]]

    with open(self.config["ttpscsv"], "w") as fp:
      fp.write("\n".join(ttpitwcsv))
      fp.write("\n")
    utils.info("updated %s with %d port-ttps mappings" % (self.config["ttpscsv"], len(ttpitwcsv)))

    utils.file_save(self.config["summaryyml"], utils.dict2yaml({"summary": self.summary}))
    utils.info("updated %s for %d writeups (private: %d)" % (self.config["summaryyml"], total-len(private), len(private)))

    self.yml2md(ymlfile=self.config["summaryyml"], templatefile="template.readme.md", templatedir=self.config["templatedir"], destdir=self.config["writeupdir"], destfile="readme.md")
    utils.info("updated %s/readme.md with new stats and metadata" % (self.config["writeupdir"]))

  def stats_counts(self):
    header, rows = ["#", "HackTheBox", "VulnHub", "OSCPlike", "Owned"], []
    rows.append("___".join([x for x in [
      "%s" % ("Total"),
      "`%s/%s (%s)`" % (self.summary["counts"]["ownedhtb"], self.summary["counts"]["totalhtb"], "%.2f%%" % (self.summary["counts"]["perhtb"])),
      "`%s/%s (%s)`" % (self.summary["counts"]["ownedvh"], self.summary["counts"]["totalvh"], "%.2f%%" % (self.summary["counts"]["pervh"])),
      "`%s/%s (%s)`" % (self.summary["counts"]["ownedoscplike"], self.summary["counts"]["totaloscplike"], "%.2f%%" % (self.summary["counts"]["peroscplike"])),
      "`%s/%s (%s)`" % (self.summary["counts"]["ownedtotal"], self.summary["counts"]["totaltotal"], "%.2f%%" % (self.summary["counts"]["pertotal"])),
    ]]))
    rows.append("___".join([str(x) for x in [
      "Windows",
      "`%s/%s (%s)`" % (self.summary["counts"]["ownedhtbwindows"], self.summary["counts"]["htbwindows"], "%.2f%%" % (self.summary["counts"]["perhtbwindows"])),
      "`%s/%s (%s)`" % (self.summary["counts"]["ownedvhwindows"], self.summary["counts"]["vhwindows"], "%.2f%%" % (self.summary["counts"]["pervhwindows"])),
      "`%s/%s (%s)`" % (self.summary["counts"]["ownedoscplikewindows"], self.summary["counts"]["oscplikewindows"], "%.2f%%" % (self.summary["counts"]["peroscplikewindows"])),
      "`%s/%s (%s)`" % (self.summary["counts"]["ownedwindows"], self.summary["counts"]["totalwindows"], "%.2f%%" % (self.summary["counts"]["perwindows"])),
    ]]))
    rows.append("___".join([str(x) for x in [
      "*nix",
      "`%s/%s (%s)`" % (self.summary["counts"]["ownedhtbnix"], self.summary["counts"]["htbnix"], "%.2f%%" % (self.summary["counts"]["perhtbnix"])),
      "`%s/%s (%s)`" % (self.summary["counts"]["ownedvhnix"], self.summary["counts"]["vhnix"], "%.2f%%" % (self.summary["counts"]["pervhnix"])),
      "`%s/%s (%s)`" % (self.summary["counts"]["ownedoscplikenix"], self.summary["counts"]["oscplikenix"], "%.2f%%" % (self.summary["counts"]["peroscplikenix"])),
      "`%s/%s (%s)`" % (self.summary["counts"]["ownednix"], self.summary["counts"]["totalnix"], "%.2f%%" % (self.summary["counts"]["pernix"])),
    ]]))
    rows.append("___".join([str(x) for x in [
      "OSCPlike",
      "`%s/%s (%s)`" % (self.summary["counts"]["ownedhtboscplike"], self.summary["counts"]["htboscplike"], "%.2f%%" % (self.summary["counts"]["perhtboscplike"])),
      "`%s/%s (%s)`" % (self.summary["counts"]["ownedvhoscplike"], self.summary["counts"]["vhoscplike"], "%.2f%%" % (self.summary["counts"]["pervhoscplike"])),
      "",
      "`%s/%s (%s)`" % (self.summary["counts"]["ownedoscplike"], self.summary["counts"]["totaloscplike"], "%.2f%%" % (self.summary["counts"]["peroscplike"])),
    ]]))
    return utils.get_table(header, rows, delim="___", markdown=True, colalign="center")

  def stats_owned(self, machines):
    header, rows = ["#", "Name", "Infra", "Killchain", "TTPs", "OS", "Points", "Owned", "OSCPlike"], []
    for machine in machines:
      if machine["owned_user"] or machine["owned_root"]:
        os = utils.to_emoji(machine["os"])
        difficulty = utils.to_emoji(machine["difficulty"]) if machine.get("difficulty") and machine["difficulty"] else utils.to_emoji("difficulty_unknown")
        if machine.get("owned_root") and machine["owned_root"]:
          owned, owned_tooltip = utils.to_emoji("access_root"), "access_root"
        elif machine.get("owned_user") and machine["owned_user"]:
          owned, owned_tooltip = utils.to_emoji("access_user"), "access_user"
        else:
          owned, owned_tooltip = "", "access_none"
        if machine["oscplike"]:
          oscplike, oscplike_tooltip = utils.to_emoji("oscplike"), "== oscplike"
        else:
          oscplike, oscplike_tooltip = utils.to_emoji("notoscplike"), "!= oscplike"
        name = "[%s](%s#machines)" % (self.config["githubrepourl"], machine["name"])
        infra = "[%s](%s)" % (machine["verbose_id"].replace("hackthebox", "htb").replace("vulnhub", "vh"), machine["url"])
        tags, matrix, rating, writeuppdfurl, killchainurl = [], None, None, None, ""
        for writeup in self.summary["readme"]:
          if machine["url"] == writeup["url"]:
            tags = writeup["tags"]
            matrix = '<img src="%s" width="59" height="59"/>' % (machine["matrixurl"]) if machine["matrixurl"] else None
            rating = '<img src="%s" width="59" height="20"/>' % (machine["ratingsurl"]) if machine["ratingsurl"] else None
            writeuppdfurl = machine["writeuppdfurl"]
            killchainurl = '<img src="%s" width="100" height="100"/>' % (machine["killchainurl"])
            if machine["matrixurl"] and machine["ratingsurl"]:
              name = "[%s](%s)<br/>%s<br/>%s" % (machine["name"], writeuppdfurl, '<img src="%s" width="59" height="59"/>' % (machine["matrixurl"]) if machine["matrixurl"] else "", '<img src="%s" width="59" height="20"/>' % (machine["ratingsurl"]) if machine["ratingsurl"] else "")
            elif machine["matrixurl"]:
              name = "[%s](%s)<br/>%s" % (machine["name"], writeuppdfurl, '<img src="%s" width="59" height="59"/>' % (machine["matrixurl"]) if machine["matrixurl"] else "")
            elif machine["ratingsurl"]:
              name = "[%s](%s)<br/>%s" % (machine["name"], writeuppdfurl, '<img src="%s" width="59" height="20"/>' % (machine["ratingsurl"]) if machine["ratingsurl"] else "")
            else:
              name = "[%s](%s)" % (machine["name"], writeuppdfurl)
        emptycols = [os, difficulty, owned, oscplike]
        os = "" if os == "⚪" else '[`%s`](foo "%s")' % (os, machine["os"])
        difficulty = "" if difficulty == "⚪" else '[`%s`](foo %s)' % (difficulty, '"%spts"' % (machine["points"]) if machine["points"] else "!= pts")
        owned = "" if owned == "⚪" else '[`%s`](foo "%s")' % (owned, owned_tooltip)
        oscplike = "" if oscplike == "⚪" else '[`%s`](foo "%s")' % (oscplike, oscplike_tooltip)
        rows.append("___".join(str(x) for x in [
          name,
          infra,
          killchainurl,
          utils.anchorformat(tags, self.config["githubrepourl"]),
          os,
          difficulty,
          owned,
          oscplike,
        ]))
    return(utils.get_table(header, ["%d.___%s" % (idx+1, x) for idx, x in enumerate(sorted(rows, key=str.casefold))], delim="___", markdown=True, colalign="center"))


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="%s (v%s)" % (utils.blue_bold("svachal"), utils.green_bold("0.1")))
  parser.add_argument('-w', '--writeupdir', required=False, action='store', help='override default writeup dir path')
  parser.add_argument('-g', '--githubrepourl', required=False, action='store', help='override default github repo url for writeups')

  sfgroup = parser.add_mutually_exclusive_group()
  sfgroup.add_argument('-s', '--start', required=False, action='store', help='initiate new writeup process (provide machine url)')
  sfgroup.add_argument('-m', '--manual', required=False, action='store', help='initiate new writeup process (provide infra.name)')
  sfgroup.add_argument('-f', '--finish', required=False, action='store_true', help='wrapup writeup process for $PWD writeup directory')
  sfgroup.add_argument('-r', '--rebuildall', required=False, action='store_true', help='rebuild all writeups (recreates md/pdf/killchain/matrix)')
  sfgroup.add_argument('-z', '--summarize', required=False, action='store_true', help='update summary.yml and readme.md with data from all writeups')
  args = parser.parse_args()

  if not args.writeupdir and not args.githubrepourl:
    svl = Svachal(
      writeupdir="%s/toolbox/repos/writeups" % (utils.expand_env(var="$HOME")),
      githubrepourl="https://github.com/7h3rAm/writeups",
    )
  elif not args.writeupdir or not args.githubrepourl:
    utils.error("must use both writeupdir and githubrepourl to keep links correct")
    utils.error("check usage below:")
    parser.print_help()
    sys.exit(1)
  else:
    svl = Svachal(writeupdir=args.writeupdir, githubrepourl=args.githubrepourl)

  if args.start:
    svl.opcode_start(args.start, manual=False)

  elif args.manual:
    svl.opcode_start(args.manual, manual=True)

  elif args.finish:
    svl.opcode_finish()

  elif args.rebuildall:
    svl.opcode_rebuildall()

  elif args.summarize:
    svl.opcode_summarize()

  else:
    parser.print_help()
