import os
import re
import glob
import json
import yaml
import errno
import codecs
import fnmatch
import datetime
import urllib.request

import requests
import sparkline
import prettytable
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt


def highlight(text, color="black", bold=False):
  resetcode = "\x1b[0m"
  color = color.lower().strip()
  if color == "black":
    colorcode = "\x1b[0;30m" if not bold else "\x1b[1;30m"
  elif color == "white":
    colorcode = "\x1b[0;37m" if not bold else "\x1b[1;37m"
  elif color == "red":
    colorcode = "\x1b[0;31m" if not bold else "\x1b[1;31m"
  elif color == "green":
    colorcode = "\x1b[0;32m" if not bold else "\x1b[1;32m"
  elif color == "yellow":
    colorcode = "\x1b[0;33m" if not bold else "\x1b[1;33m"
  elif color == "blue":
    colorcode = "\x1b[0;34m" if not bold else "\x1b[1;34m"
  elif color == "magenta":
    colorcode = "\x1b[0;35m" if not bold else "\x1b[1;35m"
  elif color == "cyan":
    colorcode = "\x1b[0;36m" if not bold else "\x1b[1;36m"
  else:
    colorcode = "\x1b[0;30m" if not bold else "\x1b[1;30m"
  return "%s%s%s" % (colorcode, text, resetcode)

def black(text):
  return highlight(text, color="black", bold=False)

def black_bold(text):
  return highlight(text, color="black", bold=True)

def white(text):
  return highlight(text, color="white", bold=False)

def white_bold(text):
  return highlight(text, color="white", bold=True)

def red(text):
  return highlight(text, color="red", bold=False)

def red_bold(text):
  return highlight(text, color="red", bold=True)

def green(text):
  return highlight(text, color="green", bold=False)

def green_bold(text):
  return highlight(text, color="green", bold=True)

def yellow(text):
  return highlight(text, color="yellow", bold=False)

def yellow_bold(text):
  return highlight(text, color="yellow", bold=True)

def blue(text):
  return highlight(text, color="blue", bold=False)

def blue_bold(text):
  return highlight(text, color="blue", bold=True)

def magenta(text):
  return highlight(text, color="magenta", bold=False)

def magenta_bold(text):
  return highlight(text, color="magenta", bold=True)

def cyan(text):
  return highlight(text, color="cyan", bold=False)

def cyan_bold(text):
  return highlight(text, color="cyan", bold=True)

def debug(text):
  print("%s %s" % (blue_bold("[*]"), text))

def info(text):
  print("%s %s" % (green_bold("[+]"), text))

def warn(text):
  print("%s %s" % (yellow_bold("[!]"), text))

def error(text):
  print("%s %s" % (red_bold("[-]"), text))

def expand_env(var="$HOME"):
  return os.environ[var.replace("$", "")]

def trim(text, maxq=40):
  return "%s..." % (text[:maxq]) if len(text) > maxq else text

def mkdirp(path):
  try:
    os.makedirs(path)
  except OSError as exc:
    if exc.errno == errno.EEXIST and os.path.isdir(path):
      pass
    else:
      raise

def search_files(dirpath="./", regex="*"):
  matches = []
  for root, dirnames, filenames in os.walk(dirpath):
    for filename in fnmatch.filter(filenames, regex):
      resultfile = os.path.join(root, filename)
      if os.path.exists(resultfile):
        matches.append(resultfile)
  fm = filter(lambda item: '/__pycache__'  not in item and '/results' not in item and '/.git' not in item and '/summary.yml' not in item and '/meta.yml' not in item and '/ttps.yml' not in item and '/test.ttp.yml' not in item, matches)
  return list(set(fm))

def search_files_all(dirpath):
  return search_files(dirpath, regex="*")

def search_files_yml(dirpath):
  return search_files(dirpath, regex="*.yml")

def search_files_md(dirpath):
  return search_files(dirpath, regex="*.md")

def download_json(url):
  with urllib.request.urlopen(url) as url:
    return json.loads(url.read().decode())

def load_json(filename):
  with open(filename) as fp:
    return json.load(fp)

def save_json(datadict, filename):
  with open(filename, "w", encoding="utf-8") as fp:
    json.dump(datadict, fp, ensure_ascii=False, indent=2, sort_keys=True)

def load_file(filename):
  lines = []
  with open(filename) as fp:
    lines = sorted(list(set(list(list(filter(None, fp.read().split("\n")))))))
  return lines

def save_file(datalist, filename):
  with open(filename, "w") as fp:
    fp.write("\n".join(sorted(list(set(list(list(filter(None, datalist))))))))
    fp.write("\n")

def load_yaml(filename):
  return yaml.safe_load(open(filename))

def save_yaml(datayml, filename):
  with open(filename, "w") as fp:
    yaml.dump(datayml, fp, default_flow_style=True)

def dict2yaml(datadict):
  return yaml.safe_dump(yaml.load(json.dumps(datadict), Loader=yaml.FullLoader), default_flow_style=False)

def file_open(filename):
  if filename and filename != "":
    with codecs.open(filename, mode="r", encoding="utf-8") as fo:
      return fo.read()

def file_save(filename, data, mode="w"):
  if filename and filename != "":
    if "/" in filename:
      mkdirp(os.path.dirname(filename))
    try:
      with codecs.open(filename, mode, encoding="utf-8") as fo:
        fo.write(data)
    except Exception as ex:
      with open(filename, mode) as fo:
        try:
          fo.write(data)
        except:
          fo.write(data.encode('utf-16', 'surrogatepass').decode('utf-16'))

def download(url, filename):
  res = requests.get(url)
  if res.status_code == 200:
    open(filename, "wb").write(res.content)

def get_http_res(url, headers={}, requoteuri=False):
  if requoteuri:
    return requests.get(cleanup_url(requests.utils.requote_uri(url)), headers=headers)
  else:
    return requests.get(cleanup_url(url), headers=headers)

def get_http(url, headers={}):
  res = requests.get(cleanup_url(url), headers=headers)
  if res.status_code == 200:
    return res.json()
  else:
    return {}

def post_http(url, data={}, headers={}):
  res = requests.post(cleanup_url(url), data=json.dumps(data), headers=headers)
  if res.status_code == 200:
    return res.json()
  else:
    return {}

def strip_html(data):
  return re.sub("\s+", " ", BeautifulSoup(data, "lxml").text)

def datetimefilter(datestr, format='%Y/%m/%d %H:%M:%S'):
  try:
    return datetime.datetime.strptime(str(datestr), '%Y%m%dT%H:%M:%SZ').strftime(format)
  except:
    return datetime.datetime.strptime(str(datestr), '%Y%m%d').strftime(format)

def cleanup_url(url):
  return url.replace("//", "/").replace(":/", "://")

def cleanup_name(name):
  return re.sub(r"[\W_]", "", name.lower())
  return name.lower().replace(" ", "").replace(":", "").replace("_", "").replace("-", "")

def ghsearchlinks(items, repourl, delim=", "):
  if isinstance(items, str):
    return "[`%s`](%s/search?q=%s&unscoped_q=%s)" % (items, repourl, items, items)
  else:
    return delim.join([ "[%s](%s/search?q=%s&unscoped_q=%s)" % (x, repourl, x, x) for x in items])

def anchorformat(items, repourl, delim=", "):
  if isinstance(items, str):
    if items.startswith("enumerate_") or items.startswith("exploit_") or items.startswith("privesc_"):
      return "[`%s`](%s#%s)" % (items, repourl, items)
    else:
      return ghsearchlinks(items, repourl)
  else:
    results = []
    for x in items:
      if x.startswith("enumerate_") or x.startswith("exploit_") or x.startswith("privesc_"):
        results.append("[`%s`](%s#%s)" % (x, repourl, x))
      else:
        results.append(ghsearchlinks(x, repourl))
    return delim.join(results)

def anchorformatttps(items, repourl="https://github.com/7h3rAm/writeups", delim=", "):
  if isinstance(items, str):
    if items.startswith("enumerate_") or items.startswith("exploit_") or items.startswith("privesc_"):
      return "[%s](%s#%s)" % (items, repourl, items)
    else:
      return ghsearchlinks(items, repourl)
  else:
    results = []
    for x in items:
      if x.startswith("enumerate_") or x.startswith("exploit_") or x.startswith("privesc_"):
        results.append("[%s](%s#%s)" % (x, repourl, x))
      else:
        results.append(ghsearchlinks(x, repourl))
    return delim.join(results)

def mdurl(datadict):
  results = []
  for item in datadict:
    results.append("[%s](%s)" % (item["name"], item["url"]))
  return "<br /><br />".join(results)

def obfuscate(data, mass=0.81, replchr="."):
  # calculate event horizon using the given mass
  # use eh to hide remaining data forever
  if isinstance(data, str):
    eh = int(len(data) * mass)
    return "".join([data[:eh], len(data[eh:])*replchr])
  else:
    results = []
    for x in data:
      eh = int(len(x) * mass)
      results.append("".join([x[:eh], len(x[eh:])*replchr]))
    return results

def monojoin(items):
  if isinstance(items, str):
    return "`%s`" % (items)
  else:
    results = []
    for x in items:
      results.append("`%s`" % (x))
    return "<br /><br />".join(results)

def customsort(items):
  return [str(y) for y in sorted([int(x) for x in items])]

def lookahead(iterable):
  # https://stackoverflow.com/a/1630350
  it = iter(iterable)
  last = next(it)
  for val in it:
    yield last, True
    last = val
  yield last, False

def yturl2verboseid(url):
  v, t = None, None
  for param in url.strip().split("?", 1)[1].split("&"):
    if param.startswith("v="):
      v = param.split("=")[1]
    if param.startswith("t="):
      t = param
  if v and t:
    return "youtu.be/%s?%s" % (v, t)
  elif v:
    return "youtu.be/%s" % (v)
  else:
    return url

def sparkify(difficulty):
  return sparkline.sparkify(difficulty)

def to_color_difficulty(sparkline):
  return "".join([green(sparkline[:3]), yellow(sparkline[3:7]), red(sparkline[7:])])

def to_emoji(text):
  text = str(text)
  # https://github.com/ikatyang/emoji-cheat-sheet
  if "private" == text.lower():
    return red("")
  elif "public" == text.lower():
    return green("")
  elif "oscplike" == text.lower():
    return magenta("")
  elif "access_root" == text.lower():
    return red("")
  elif "access_user" == text.lower():
    return yellow("")
  elif "android" in text.lower():
    return green("")
  elif "arm" in text.lower():
    return magenta("")
  elif "bsd" in text.lower():
    return red("")
  elif "linux" == text.lower():
    return yellow_bold("")
  elif "solaris" in text.lower():
    return magenta_bold("")
  elif "unix" in text.lower():
    return magenta("")
  elif "windows" == text.lower():
    return blue("")
  elif "other" in text.lower():
    return magenta("")
  elif "difficulty_unknown" == text.lower():
    return ""
  elif "easy" == text.lower():
    return cyan_bold("")
  elif "medium" == text.lower():
    return green_bold("")
  elif "hard" == text.lower():
    return yellow_bold("")
  elif "insane" == text.lower():
    return red_bold("")
  else:
    return ""

def to_markdown_table(pt):
  _junc = pt.junction_char
  if _junc != "|":
    pt.junction_char = "|"
  markdown = [row for row in pt.get_string().split("\n")[1:-1]]
  pt.junction_char = _junc
  return "\n".join(markdown)

def get_table(header, rows, delim="___", aligndict=None, markdown=False, colalign=None):
  table = prettytable.PrettyTable()
  table.field_names = header
  table.align = "c"; table.valign = "m"
  for row in rows:
    table.add_row(row.split(delim))
  if markdown:
    if colalign in ["left", "center", "right"]:
      if colalign == "left":
        return to_markdown_table(table).replace("|-", "|:")
      elif colalign == "center":
        return to_markdown_table(table).replace("-|-", ":|:").replace("|-", "|:").replace("-|", ":|")
      elif colalign == "right":
        return to_markdown_table(table).replace("-|", ":|")
    else:
      #return table.get_html_string()
      return to_markdown_table(table)
  else:
    if aligndict:
      for colheader in aligndict:
        table.align[colheader] = aligndict[colheader]
    else:
      table.align["#"] = "r"
      table.align["ID"] = "r"
      table.align["Name"] = "l"
      table.align["Expires"] = "l"
      table.align["Match"] = "l"
      table.align["Follow"] = "l"
      table.align["Private"] = "c"
      table.align["Rating"] = "c"
      table.align["Difficulty"] = "c"
      table.align["OS"] = "c"
      table.align["OSCPlike"] = "c"
      table.align["Owned"] = "c"
    table.vertical_char = " "
    table.horizontal_char = "-"
    table.junction_char = " "
    return table.get_string()

def to_table(header, rows, delim="___", aligndict=None, markdown=False):
  print(get_table(header, rows, delim=delim, aligndict=aligndict, markdown=markdown))

def to_json(data):
  print(json.dumps(data, indent=2, sort_keys=True))

def to_gsheet(data):
  lines = []
  for item in data:
    name = "=HYPERLINK(\"%s\",\"%s\")" % (item["url"], item["name"])
    if "htb" in item["infrastructure"] or "hackthebox" in item["infrastructure"]:
      infra = "HackTheBox"
    elif "vh" in item["infrastructure"] or "vulnhub" in item["infrastructure"]:
      infra = "VulnHub"
    elif "thm" in item["infrastructure"] or "tryhackme" in item["infrastructure"]:
      infra = "TryHackMe"
    else:
      infra = "Misc"
    os = item["os"].title()
    points = item["points"] if item["points"] else ""
    owned = "Yes" if item["owned_user"] or item["owned_root"] else "No"
    lines.append("%s,%s,%s,%s,%s," % (name, infra, os, points, owned))
  print("Name,Infra,OS,Points,Difficulty,Owned,Writeup")
  for line in sorted(lines):
    print(line)

def show_machines(data, sort_key="name", jsonify=False, gsheet=False):
  if not len(data):
    return
  elif "success" in data:
    return to_json(data)
  elif jsonify:
    to_json(data)
  elif gsheet:
    to_gsheet(data)
  else:
    rows = []
    if "writeuppdfurl" in data[0]:
      header = ["#", "ID", "Name", "Private", "Rating", "Difficulty", "OS", "OSCPlike", "Owned"]
      for idx, entry in enumerate(sorted(data, key=lambda k: k[sort_key].lower())):
        mid = "%s%s" % (blue("%s#" % (entry["verbose_id"].split("#")[0])), blue_bold("%s" % (entry["verbose_id"].split("#")[1])))
        name = black_bold(entry["name"])
        os = to_emoji(entry["os"])
        difficulty = entry["difficulty"] if entry.get("difficulty") and entry["difficulty"] else "difficulty_unknown"
        rating = to_color_difficulty(sparkify(entry["difficulty_ratings"])) if entry.get("difficulty_ratings") else ""
        if entry.get("owned_root") and entry["owned_root"]:
          owned = "access_root"
        elif entry.get("owned_user") and entry["owned_user"]:
          owned = "access_user"
        else:
          owned = "access_none"
        oscplike = "oscplike" if entry.get("oscplike") and entry["oscplike"] else "notoscplike"
        private = to_emoji("private") if entry["private"] else to_emoji("public")
        rows.append("%s.___%s___%s___%s___%s___%s___%s___%s___%s" % (
        idx+1,
        mid,
        name,
        private,
        rating,
        to_emoji(difficulty),
        os,
        to_emoji(oscplike),
        to_emoji(owned),
      ))

    elif "expires_at" in data[0]:
      header = ["#", "ID", "Name", "Expires", "Rating", "Difficulty", "OS", "OSCPlike", "Owned"]
      for idx, entry in enumerate(sorted(data, key=lambda k: k[sort_key].lower())):
        mid = "%s%s" % (blue("%s#" % (entry["verbose_id"].split("#")[0])), blue_bold("%s" % (entry["verbose_id"].split("#")[1])))
        name = black_bold(entry["name"])
        os = to_emoji(entry["os"])
        difficulty = entry["difficulty"] if entry.get("difficulty") and entry["difficulty"] else "difficulty_unknown"
        rating = to_color_difficulty(sparkify(entry["difficulty_ratings"])) if entry.get("difficulty_ratings") else ""
        if entry.get("owned_root") and entry["owned_root"]:
          owned = "access_root"
        elif entry.get("owned_user") and entry["owned_user"]:
          owned = "access_user"
        else:
          owned = "access_none"
        oscplike = "oscplike" if entry.get("oscplike") and entry["oscplike"] else "notoscplike"
        rows.append("%s.___%s___%s___%s___%s___%s___%s___%s___%s" % (
        idx+1,
        mid,
        name,
        entry["expires_at"],
        rating,
        to_emoji(difficulty),
        os,
        to_emoji(oscplike),
        to_emoji(owned),
      ))

    elif "search_url" in data[0]:
      header = ["#", "ID", "Name", "Match", "Follow", "Rating", "Difficulty", "OS", "OSCPlike", "Owned"]
      for idx, entry in enumerate(sorted(data, key=lambda k: k[sort_key].lower())):
        mid = "%s%s" % (blue("%s#" % (entry["verbose_id"].split("#")[0])), blue_bold("%s" % (entry["verbose_id"].split("#")[1])))
        name = black_bold(entry["name"])
        match = trim(entry["search_text"].replace(" - ", " ").strip(), maxq=30) if entry.get("search_text") else ""
        follow = blue(entry["search_url"])
        os = to_emoji(entry["os"])
        difficulty = entry["difficulty"] if entry.get("difficulty") and entry["difficulty"] else "difficulty_unknown"
        rating = to_color_difficulty(sparkify(entry["difficulty_ratings"])) if entry.get("difficulty_ratings") else ""
        if entry.get("owned_root") and entry["owned_root"]:
          owned = "access_root"
        elif entry.get("owned_user") and entry["owned_user"]:
          owned = "access_user"
        else:
          owned = "access_none"
        oscplike = "oscplike" if entry.get("oscplike") and entry["oscplike"] else "notoscplike"
        rows.append("%s.___%s___%s___%s___%s___%s___%s___%s___%s___%s" % (
        idx+1,
        mid,
        name,
        match,
        follow,
        rating,
        to_emoji(difficulty),
        os,
        to_emoji(oscplike),
        to_emoji(owned),
      ))

    else:
      header = ["#", "ID", "Name", "Rating", "Difficulty", "OS", "OSCPlike", "Owned"]
      for idx, entry in enumerate(sorted(data, key=lambda k: k[sort_key].lower())):
        mid = "%s%s" % (blue("%s#" % (entry["verbose_id"].split("#")[0])), blue_bold("%s" % (entry["verbose_id"].split("#")[1])))
        name = black_bold(entry["name"])
        os = to_emoji(entry["os"])
        difficulty = entry["difficulty"] if entry.get("difficulty") and entry["difficulty"] else "difficulty_unknown"
        rating = to_color_difficulty(sparkify(entry["difficulty_ratings"])) if entry.get("difficulty_ratings") else ""
        if entry.get("owned_root") and entry["owned_root"]:
          owned = "access_root"
        elif entry.get("owned_user") and entry["owned_user"]:
          owned = "access_user"
        else:
          owned = "access_none"
        oscplike = "oscplike" if entry.get("oscplike") and entry["oscplike"] else "notoscplike"
        rows.append("%s.___%s___%s___%s___%s___%s___%s___%s" % (
        idx+1,
        mid,
        name,
        rating,
        to_emoji(difficulty),
        os,
        to_emoji(oscplike),
        to_emoji(owned),
      ))

    to_table(header=header, rows=rows, delim="___", aligndict=None, markdown=False)

def to_xkcd(plotdict, filename, title, rotate=True, trimlength=20):
  datadict = {}
  for key in plotdict:
    datadict[key] = [[key], [plotdict[key]]]
  with plt.xkcd():
    for idx, label in enumerate(datadict):
      plt.bar(datadict[label][0], datadict[label][1])
      text = "%s... (%d)" % ("".join(datadict[label][0][0][:trimlength]), datadict[label][1][0]) if len(label) >= trimlength else "%s (%d)" % (datadict[label][0][0], datadict[label][1][0])
      if rotate:
        angle = 90
        x, y = idx, 0.5
      else:
        angle = 0
        padding = (len(label)/2)/10
        x, y = idx-padding, datadict[label][1][0]-1
      plt.text(s=text, x=x, y=y, color="black", verticalalignment="center", horizontalalignment="left", size=15, rotation=angle, rotation_mode="anchor")
    plt.suptitle(title, fontsize=18, color="black")
    plt.gca().spines["left"].set_color("black")
    plt.gca().spines["bottom"].set_color("black")
    plt.gca().spines["left"].set_visible(False)
    plt.gca().spines["right"].set_visible(False)
    plt.gca().spines["top"].set_visible(False)
    plt.xticks([]); plt.yticks([])
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()

def to_sparklines(items, filename, transparent=True):
  colormap = ["#9acc14", "#9acc14", "#9acc14", "#f7af3e", "#f7af3e", "#f7af3e", "#f7af3e", "#db524b", "#db524b", "#db524b"]
  barlist = plt.bar([str(x) for x in range(len(items))], items, width=0.95)
  for i in range(len(items)):
    barlist[i].set_color(colormap[i])
  ax = plt.gca()
  ax.spines["bottom"].set_visible(False)
  ax.spines["left"].set_visible(False)
  ax.spines["right"].set_visible(False)
  ax.spines["top"].set_visible(False)
  plt.xticks([]); plt.yticks([])
  plt.tight_layout()
  plt.savefig(filename, dpi=300, transparent=transparent)
  plt.close()
