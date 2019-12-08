"""
Extract articles from a file named test.xml.

The script search for all article-like information and saves the plain
content in one file per article, named after the date and an identifier of the
article.
"""

import csv
import os
import re


def extract_tag_inner_content(tagname, content):
    """Helper function to get the (first) inner content of a tag.

    E.g. for <tag attr="value"><inner>text</inner></tag>
    it will return <inner>text</inner>.

    Returns an empty string if no match found.
    """
    match = re.search(
        "<" + tagname + r"(\s+[^>]*)?>(.*)</" + tagname + ">", content)
    if match:
        return match.group(2)
    return ""


def extract_tag_attr_value(tagname, attrname, content):
    """Helper function to get the value of a tags attribute.

    It only considers the first found attribute of the first found tag.
    """
    match = re.search("<" + tagname + r"(\s+[^>]*)>", content)
    value = None
    if match:
        all_attrs = match.group(1)
        match2 = re.search(r"\s+" + attrname + "=\"([^\"]*)\"", all_attrs)
        if match2:
            value = match2.group(1)
    return value


def remove_tag_inner_content(tagname, content):
    """Helper function to remove all the tags from a content.

    Returns the changed content.
    """
    replaced = re.sub(
        "<" + tagname + r"(\s+[^>]*)?>(.*)</" + tagname + ">", '', content)
    return replaced


def strip_all_tags(content):
    """Helper function to remove all tags from a string.

    The inner text is preserved.
    """
    return re.sub(r"<[^\>]*>", "", content)


# Read the files content into a variable
content = None
with open('test.xml', 'r') as testfile:
    content = testfile.read()

# Split the read content at each <div3> tag.
#
# As the split removes the marker string, it is added again.
# This allows for using the helper functions.
# Partition into a header (i.e. the content before the first div3)
# and a list of div3 items (i.e. the articles).
parts = re.split(r"<div3", content)
header = parts[0]
articles = []
for part in parts[1:]:
    articles.append("<div3" + part)

# Extract the date from an attribute and save it in a vairable.
title_page = extract_tag_inner_content('titlePage', header)
date = extract_tag_attr_value('date', 'value', title_page)

# Loop through all articles, extract information and save it in
# a dictionary variable.
# A unique key is contructed by glueing together the index number, the type and
# the value of the n attribute of a div3.
# Technically the index would be unique enough, but difficult to filter without
# the type information (this key will be used to constuct the filenames).
stripped_and_keyed_articles = {}
for index, article in enumerate(articles):
    type_ = extract_tag_attr_value('div3', 'type', article)
    n = extract_tag_attr_value('div3', 'n', article)
    key = "{:03d}-{}-{:02d}".format(index, type_, int(n))

    header = strip_all_tags(extract_tag_inner_content('head', article))
    stripped = strip_all_tags(remove_tag_inner_content('head', article))
    # save the information in a basic data structure (tuple)
    stripped_and_keyed_articles[key] = (type_, header, stripped)

# Write the information (contents) to a TSV file with one article per item.
filename = "dispatch_" + date + ".tsv"
with open(filename, "w") as output:
    print(filename + " : ", end="")
    csvwriter = csv.writer(output, delimiter="\t",
                           quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csvwriter.writerow(["date", "type", "header", "content"])
    for key in sorted(stripped_and_keyed_articles.keys()):
        print(".", end="", flush=True)
        csvwriter.writerow([date] + list(stripped_and_keyed_articles[key]))
    print("\n")

print("\nDone! Bye.\n")
