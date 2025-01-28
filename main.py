from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import urllib.request
from urllib.parse import quote
import random
import json

class GoogleImageScraper:
    def __init__(self, download_path='imagens_baixadas/'):
        self.download_path = download_path
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        
        # Configurar Chrome Options
        self.options = Options()
        self.options.add_argument('--headless=new')  # Usando novo modo headless
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('--start-maximized')
        self.options.add_argument('--window-size=1920,1080')
        self.options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Instalação automática do ChromeDriver
        self.service = Service(ChromeDriverManager().install())
    
    def download_image(self, url, file_name):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            }
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=10) as response:
                with open(file_name, 'wb') as out_file:
                    out_file.write(response.read())
            return True
        except Exception as e:
            print(f"Erro ao baixar imagem: {str(e)}")
            return False

    def extract_image_urls(self, driver, num_images):
        image_urls = set()
        
        # Função para extrair URLs de imagens
        def extract_urls():
            images = driver.find_elements(By.CSS_SELECTOR, "img[data-iml]")
            for img in images:
                try:
                    # Tentar diferentes métodos para obter a URL da imagem
                    url = None
                    
                    # Método 1: Atributo src
                    url = img.get_attribute('src')
                    
                    # Método 2: Atributo data-src
                    if not url or url.startswith('data:'):
                        url = img.get_attribute('data-src')
                    
                    # Método 3: Procurar no atributo metadata
                    if not url or url.startswith('data:'):
                        metadata = img.get_attribute('metadata')
                        if metadata:
                            try:
                                metadata_json = json.loads(metadata)
                                if 'url' in metadata_json:
                                    url = metadata_json['url']
                            except:
                                pass
                    
                    if url and url.startswith('http') and not url.endswith('.gif'):
                        print(f"URL encontrada: {url[:100]}")
                        image_urls.add(url)
                except Exception as e:
                    print(f"Erro ao extrair URL: {str(e)}")
                    continue
                
                if len(image_urls) >= num_images:
                    return True
            return False

        print("Scrolling e extraindo URLs...")
        last_count = 0
        scroll_attempts = 0
        max_scroll_attempts = 10

        while len(image_urls) < num_images and scroll_attempts < max_scroll_attempts:
            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Extrair URLs
            if extract_urls():
                break
                
            # Verificar progresso
            if len(image_urls) == last_count:
                scroll_attempts += 1
            else:
                scroll_attempts = 0
                last_count = len(image_urls)
            
            print(f"URLs encontradas até agora: {len(image_urls)}")
            
        return list(image_urls)

    def scrape_images(self, search_query, num_images=10):
        driver = None
        try:
            print("Iniciando o Chrome...")
            driver = webdriver.Chrome(service=self.service, options=self.options)
            
            # Codificar a consulta de pesquisa para URL
            encoded_query = quote(search_query)
            url = f"https://www.google.com/search?q={encoded_query}&tbm=isch"
            
            print(f"Acessando URL: {url}")
            driver.get(url)
            
            # Aguardar carregamento inicial
            time.sleep(3)
            
            # Extrair URLs das imagens
            image_urls = self.extract_image_urls(driver, num_images)
            
            # Baixar as imagens
            print(f"\nIniciando download de {len(image_urls)} imagens...")
            for i, url in enumerate(image_urls):
                file_name = os.path.join(self.download_path, f"{search_query}_{i+1}.jpg")
                if self.download_image(url, file_name):
                    print(f"Imagem {i+1} baixada com sucesso: {file_name}")
                else:
                    print(f"Falha ao baixar imagem {i+1}")
                
                # Pequena pausa entre downloads
                time.sleep(random.uniform(0.5, 1.5))
                
        except Exception as e:
            print(f"Erro durante o scraping: {str(e)}")
            print("Stack trace completo:", e.__class__.__name__)
        
        finally:
            if driver:
                driver.quit()

if __name__ == "__main__":
    # Exemplo de uso
    scraper = GoogleImageScraper()
    scraper.scrape_images("cachorro fofo", 5)  # Baixar 5 imagens de cachorros fofos