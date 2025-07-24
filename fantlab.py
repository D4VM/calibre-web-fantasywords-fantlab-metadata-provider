import re
from typing import List, Optional

import requests  # noqa
from bs4 import BeautifulSoup as BS  # noqa

from cps.services.Metadata import Metadata, MetaRecord, MetaSourceInfo  # noqa


class Fantlab(Metadata):
    __name__ = "Fantlab"
    __id__ = "fantlab"

    FANTLIB_SEARCH_URL = "https://fantlab.ru/searchmain?searchstr="

    @staticmethod
    def _search_string_fixer(search_string: str) -> str:
        words = search_string.strip().split()
        return "+".join(words) if len(words) > 1 else search_string.strip()

    def search(
        self, query: str, generic_cover: str = "", locale: str = "en"
    ) -> Optional[List[MetaRecord]]:
        fixed_query = self._search_string_fixer(query)
        url = self.FANTLIB_SEARCH_URL + fixed_query

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"[Fantlab] Request failed: {e}")
            return None

        soup = BS(response.content, "html.parser")
        results = []

        for item in soup.select(".search-block.editions .b"):
            a_tag = item.select_one("a")
            if not a_tag:
                continue

            href = a_tag.get("href")
            if not href:
                continue

         
            match = re.search(r"edition(\d+)", href)
            book_id = match.group(1) if match else None
            if not book_id:
                continue

            edition_url = f"https://fantlab.ru{href}"

            try:
                edition_response = requests.get(edition_url, timeout=10)
                edition_response.raise_for_status()
            except Exception as e:
                print(f"[Fantlab] Failed to fetch edition page: {e}")
                continue

            edition_soup = BS(edition_response.content, "html.parser")
            block = edition_soup.select_one(".titles-block-center")
            if not block:
                continue

            title = block.select_one("#name")
            title_text = title.get_text(strip=True) if title else "Без названия"

            author = block.select_one("#autors a")
            authors = [author.get_text(strip=True)] if author else []

            lang_meta = block.select_one("meta[itemprop='inLanguage']")
            language = lang_meta.get("content", "").strip() if lang_meta else ""

            publisher_tag = block.select_one("#publisher a")
            publisher = publisher_tag.get_text(strip=True) if publisher_tag else ""

            series_tag = block.select_one("#series a")
            series = series_tag.get_text(strip=True) if series_tag else ""

            img_tag = edition_soup.select_one("img[itemprop='image']")
            cover = (
                f"https://fantlab.ru{img_tag['src']}"
                if img_tag and img_tag.get("src", "").startswith("/")
                else generic_cover
            )
            book_id = href.replace("/edition", "")
            results.append(
                MetaRecord(
                    id=book_id,
                    source=MetaSourceInfo(
                        id=self.__id__,
                        description="Fantlab Metadata",
                        link=edition_url,
                    ),
                    title=title_text,
                    url=edition_url,
                    cover=cover,
                    authors=authors,
                    languages=[language] if language else [],
                    publisher=publisher,
                    series=series,
                    identifiers={"fantlab": book_id},
                )
            )

        return results
