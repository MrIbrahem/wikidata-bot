#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

python3 pwb.py dump/labels

"""
#
# (C) Ibrahem Qasim, 2022
#
#

import re
import bz2
import json
import time
import pywikibot

Old = {}
title = "User:Mr. Ibrahem/Language statistics for items"
site = pywikibot.Site("wikidata")
page = pywikibot.Page(site, title)
texts = page.text

texts = texts.split("|}")[0].replace("|}", "").replace(",", "")

for L in texts.split("|-"):
    L = L.strip()
    L = L.replace("\n", "|")
    if L.find("{{#language:") != -1:
        L = re.sub("\(\d+\.\d+\%\)", "", L)
        L = re.sub("\|\|\s*\+\d+\s*", "", L)
        L = re.sub("\|\|\s*\-\d+\s*", "", L)
        L = re.sub("\s*\{\{\#language\:.*?\}\}\s*", "", L)
        L = re.sub("\s*\|\|\s*", "||", L)
        L = re.sub("\s*\|\s*", "|", L)
        L = L.replace("||||||", "||")
        L = L.strip()
        iu = re.search("\|(.*?)\|\|(\d*)\|\|(\d*)\|\|(\d*)", L)
        if iu:
            lang = iu.group(1).strip()
            Old[lang] = {"labels": 0, "descriptions": 0, "aliases": 0}

            labels = iu.group(2)
            if labels:
                Old[lang]["labels"] = int(labels)

            descriptions = iu.group(3)
            if descriptions:
                Old[lang]["descriptions"] = int(descriptions)

            aliases = iu.group(4)
            if aliases:
                Old[lang]["aliases"] = int(aliases)

All_items = {1: 0}


def make_cou(num, all):
    if num == 0:
        return 0
    fef = (num / all) * 100
    return str(fef)[:4] + "%"


def mainar():
    start = time.time()
    Main_Table = {}
    dumpdate = "latest"
    f = bz2.open(
        "/mnt/nfs/dumps-clouddumps1002.wikimedia.org/other/wikibase/wikidatawiki/latest-all.json.bz2",
        "r",
    )
    for line in f:
        line = line.decode("utf-8")
        line = line.strip("\n").strip(",")

        if line.startswith("{") and line.endswith("}"):
            All_items[1] += 1
            json1 = json.loads(line)
            labels = json1.get("labels", {})
            for code in labels:
                if not code in Main_Table:
                    Main_Table[code] = {"labels": 0, "descriptions": 0, "aliases": 0}
                Main_Table[code]["labels"] += 1

            descriptions = json1.get("descriptions", {})
            for code in descriptions:
                if not code in Main_Table:
                    Main_Table[code] = {"labels": 0, "descriptions": 0, "aliases": 0}
                Main_Table[code]["descriptions"] += 1

            aliases = json1.get("aliases", {})
            for code in aliases:
                if not code in Main_Table:
                    Main_Table[code] = {"labels": 0, "descriptions": 0, "aliases": 0}
                Main_Table[code]["aliases"] += 1

    lisr = """| %s || {{#language:%s|en}} || {{#language:%s}}
| {{subst:formatnum:%d}} (%s) || +{{subst:formatnum:%s}} || {{subst:formatnum:%d}} (%s) || +{{subst:formatnum:%s}} || {{subst:formatnum:%d}} || +{{subst:formatnum:%s}}"""

    p31list = list(Main_Table.keys())
    p31list.sort()
    rows = []
    test_new_descriptions = 0

    for code in p31list:
        new_labels = 0
        new_descriptions = 0
        new_aliases = 0
        if code in Old:
            new_labels = int(Main_Table[code]["labels"] - Old[code]["labels"])
            new_descriptions = int(
                Main_Table[code]["descriptions"] - Old[code]["descriptions"]
            )
            new_aliases = int(Main_Table[code]["aliases"] - Old[code]["aliases"])
        else:
            pywikibot.output('code "%s" not in Old' % code)

        if new_descriptions != 0:
            test_new_descriptions = 1

        line = lisr % (
            code,
            code,
            code,
            Main_Table[code]["labels"],
            make_cou(Main_Table[code]["labels"], All_items[1]),
            str(new_labels),
            Main_Table[code]["descriptions"],
            make_cou(Main_Table[code]["descriptions"], All_items[1]),
            str(new_descriptions),
            Main_Table[code]["aliases"],
            str(new_aliases),
        )
        line = line.replace("+-", "-")
        line = line.replace("+{{subst:formatnum:-", "-{{subst:formatnum:")
        line = line.replace("{{subst:formatnum:0}}", "0")
        rows.append(line)

    rows = "\n|-\n".join(rows)

    table = (
        """
== Number of labels, descriptions and aliases for items per language ==
{| class="wikitable sortable"
|-
! Language code
! Language (English)
! Language (native)
! data-sort-type="number"|# of labels
! data-sort-type="number"|# new labels
! data-sort-type="number"|# of descriptions
! data-sort-type="number"|# new descriptions
! data-sort-type="number"|# of aliases
! data-sort-type="number"|# new aliases
|-
%s
|}
[[Category:Wikidata statistics|Language statistics]]
"""
        % rows
    )

    if test_new_descriptions == 0:
        pywikibot.output("nothing new.. ")
        return ""

    final = time.time()
    delta = int(final - start)

    text = ""
    text = "Update: <onlyinclude>%s</onlyinclude>.\n" % dumpdate
    text += "* Total items:{{subst:formatnum:%d}} \n" % All_items[1]
    text += "<!-- bots work done in %d secounds --> \n" % delta
    text += "--~~~~~\n"
    text = text + "\n" + table
    text = text.replace("0 (0000)", "0")
    text = text.replace("0 (0)", "0")

    page.text = text
    page.save()


if __name__ == "__main__":
    mainar()