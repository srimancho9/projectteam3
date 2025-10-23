from typing import Dict, List
from .sources.pubmed import search_pubmed
from .sources.europe_pmc import search_eupmc
from .sources.crossref import search_crossref
from .sources.preprints import search_preprints
from .sources.ctgov import search_ctgov
from .sources.agency import harvest_agencies
from .sources.repos import find_datasets
from .ranking import rank_items
from .utils import dedupe_list

def harvest_topic(keyword: str, limit: int = 50) -> Dict[str, List[Dict]]:
    pools = []
    pools += search_pubmed(keyword, n=20)
    pools += search_eupmc(keyword, n=20)
    pools += search_crossref(keyword, n=15)
    pools += search_preprints(keyword, n=10)
    pools += search_ctgov(keyword, n=10)
    pools += harvest_agencies(keyword, n=5)
    pools += find_datasets(keyword, n=5)
    items = dedupe_list(pools)
    ranked = rank_items(items)[:limit]
    return {"items": ranked}
