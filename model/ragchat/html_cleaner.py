import os
import re
from traceback import format_exc

import pycld2 as cld2
from bs4 import BeautifulSoup
from inscriptis import get_text
from ragchat.html_patterns import HtmlPatterns


class HtmlCleaner:
    def __init__(
        self,
        parser="soup",
        min_chars_ref_text=10,
        min_engl_share_ref_text=90,
        debug=True,
        max_pages=None,
        page_list=None,
    ):
        self.parser = parser
        ## "soup" for beautifulsoup4, "inscriptus" for inscriptus
        self.min_chars_ref_text = min_chars_ref_text
        ## if len(clean_text)<min_chars_ref_text, then drop page
        self.min_engl_share_ref_text = 90
        ## if cld2 detects english share below min_engl_share_ref_text, then drop page
        self.debug = debug
        ## if True, save extra information to private-ish attributes (i.e., ending in _)
        self.max_pages = max_pages
        ## truncates at first n=max_pages pages to speed things up for debugging
        self.page_list = page_list
        ## retrieve a subset of pages isntead of all in the reference directory

        self.delete_matcher = self.get_delete_matcher(parser)
        ## compiled regular expression used for deleting a list of substrings

    def get_delete_matcher(self, parser):
        drop_text = (
            HtmlPatterns.bs_drop_text
            if parser == "soup"
            else HtmlPatterns.inscriptis_drop_text
        )
        _, drop_text = zip(
            *sorted([(len(t), t) for t in drop_text])[::-1]
        )  # find long matches before short
        # drop_text=[p.strip() for p in drop_text]
        return re.compile("|".join(map(re.escape, drop_text)))

    def get_clean_text_dict(self):
        # this is the primary method of this class.
        if self.page_list is not None:
            pages = self.page_list
        else:
            pages = [p for p in os.listdir("reference_pages") if p[-5:] == ".html"]
        clean_text_dict = self.open_and_parse_html(pages)
        clean_text_dict = self.remove_pages_with_unwanted_titles(clean_text_dict)
        clean_text_dict = self.remove_non_english(clean_text_dict)
        return clean_text_dict

    def open_and_parse_html(self, pages):
        if self.parser == "soup":
            cleaner = self.clean_with_soup
        elif self.parser == "inscriptis":
            cleaner = self.clean_with_inscriptus
        else:
            assert False, "unexpected parser: {self.parser}"
        n = len(pages) if self.max_pages is None else self.max_pages
        clean_text_dict = cleaner(pages[:n])
        return clean_text_dict

    def remove_pages_with_unwanted_titles(self, clean_text_dict):
        wanted_title_clean_text_dict = {}
        if self.debug:
            unwanted_title_clean_text_dict = {}
        for pg, result_text in clean_text_dict.items():
            if (not result_text["title"] == "") and (
                not any(
                    [
                        t.lower() in result_text["title"].lower()
                        for t in HtmlPatterns.drop_page_titles
                    ]
                )
            ):
                wanted_title_clean_text_dict[pg] = result_text
            else:
                if self.debug:
                    unwanted_title_clean_text_dict[pg] = result_text
        if self.debug:
            self.unwanted_title_clean_text_dict_ = unwanted_title_clean_text_dict
        return wanted_title_clean_text_dict

    def remove_non_english(self, clean_text_dict):
        english_clean_text_dict = {}
        non_english_clean_text_dict = {}
        for pg, text_result in clean_text_dict.items():
            isReliable, textBytesFound, details = cld2.detect(text_result["cleaned"])
            if not isReliable:
                continue
            for lang_tup in details:
                if lang_tup[0] == "ENGLISH":
                    if lang_tup[2] < self.min_engl_share_ref_text:
                        if self.debug:
                            non_english_clean_text_dict[pg] = text_result
                    else:
                        english_clean_text_dict[pg] = text_result
                    break
        if self.debug:
            self.non_english_clean_text_dict_ = non_english_clean_text_dict
        return english_clean_text_dict

    def clean_with_inscriptus(self, pages):
        texts = {}
        nothing_found_pages = {}
        read_errors = {}
        for pg in pages:
            try:
                with open(os.path.join("reference_pages", pg), "r") as f:
                    html = f.read()
            except:
                read_errors[pg] = format_exc()
                continue

            parsed = get_text(html)
            cleaned = re.sub(
                "\n\n\n+",
                "\n\n",
                re.sub(" +\n", " ", re.sub(self.delete_matcher, "", parsed).strip()),
            )
            cleaned = cleaned.replace("    ", " ")  # shrink spacing
            soup = BeautifulSoup(html, "html.parser")
            try:
                title = " ".join(
                    [
                        " ".join(s.get_text().split("|")[0].split())
                        for s in soup.html.head.findAll("title")
                    ]
                )
            except:
                title = None
            if len(cleaned) < self.min_chars_ref_text:
                nothing_found_pages[pg] = {
                    "all_text": parsed,
                    "cleaned": cleaned,
                    "title": title,
                }
                continue

            texts[pg] = {"all_text": parsed, "cleaned": cleaned, "title": title}
        if self.debug:
            # save as attributes to facilitate debugging
            self.nothing_found_pages_ = nothing_found_pages
            self.read_errors_ = read_errors
            self.clean_text_dict_ = texts
        return texts
