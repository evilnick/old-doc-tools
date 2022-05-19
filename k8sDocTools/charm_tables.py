#!/usr/bin/python3

import argparse
import getpass
import os
import glob
import tempfile
import sh
import sys
import logging
from jinja2 import Template
from ruamel.yaml import YAML
import requests
import re
from io import StringIO
from github import Github
from github import GithubException
# from __init__ import __version__
from k8sDocTools.templates import charm_config_tpl
from k8sDocTools.templates import charm_config_tpl_2
from k8sDocTools import __version__
from k8sDocTools.utils import *

# globals
# TODO: may be needed in other files possibly better to store as a module

repo_name = "charmed-kubernetes/kubernetes-docs"
repo_path = "pages/k8s/"
store_url = (
    "https://api.jujucharms.com/charmstore/v5/~containers/*charm*/archive/config.yaml"
)


def obj2table(obj):
    """
    Takes the object representing the charm config as extracted from the YAML
    and pre-processes it to split off over-long table elements into a follow on
    note stored in 'overmatter'
    """

    obj["overmatter"] = dict()
    overmatter = ""
    for option in sorted(obj["options"].items()):
        name = option[0]
        backlink = f"\n\n[Back to table](#table-{name})"
        # check if default is too big
        if isinstance(option[1]["default"], str):
            if len(option[1]["default"]) > 20:
                obj["overmatter"][option[0]] = list()
                obj["overmatter"][option[0]].append(
                    [
                        f'<a id="{option[0]}-default"> </a>',
                        "Default",
                        "```\n"+option[1]["default"]+"\n```\n" + backlink,
                    ]
                )
                option[1]["default"] = f"[See notes](#{option[0]}-default)"
        option[1]["description"] = option[1]["description"].strip('\n')
        # print(f"string: {option[1]['description']} len: {len(option[1]['description'])}")
        if (len(option[1]["description"]) > 210) or ("\n " in (option[1]["description"])):
            # assume multi-line entries need to be notes
            if not option[0] in obj["overmatter"]:
                obj["overmatter"][option[0]] = list()
            option[1]["description"] = markdownify(option[1]["description"])
            obj["overmatter"][option[0]].append(
                [
                    f'<a id="{option[0]}-description"> </a>',
                    "Description",
                    option[1]["description"] + backlink,
                ]
            )
            option[1]["description"] = f"[See notes](#{option[0]}-description)"
        else:
            # No \n in a table thanks
            option[1]["description"] = option[1]["description"].replace('\n',' ')
    return obj

def markdownify(txt):
    #TODO some simple style fixes to make text render nicely
    # - put URLS *in text* into angle brackets


    regex = r'(?<!<|\(|")(?:(?:https?|ftp|file):\/\/|www\.|ftp\.)(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[-A-Z0-9+&@#\/%=~_|$?!:,.])*(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[A-Z0-9+&@#\/%=~_|$])'
    txt = re.sub(regex, '<\g<0>>', txt,0,re.DOTALL)
    # - fence obviously indented code
    regex = r"\n(( {2,}|\t)(.*?(\n)))+"
    txt = re.sub(regex, '\n\n```\g<0>```\n\n', txt,0,re.DOTALL)

    return(txt)


def updatePage(filename, charm):
    """
    Given a filename, and the charm (possibly including specific version)
    will insert the generated table in the correct place, removing any previous
    config table content.
    """
    regex = "<!-- CONFIG STARTS -->\n(.*)\n<!-- CONFIG ENDS -->"
    config_text = charmconfig2md(charm)
    with open(filename, 'r+', encoding="utf-8") as f:
        content = f.read()
        content = re.sub(regex, config_text, content, 1, re.DOTALL)
        f.seek(0)
        f.write(content)
        f.truncate()
        f.close()

def updateString(string, charm):
    regex = "<!-- CONFIG STARTS -->\n(.*)\n<!-- CONFIG ENDS -->"
    config_text = charmconfig2md(charm)
    re.sub(regex, config_text, string, 1, re.DOTALL)

def updateDir(path):
    """
    Finds all the charm pages in a given path and updates them
    """
    for file in os.listdir(path):
        if file.startswith("charm-"):
            if file.endswith(".md"):
                if not (file == "charm-reference.md"):
                    print(file)
                    updatePage(os.path.join(path,file),file[6:-3])


def charmconfig2md(charm):
    """
    The charm argument corresponds to a charm in the charmstore
    which can be either the simple name of a charm (e.g. 'etcd')
    in which case the latest stable version is fetched, OR a specific
    versions (e.g. 'etcd-113'), in which case that specific version is used.
    """
    config_url = store_url.replace("*charm*", charm)
    template = Template(charm_config_tpl_2)
    y = YAML(typ='safe').load(requests.get(config_url).content)
    # y = yaml.load(requests.get(config_url).content, Loader=yaml.FullLoader)
    if 'options' in y.keys():
        y = template.render(obj2table(y))
    else:
        y = ''
    return y

def charmactions2md(charm):
    """
    The charm argument corresponds to a charm in the charmstore
    which can be either the simple name of a charm (e.g. 'etcd')
    in which case the latest stable version is fetched, OR a specific
    versions (e.g. 'etcd-113'), in which case that specific version is used.
    """


def main():
    parser = argparse.ArgumentParser(
        description="Charm config template thing " + __version__
    )

    parser.add_argument("--charm", help="A specific charm to update (defaults to all)")
    args = parser.parse_args()
    print(charmconfig2md(args.charm))


if __name__ == "__main__":
    main()
