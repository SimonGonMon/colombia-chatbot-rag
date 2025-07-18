import requests
from bs4 import BeautifulSoup
from typing import Optional
import re


class DataExtractor:
    """
    Extrae y limpia el contenido textual de una URL de Wikipedia.

    Esta clase se encarga de realizar la solicitud HTTP, parsear el HTML
    y extraer el contenido relevante del artículo, como párrafos y encabezados,
    eliminando elementos no deseados (infoboxes, navboxes, etc.).
    """

    WIKI_URL = "https://es.wikipedia.org/wiki/Colombia"

    def fetch_content(self) -> Optional[str]:
        """
        Obtiene el contenido principal de la página de Wikipedia.

        Realiza una solicitud GET con un User-Agent de navegador para asegurar
        la recepción del HTML completo. Selecciona el contenedor de contenido
        principal y extrae el texto de las etiquetas <p> y <h*>, asegurando
        que los espacios se manejen correctamente.

        Returns:
            Optional[str]: Una cadena con el texto limpio del artículo, o None si ocurre un error.
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

                text = elem.get_text(separator=" ", strip=True)
                if text:
                    if elem.name.startswith("h"):
                        # Limpiar el texto del título y solo añadirlo si no está vacío
                        clean_title = text.replace("[editar]", "").strip()
                        if clean_title:
                            text_elements.append(f"\n\n--- {clean_title} ---\n")
                    else:
                        text_elements.append(text)

            return "\n".join(text_elements) if text_elements else None

        except requests.RequestException as e:
            print(f"Error al realizar la solicitud HTTP: {e}")
            return None
        except Exception as e:
            print(f"Error inesperado durante la extracción: {e}")
            return None


if __name__ == "__main__":
    extractor = DataExtractor()
    content = extractor.fetch_content()

    if content:
        # Usar una expresión regular para dividir por los títulos --- Título ---
        sections = re.split(r"\n\n--- .*? ---\n", content)

        # Filtrar secciones vacías que pueden resultar de la división
        section_lengths = [
            len(section.strip()) for section in sections if section.strip()
        ]

        if section_lengths:
            avg_len = sum(section_lengths) / len(section_lengths)
            min_len = min(section_lengths)
            max_len = max(section_lengths)

            print(f"Número total de secciones de texto: {len(section_lengths)}")
            print(f"Longitud promedio por sección: {avg_len:.0f} caracteres")
        else:
            print("No se encontró contenido textual en las secciones para analizar.")
    else:
        print("No se pudo extraer contenido para el análisis.")
