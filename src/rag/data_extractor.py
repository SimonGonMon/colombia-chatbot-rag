import requests
from bs4 import BeautifulSoup
from typing import Optional


class DataExtractor:
    WIKI_URL = "https://es.wikipedia.org/wiki/Colombia"

    def fetch_content(self) -> Optional[str]:
        """
        Extrae el texto principal del artículo de Wikipedia, incluyendo párrafos y encabezados.
        Retorna None si ocurre un error.
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(self.WIKI_URL, timeout=15, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            all_divs = soup.find_all("div", class_="mw-parser-output")
            if not all_divs:
                raise ValueError(
                    "No se encontró ningún div con la clase 'mw-parser-output'."
                )

            content_div = max(all_divs, key=lambda div: len(str(div)))

            text_elements = []
            for elem in content_div.find_all(["p", "h2", "h3", "h4"]):
                if elem.find_parent(
                    ["table", "div"], class_=["infobox", "navbox", "thumb"]
                ):
                    continue

                # Usar un separador para asegurar espacios entre el texto de las etiquetas anidadas (ej. hipervínculos)
                text = elem.get_text(separator=" ", strip=True)
                if text:
                    if elem.name.startswith("h"):
                        text_elements.append(
                            f"\n\n--- {text.replace('[editar]', '')} ---\n"
                        )
                    else:
                        text_elements.append(text)

            return "\n".join(text_elements) if text_elements else None

        except requests.RequestException as e:
            print(f"Error al realizar la solicitud HTTP: {e}")
            return None
        except Exception as e:
            print(f"Error inesperado: {e}")
            return None
