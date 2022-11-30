#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

python3 pwb.py dump/claims

"""
#
# (C) Ibrahem Qasim, 2022
#
#
import bz2
import json
import time
import pywikibot

tab = {}
tab["len_of_all_properties"] = 0
tab["items_1_claims"] = 0
tab["items_no_claims"] = 0
tab["All_items"] = 0
tab["all_claims_2020"] = 0
tab["Main_Table"] = {}
lamo = [
    "len_of_all_properties",
    "items_1_claims",
    "items_no_claims",
    "All_items",
    "all_claims_2020",
    "Main_Table",
]
jsonname = "dump/claimse.json"

sections_done = {1: 0}
sections_false = {1: 0}


def make_section(P, table, Len):
    texts = "== {{P|%s}}  ==" % P
    if sections_done[1] == 50:
        return ""
    pywikibot.output(" make_section for property:%s" % P)
    texts += "\n* Total items use these property:%d" % Len
    if tab["Main_Table"].get(P, {}).get("lenth_of_claims_for_property"):
        texts += "\n* Total number of claims with these property:%d" % tab[
            "Main_Table"
        ].get(P, {}).get("lenth_of_claims_for_property")
    texts += "\n"
    pywikibot.output(texts)
    if table["props"] == {}:
        pywikibot.output('%s table["props"] == {} ' % P)
        return ""
    xline = ""
    yline = ""
    Chart = """
{| class="floatright sortable" 
|-
|
{{Graph:Chart|width=140|height=140|xAxisTitle=value|yAxisTitle=Number
|type=pie|showValues1=offset:8,angle:45
|x=%s
|y1=%s
|legend=value
}}
|-
|}"""
    tables = """
{| class="wikitable sortable plainrowheaders"
|-
! class="sortable" | #
! class="sortable" | value
! class="sortable" | Numbers
|-
"""
    lists = [[y, xff] for xff, y in table["props"].items()]
    lists.sort(reverse=True)
    num = 0
    other = 0
    for ye, x in lists:
        if ye == 0 and sections_false[1] < 100:
            pywikibot.output("p(%s),x(%s) ye == 0 or ye == 1 " % (P, x))
            sections_false[1] += 1
            return ""
        num += 1
        if num < 51:
            tables += "\n"
            if x.startswith("Q"):
                row = "| %d || {{Q|%s}} || {{subst:formatnum:%d}} " % (num, x, ye)
            else:
                row = "| %d || %s || {{subst:formatnum:%d}} " % (num, x, ye)
            xline += ",%s" % x
            yline += ",%d" % ye
            tables += row
            tables += "\n|-"
        else:
            other += ye
    num += 1
    tables += "\n| %d || others || {{subst:formatnum:%d}} " % (num, other)
    tables += "\n|-"
    Chart = Chart % (xline, yline)
    tables += "\n|}\n{{clear}}\n"
    texts += Chart.replace("=,", "=")
    texts += tables
    sections_done[1] += 1
    return texts


ttypes = [
    "wikibase-entityid",
    "time",
    "monolingualtext",
    "quantity",
]


def log_dump():
    with open(jsonname, "w") as outfile:
        json.dump(tab, outfile)


def workondata():
    fileeee = bz2.open(
        "/mnt/nfs/dumps-clouddumps1002.wikimedia.org/other/wikibase/wikidatawiki/latest-all.json.bz2",
        "r",
    )

    for line in fileeee:
        line = line.decode("utf-8")
        line = line.strip("\n").strip(",")

        if line.startswith("{") and line.endswith("}"):

            tab["All_items"] += 1
            json1 = json.loads(line)
            claimse = json1.get("claims", {})
            if claimse == {}:
                tab["items_no_claims"] += 1
            if len(claimse) == 1:
                tab["items_1_claims"] += 1

            for P31 in claimse:
                if not P31 in tab["Main_Table"]:
                    tab["Main_Table"][P31] = {
                        "props": {},
                        "lenth_of_usage": 0,
                        "lenth_of_claims_for_property": 0,
                    }

                tab["Main_Table"][P31]["lenth_of_usage"] += 1
                tab["all_claims_2020"] += len(json1["claims"][P31])

                for claim in json1["claims"][P31]:
                    tab["Main_Table"][P31]["lenth_of_claims_for_property"] += 1
                    datavalue = claim.get("mainsnak", {}).get("datavalue", {})
                    ttype = datavalue.get("type")

                    if ttype == "wikibase-entityid":
                        id = datavalue.get("value", {}).get("id")
                        if id:
                            if id in tab["Main_Table"][P31]["props"]:
                                tab["Main_Table"][P31]["props"][id] += 1
                            else:
                                tab["Main_Table"][P31]["props"][id] = 1


dumpdate = "latest"


def mainar():
    time_start = time.time()
    pywikibot.output("time_start:%s" % str(time_start))
    sections = ""
    xline = ""
    yline = ""
    Chart2 = """
{| class="floatright sortable" 
|-
|
{{Graph:Chart|width=900|height=100|xAxisTitle=property|yAxisTitle=usage|type=rect
|x=%s
|y1=%s
}}
|-
|}"""
    workondata()

    property_other = 0
    tab["len_of_all_properties"] = 0
    p31list = [
        [y["lenth_of_usage"], x]
        for x, y in tab["Main_Table"].items()
        if y["lenth_of_usage"] != 0
    ]
    p31list.sort(reverse=True)
    rows = []

    for Len, P in p31list:
        tab["len_of_all_properties"] += 1
        if tab["len_of_all_properties"] < 27:
            xline += ",%s" % P
            yline += ",%d" % Len
        sections += make_section(P, tab["Main_Table"][P], Len)
        if len(rows) < 51:
            rows.append(
                "| %d || {{P|%s}} || {{subst:formatnum:%d}} "
                % (tab["len_of_all_properties"], P, Len)
            )
        else:
            property_other += int(Len)

    Chart2 = Chart2.replace("|x=%s", "|x=" + xline)
    Chart2 = Chart2.replace("|y1=%s", "|y1=" + yline)
    Chart2 = Chart2.replace("=,", "=")

    rows.append("| 52 || others || {{subst:formatnum:%d}} " % property_other)
    rows = "\n|-\n".join(rows)
    table = (
        """
{| class="wikitable sortable"
|-
! #
! property
! usage
|-
%s
|}
"""
        % rows
    )

    final = time.time()
    delta = int(final - time_start)

    text = "Update: <onlyinclude>%s</onlyinclude>.\n" % dumpdate
    text += "* Total items:{{subst:formatnum:%d}} \n" % tab["All_items"]
    text += "* Items without claims:{{subst:formatnum:%d}} \n" % tab["items_no_claims"]
    text += (
        "* Items with 1 claim only:{{subst:formatnum:%d}} \n" % tab["items_1_claims"]
    )
    text += (
        "* Total number of claims:{{subst:formatnum:%d}} \n" % tab["all_claims_2020"]
    )
    text += (
        "* Number of properties of the report:{{subst:formatnum:%d}} \n"
        % tab["len_of_all_properties"]
    )
    text += "<!-- bots work done in %d secounds --> \n" % delta
    text += "--~~~~~\n"
    text = text + "== Numbers ==\n"
    text = text + "\n" + Chart2
    text = text + "\n" + table
    text = text + "\n" + sections
    text = text.replace("0 (0000)", "0")
    text = text.replace("0 (0)", "0")
    
    title = "User:Mr. Ibrahem/claims"
    site = pywikibot.Site("wikidata")
    page = pywikibot.Page(site, title)

    page.text = text
    page.save()

    with open("dump/claims.txt", "w") as f:
        f.write(text)


if __name__ == "__main__":
    mainar()