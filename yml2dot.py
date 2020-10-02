#!/usr/bin/env python3

from __future__ import print_function
from pprint import pprint
import subprocess
import hashlib
import secrets
import yaml
import sys
import re
import os

"""
https://stackoverflow.design/product/base/colors/

rgb(244, 248, 251) #f4f8fb
rgb(225, 236, 244) #e1ecf4
rgb(209, 229, 241) #d1e5f1
rgb(0, 119, 204)   #0077cc
rgb(91, 141, 177)  #5b8db1

rgb(253, 247, 227) #fdf7e3
rgb(251, 242, 212) #fbf2d4
rgb(241, 229, 188) #f1e5bc
rgb(206, 165, 27)  #cea51b

rgb(238, 248, 241) #eef8f1
rgb(220, 240, 226) #dcf0e2
rgb(202, 232, 212) #cae8d4
rgb(61, 143, 88)   #3d8f58

rgb(253, 243, 244) #fdf3f4
rgb(249, 211, 215) #f9d3d7
rgb(244, 180, 187) #f4b4bb
rgb(192, 45, 46)   #c02d2e 
"""


class YML2DOT:
  def __init__(self, rootnode="!@#$", fontsize="medium", addrootnode=True, rankdirlr=False, randomnodecolor=True, savehtml=False):
    self.nodesdict = {}
    self.nodes = []
    self.edges = []
    self.config = {
      "rootnode": rootnode,
      "fontsize": 18 if fontsize.strip().lower() == "large" else 16 if fontsize.strip().lower() == "medium" else 12,
      "rankdirlr": rankdirlr,
      "addrootnode": addrootnode,
      "randomnodecolor": randomnodecolor,
      "savehtml": savehtml,
      "ignorekeys": ["__metadata__"],
      "writeupyml": False,

      "cluster0": {
        "title": "",
        "colornode": "#e1ecf4",
        "colorborder": "#0077cc",
      },
      "cluster1": {
        "title": "Phase #1:Enumeration",
        "colornode": "#dcf0e2",
        "colorborder": "#3d8f58",
      },
      "cluster2": {
        "title": "Phase #2:Exploitation",
        "colornode": "#fbf2d4",
        "colorborder": "#cea51b",
      },
      "cluster3": {
        "title": "Phase #3:Privilege Escalation",
        "colornode": "#f9d3d7",
        "colorborder": "#c02d2e",
      },

      "colorpallete": ["#cceabb", "#ffe0ac", "#ffacb7", "#b5cbcc", "#becddb", "#c2d6e1", "#c5d0cc", "#cddeef", "#dad4d5", "#dce1e4", "#dee9e7", "#dfdada", "#e3f2f7", "#ece1db", "#eff0ea", "#f3dbbe", "#fac3ac", "#ffcaaf"],
      "colorborder": "#665957",
      "colorlink": "#85285d",
      "colorbg": "#ffffff",
      "coloredge": "#665957",
      "colornode": "#FFFFFF",
      "colorwriteuproot": "",
    }

  def md5(self, data):
    return hashlib.md5(data.encode('utf-8')).hexdigest()

  def get_edges(self, treedict, parent=None):
    if not parent and self.config["addrootnode"]:
      parent = self.config["rootnode"]
    if isinstance(treedict, dict):
      for key in treedict.keys():
        if key in self.config["ignorekeys"]:
          continue
        self.update_nodes_edges(parent, key)
        self.get_edges(treedict[key], parent=key)
    elif isinstance(treedict, list):
      for item in treedict:
        self.get_edges(item, parent=parent)
    elif isinstance(treedict, str):
      self.update_nodes_edges(parent, treedict)

  def update_nodes_edges(self, parent, child, indent=0, borderless=False):
    def update_nodes(node, spaces, indent, borderless):
      if node not in self.nodesdict:
        label, href, tooltip, image = node, None, node, None
        match = re.match(r'^{{\s*(.*)\s*}}$', node, re.M)
        if match:
          tooltip = match.groups()[0]
          label = tooltip
        match = re.match(r'^\[\s*(.*)\s*\]\s*\(\s*(.*)\s*\)$', node, re.M)
        if match:
          label, href = match.groups()
          tooltip = label
        match = re.match(r'^\[\s*(.*)\s*\]\s*\(\s*(.*)\s*\)\s*{{\s*(.*)\s*}}$', node, re.M)
        if match:
          label, href, tooltip = match.groups()

        match = re.match(r'^!\[\s*(.*)\s*\]\s*\(\s*(.*)\s*\)$', node, re.M)
        if match:
          label, image = match.groups()
          tooltip = label
        match = re.match(r'^!\[\s*(.*)\s*\]\s*\(\s*(.*)\s*\)\s*{{\s*(.*)\s*}}$', node, re.M)
        if match:
          label, image, tooltip = match.groups()

        nodecolor = secrets.choice(self.config["colorpallete"]) if self.config["randomnodecolor"] else self.config["colornode"]
        self.config["writeupyml"] = False
        bordercolor = self.config["colorborder"]
        if label.startswith("_ "):
          self.config["writeupyml"] = True
          self.config["cluster0"]["title"], label = label.split("_ ")[1].split("/")
          tooltip = self.config["cluster0"]["title"]
          nodecolor = self.config["cluster0"]["colornode"]
          bordercolor = self.config["cluster0"]["colorborder"]
        elif label.startswith(". "):
          self.config["writeupyml"] = True
          label = label.split(". ")[1]
          tooltip = self.config["cluster1"]["title"]
          nodecolor = self.config["cluster1"]["colornode"]
          bordercolor = self.config["cluster1"]["colorborder"]
        elif label.startswith(".. "):
          self.config["writeupyml"] = True
          label = label.split(".. ")[1]
          tooltip = self.config["cluster2"]["title"]
          nodecolor = self.config["cluster2"]["colornode"]
          bordercolor = self.config["cluster2"]["colorborder"]
        elif label.startswith("... "):
          self.config["writeupyml"] = True
          label = label.split("... ")[1]
          tooltip = self.config["cluster3"]["title"]
          nodecolor = self.config["cluster3"]["colornode"]
          bordercolor = self.config["cluster3"]["colorborder"]

        self.nodesdict[node] = {
          "nodeid": len(self.nodesdict),
          "label": label,
          "href": href,
          "image": image,
          "tooltip": tooltip,
          "color": nodecolor,
          "colorborder": bordercolor,
        }
        self.nodesdict[node]["colorborder"] = self.nodesdict[node]["color"] if borderless else self.nodesdict[node]["colorborder"]

        attribs = []

        if self.nodesdict[node]["image"]:
          attribs.append("label=\"\"")
          attribs.append("image=\"%s\"" % (self.nodesdict[node]["image"]))
        else:
          attribs.append("label=\"%s\"" % (self.nodesdict[node]["label"]))

        if self.nodesdict[node]["href"]:
          attribs.append("href=\"%s\"" % (self.nodesdict[node]["href"]))
          attribs.append("fontcolor=\"%s\"" % (self.config["colorlink"]))

        attribs.append("color=\"%s\"" % (self.nodesdict[node]["colorborder"]))
        attribs.append("fillcolor=\"%s\"" % (self.nodesdict[node]["color"]))
        attribs.append("tooltip=\"%s\"" % (self.nodesdict[node]["tooltip"]))
        self.nodes.append("%s%d[%s];" % (spaces, self.nodesdict[node]["nodeid"], " ".join(attribs)))

    spaces = " " * indent

    if parent:
      parent = parent.strip()
      update_nodes(parent, spaces, indent, borderless)
    if child:
      child = child.strip()
      update_nodes(child, spaces, indent, borderless)
    if parent and child:
      self.edges.append("%s%d -> %d [color=\"%s\"];" % (spaces, self.nodesdict[parent]["nodeid"], self.nodesdict[child]["nodeid"], self.config["coloredge"]))

  def process(self, ymldata, dotfile):
    ymlfile = dotfile.replace("dot", "yml")

    self.nodesdict = {}
    self.nodes = []
    self.edges = []

    self.get_edges(ymldata)
    self.nodes, self.edges = sorted(list(set(self.nodes))), sorted(list(set(self.edges)))

    dotgraph = []
    dotgraph.append("digraph G {")
    dotgraph.append("  rankdir=LR;" if self.config["rankdirlr"] else "  #rankdir=LR;")
    dotgraph.append("  nodesdictep=1.0; splines=\"ortho\"; K=0.6; overlap=scale; fixedsize=true; resolution=72; bgcolor=\"%s\"; outputorder=\"edgesfirst\";" % (self.config["colorbg"]))
    dotgraph.append("  node [fontname=\"courier\" fontsize=%s shape=box width=0.25 fillcolor=\"white\" style=\"filled,solid\"];" % (self.config["fontsize"]))
    dotgraph.append("  edge [style=solid color=\"%s\" penwidth=0.75 arrowhead=vee arrowsize=0.75 ];" % (self.config["coloredge"]))
    dotgraph.append("")
    dotgraph.extend(["  %s" % (x) for x in self.nodes])
    dotgraph.append("")
    dotgraph.append("  subgraph cluster_0 {")
    dotgraph.append("    node [style=\"filled,solid\"];")
    dotgraph.append("    label = \"%s\";" % (self.config["cluster0"]["title"] if self.config["writeupyml"] else os.path.basename(dotfile)))
    dotgraph.append("    color = \"%s\";" % (self.config["colorborder"]))
    dotgraph.extend(["    %s" % (x) for x in self.edges])
    dotgraph.append("  }")
    dotgraph.append("}")
    dotgraph.append("")
    with open(dotfile, "w") as fp:
      fp.write("\n".join(dotgraph))

    if self.config["savehtml"]:
      d3graph = []
      d3graph.append("<!DOCTYPE html>")
      d3graph.append("<meta charset=\"utf-8\">")
      d3graph.append("<body>")
      d3graph.append("<script src=\"https://d3js.org/d3.v5.min.js\"></script>")
      d3graph.append("<script src=\"https://unpkg.com/@hpcc-js/wasm@0.3.11/dist/index.min.js\"></script>")
      d3graph.append("<script src=\"https://unpkg.com/d3-graphviz@3.0.5/build/d3-graphviz.js\"></script>")
      d3graph.append("<div id=\"graph\" style=\"text-align: center;\"></div>")
      d3graph.append("<script>")
      d3graph.append("d3.select(\"#graph\").graphviz().renderDot(`")
      d3graph.extend(dotgraph)
      d3graph.append("`);")
      d3graph.append("</script>")
      htmlfile = "%s.html" % (".".join(dotfile.split(".")[:-1]))
      with open(htmlfile, "w") as fp:
        fp.write("\n".join(d3graph))

    pngfile = "%s.png" % (".".join(dotfile.split(".")[:-1]))
    subprocess.call("/usr/bin/dot -Tpng %s -o %s" % (dotfile, pngfile), shell=True)

    return dotgraph


if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("USAGE: %s <filename>" % (sys.argv[0]))
    sys.exit(1)

  if not os.path.exists(sys.argv[-1]):
    print("no such file: %s" % (sys.argv[-1]))
    sys.exit(2)

  infilename = sys.argv[-1]
  outfileprefix = ".".join(infilename.split(".")[:-1])

  with open(infilename) as fp:
    ymldata = yaml.safe_load(fp)

  y2d = YML2DOT(rootnode="!@#$", fontsize="medium", addrootnode=False, rankdirlr=False, randomnodecolor=True, savehtml=True)
  y2d.process(ymldata, outfileprefix)
