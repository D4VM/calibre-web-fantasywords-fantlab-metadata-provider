from typing import List, Optional

import requests
from bs4 import BeautifulSoup as BS

from cps.services.Metadata import Metadata, MetaRecord, MetaSourceInfo


class FantasyWorlds(Metadata):
    __name__ = "Fantasy Worlds"
    __id__ = "fantasyworld"

    meta_source_id: str = "fantasyworlds"
    meta_source_desc: str = "Fantasy-Worlds.org Provider"
    meta_source_link: str = "https://fantasy-worlds.org"

    QUERY_URL = "https://fantasy-worlds.org/search/?q="

    @staticmethod
    def _search_string_fixer(search_string: str) -> str:
        words = search_string.strip().split()
        return "+".join(words) if len(words) > 1 else search_string.strip()

    def search(
        self, query: str, generic_cover: str = "", locale: str = "en"
    ) -> Optional[List[MetaRecord]]:
        request_session = requests.Session()
        request_session.get(self.QUERY_URL)

        fixed_query: str = self._search_string_fixer(query)
        search_url: str = self.QUERY_URL + fixed_query

        print(f"[FantasyWorlds] Поисковый запрос: {query}")
        print(f"[FantasyWorlds] URL запроса: {search_url}")

        try:
            response = request_session.get(search_url, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"[FantasyWorlds] Ошибка запроса: {e}")
            return None

        soup = BS(response.content, "html.parser")
        results = []

        def extract_series_links(item) -> str:
            series_links = item.select('a[href^="/series/"]')
            series_names = [a.get_text(strip=True) for a in series_links]
            return ": ".join(series_names)

        for idx, item in enumerate(soup.select(".news_body"), 1):
            print(f"\n[FantasyWorlds] Обработка результата #{idx}")
            try:
                title = item.select_one('span[itemprop="name"]')
                if title:
                    title = title.text.strip()
                else:
                    print("  ➤ Название не найдено")
                    continue

                author = item.select_one('a[itemprop="author"]')
                author = author.text.strip() if author else "Неизвестен"

                series = extract_series_links(item)

                # Парсинг номера книги в серии
                try:
                    number_text = item.find(string="Номер книги в серии:")
                    number_in_series = (
                        int(number_text.next.strip()) if number_text else 0
                    )
                except Exception as e:
                    print(f"  ➤ Ошибка парсинга номера книги: {e}")
                    number_in_series = 0

                isbn_tag = item.select_one('span[itemprop="isbn"]')
                isbn = isbn_tag.text.strip() if isbn_tag else f"{title}_{author}"

                description_tag = item.select_one('span[itemprop="description"]')
                description = description_tag.text.strip() if description_tag else ""

                img_tag = item.select_one('img[itemprop="image"]')
                cover_url = (
                    "https://fantasy-worlds.org" + img_tag["src"] if img_tag else ""
                )

                print(f"  ➤ Название: {title}")
                print(f"  ➤ Автор: {author}")
                print(f"  ➤ Серия: {series}")
                print(f"  ➤ Номер в серии: {number_in_series}")
                print(f"  ➤ ISBN: {isbn}")
                print(f"  ➤ Обложка: {cover_url}")

                record = MetaRecord(
                    id=isbn,
                    source=MetaSourceInfo(
                        id=self.meta_source_id,
                        description=self.meta_source_desc,
                        link=self.meta_source_link,
                    ),
                    title=title,
                    authors=[author],
                    description=description,
                    url=self.meta_source_link,
                    series=series,
                    series_index=number_in_series,
                    identifiers={"isbn": isbn},
                    cover=cover_url,
                )

                results.append(record)

            except Exception as e:
                print(f"  ➤ Ошибка при разборе результата: {e}")

        print(f"\n[FantasyWorlds] Найдено результатов: {len(results)}")
        return results if results else None
