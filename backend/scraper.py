import httpx
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional

class CFScraper:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.base_url = "https://codeforces.com/problemset/problem"

    async def fetch_problem(self, problem_id: str) -> Optional[Dict]:
        """
        Fetch problem details from Codeforces.
        problem_id: e.g., '78A', '118A'
        """
        # Parse problem_id into contest_id and index (e.g., 78 and A)
        match = re.match(r"(\d+)([A-Z]\d*)", problem_id)
        if not match:
            return None
        
        contest_id, index = match.groups()
        url = f"{self.base_url}/{contest_id}/{index}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, follow_redirects=True)
                if response.status_code != 200:
                    return None
                
                return self._parse_html(response.text, problem_id)
            except Exception as e:
                print(f"Scraping error: {e}")
                return None

    def _parse_html(self, html: str, problem_id: str) -> Dict:
        soup = BeautifulSoup(html, "html.parser")
        
        # Title
        title_tag = soup.find("div", class_="title")
        title = title_tag.text.strip() if title_tag else problem_id

        # Rating (often found in sideboxes)
        rating = "unknown"
        for tag in soup.find_all("span", title="Difficulty"):
            rating = tag.text.strip().lstrip('*')

        # Tags
        tags = []
        for tag in soup.find_all("span", class_="tag-box"):
            tags.append(tag.text.strip())

        # Samples
        samples = []
        sample_test = soup.find("div", class_="sample-test")
        if sample_test:
            inputs = sample_test.find_all("div", class_="input")
            outputs = sample_test.find_all("div", class_="output")
            
            for i, o in zip(inputs, outputs):
                in_text = i.find("pre").text.strip()
                out_text = o.find("pre").text.strip()
                samples.append({
                    "input": in_text,
                    "expected_output": out_text
                })

        return {
            "problemId": problem_id,
            "title": title,
            "rating": rating,
            "tags": tags,
            "samples": samples
        }

if __name__ == "__main__":
    # Quick manual test
    import asyncio
    async def test():
        scraper = CFScraper()
        data = await scraper.fetch_problem("78A")
        print(data)
    asyncio.run(test())
