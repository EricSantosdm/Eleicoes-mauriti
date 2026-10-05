"""
===============================================================================
SCRAPER DE DADOS ELEITORAIS - MAURITI / CE (76ª ZONA ELEITORAL)
===============================================================================
Este script realiza a coleta dos Boletins de Urna (BU) no site oficial do TSE,
processa as seções eleitorais ativas de Mauriti/CE, cruza as informações com o
mapeamento de endereços extraído do arquivo PDF oficial e gera o dataset JSON.

Requisitos:
  pip install selenium pypdf beautifulsoup4

Uso:
  python scraper_eleicoes_mauriti.py
===============================================================================
"""

import time
import json
import re
import urllib.request
import ssl
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pypdf

# -----------------------------------------------------------------------------
# 1. PARSER DO ARQUIVO PDF (Mapeamento de Escolas, Endereços e Bairros)
# -----------------------------------------------------------------------------
def parse_pdf_locations(pdf_path="LOCAIS DE VOTAÇÃO - SEÇÕES E APTOS.pdf"):
    print("📖 Extraindo endereços e locais do PDF:", pdf_path)
    reader = pypdf.PdfReader(pdf_path)
    
    sec_map = {}
    for page_num, page in enumerate(reader.pages, 1):
        text = page.extract_text()
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        i = 0
        while i < len(lines):
            l = lines[i]
            if "LOCAIS DE VOTA" in l or "Rela" in l or l in ["SEÇÃO", "Local", "Aptos", "Endereço", "OBERVAÇÕES", "OBSERVAÇÕES"]:
                i += 1
                continue
                
            if re.match(r'^\d{1,3}$', l):
                sec_num = int(l)
                sec_code = f"{sec_num:04d}"
                
                j = i + 1
                block = []
                while j < len(lines):
                    nxt = lines[j]
                    if nxt in ["SEÇÃO", "Local", "Aptos", "Endereço", "OBERVAÇÕES", "OBSERVAÇÕES"]:
                        j += 1
                        continue
                    if "LOCAIS DE VOTA" in nxt or "Rela" in nxt:
                        j += 1
                        continue
                    if re.match(r'^\d{1,3}$', nxt):
                        nxt_num = int(nxt)
                        if nxt_num == sec_num + 1 or (nxt_num > sec_num and nxt_num <= sec_num + 5):
                            break
                    block.append(nxt)
                    j += 1
                    
                aptos_idx = -1
                for b_idx, b_line in enumerate(block):
                    if re.match(r'^\d{2,3}$', b_line) and 20 <= int(b_line) <= 550:
                        aptos_idx = b_idx
                        break
                        
                local_nome = ""
                endereco = ""
                obs = ""
                
                if aptos_idx != -1:
                    local_nome = " ".join(block[:aptos_idx]).strip()
                    rem = block[aptos_idx+1:]
                    addr_parts = []
                    for r in rem:
                        if "AGREGADA" in r:
                            obs = r
                        else:
                            addr_parts.append(r)
                    endereco = " ".join(addr_parts).strip()
                else:
                    local_nome = " ".join(block).strip()
                    
                sec_map[sec_code] = {
                    "local_nome": local_nome,
                    "endereco": endereco,
                    "observacao": obs
                }
                i = j - 1
            i += 1
            
    print(f"✅ Mapeadas {len(sec_map)} seções do PDF.")
    return sec_map

def get_bairro_distrito(endereco, local_nome):
    if not endereco:
        return "Sede / Outros"
    
    end_upper = endereco.upper().strip()
    
    if "ANAUA" in end_upper or "ANAUÁ" in end_upper:
        return "Distrito de Anauá"
    elif "BURITIZINHO" in end_upper:
        return "Distrito de Buritizinho"
    elif "COITE" in end_upper or "COITÉ" in end_upper:
        return "Distrito de Coité"
    elif "PALESTINA" in end_upper:
        return "Distrito de Palestina do Cariri"
    elif "SÃO FÉLIX" in end_upper or "SAO FELIX" in end_upper:
        return "Distrito de São Félix"
    elif "UMBURANAS" in end_upper:
        return "Distrito de Umburanas"
    elif "SANTA CRUZ" in end_upper:
        return "Distrito de Nova Santa Cruz"
    elif "SAO MIGUEL" in end_upper or "SÃO MIGUEL" in end_upper:
        return "Distrito de São Miguel"
    elif "BELA VISTA" in end_upper:
        return "Bairro Bela Vista"
    elif "SERRINHA" in end_upper:
        return "Bairro Serrinha"
    elif "POPULARES" in end_upper:
        return "Bairro Populares"
    elif "CENTRO" in end_upper:
        return "Centro"
    elif "SITIO" in end_upper or "SÍTIO" in end_upper or "VILA" in end_upper:
        return "Zona Rural / Sítios"
    else:
        return "Sede / Outros"

# -----------------------------------------------------------------------------
# 2. RASPAGEM DE BOLETINS DE URNA DO TSE VIA SELENIUM
# -----------------------------------------------------------------------------
def run_tse_scraper(rota_path="rota.txt", pdf_path="LOCAIS DE VOTAÇÃO - SEÇÕES E APTOS.pdf"):
    pdf_locations = parse_pdf_locations(pdf_path)
    
    # Ler seções de rota.txt
    with open(rota_path, 'r', encoding='utf-8', errors='ignore') as f:
        rota_text = f.read()

    matches = re.findall(r'<ion-label[^>]*>\s*<!---->\s*(\d{4})\s*(\(agregada[^)]*\))?\s*\*?\s*</ion-label>', rota_text)

    active_secs = []
    agregadas_map = {}

    for sec_num, extra in matches:
        if extra:
            agregadas_map[sec_num] = extra
        else:
            active_secs.append(sec_num)

    print(f"\n🌐 Iniciando raspagem das {len(active_secs)} seções ativas (Ignoradas {len(agregadas_map)} agregadas)...")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--blink-settings=imagesEnabled=false")

    driver = webdriver.Chrome(options=options)

    base_url = "https://resultados.tse.jus.br/oficial/app/index.html#/eleicao/6257/uf/ce/mu/14630/zn/0076/cargo/1/vis/nominal/se/{sec}/dados-de-urna/boletim-de-urna"

    dataset = []
    failed_secs = []
    distritos_stats = {}

    t0 = time.time()

    for idx, sec in enumerate(active_secs, 1):
        t_start = time.time()
        url = base_url.format(sec=sec)
        driver.get(url)
        
        max_wait = 6.0
        poll_interval = 0.05
        start_wait = time.time()
        
        current_sec_dom = ""
        soup = None
        
        while time.time() - start_wait < max_wait:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            info_cols = soup.find_all('coluna-informacoes')
            for col in info_cols:
                desc = col.get('descricao') or (col.find(class_='descricao').get_text(strip=True) if col.find(class_='descricao') else '')
                if 'Se' in desc and 'Eleitoral' in desc and 'Zona' not in desc:
                    val = col.find(class_='valor').get_text(strip=True) if col.find(class_='valor') else ''
                    current_sec_dom = val
                    break
            if current_sec_dom == sec:
                break
            time.sleep(poll_interval)
            
        if current_sec_dom != sec:
            print(f"❌ [{idx}/{len(active_secs)}] Sec {sec} TIMEOUT")
            failed_secs.append(sec)
            continue
            
        local_votacao_tse = ""
        aptos = 0
        comparecimento = 0
        faltosos = 0
        votos_nominais = 0
        votos_branco = 0
        votos_nulo = 0
        total_apurado = 0
        
        for col in soup.find_all('coluna-informacoes'):
            desc = col.get('descricao') or (col.find(class_='descricao').get_text(strip=True) if col.find(class_='descricao') else '')
            val = col.find(class_='valor').get_text(strip=True) if col.find(class_='valor') else ''
            val_clean = val.replace('.', '').strip()
            
            if 'Local de Vota' in desc:
                local_votacao_tse = val
            elif 'Eleitores Aptos' in desc and 'Originais' not in desc and 'Tempor' not in desc:
                aptos = int(val_clean) if val_clean.isdigit() else 0
            elif 'Comparecimento' in desc:
                comparecimento = int(val_clean) if val_clean.isdigit() else 0
            elif 'Eleitores Faltosos' in desc:
                faltosos = int(val_clean) if val_clean.isdigit() else 0
            elif 'Votos nominais' in desc:
                votos_nominais = int(val_clean) if val_clean.isdigit() else 0
            elif 'branco' in desc:
                votos_branco = int(val_clean) if val_clean.isdigit() else 0
            elif 'Nulos' in desc:
                votos_nulo = int(val_clean) if val_clean.isdigit() else 0
            elif 'Total Apurado' in desc:
                total_apurado = int(val_clean) if val_clean.isdigit() else 0
                
        votes_dict = {}
        cargos = soup.find_all('div', class_='cargo-section')
        for c in cargos:
            title_el = c.find('h1', class_='title')
            title = title_el.get_text(strip=True) if title_el else ''
            if 'Presidente' in title:
                cand_items = c.find_all('lista-candidatos-item')
                for ci in cand_items:
                    ps = ci.find_all('p')
                    if len(ps) >= 2:
                        cand_num = ps[0].get_text(strip=True)
                        cand_votes = ps[1].get_text(strip=True).replace('.', '')
                        if cand_votes.isdigit():
                            votes_dict[cand_num] = int(cand_votes)

        lula_votes = votes_dict.get('13', 0)
        flavio_votes = votes_dict.get('22', 0)
        renan_votes = votes_dict.get('14', 0)
        caiado_votes = votes_dict.get('55', 0)
        cury_votes = votes_dict.get('70', 0)
        
        opositores_votes = flavio_votes + renan_votes + caiado_votes + cury_votes
        votos_validos = lula_votes + opositores_votes
        
        pct_lula = round((lula_votes / votos_validos * 100), 2) if votos_validos > 0 else 0.0
        pct_opositores = round((opositores_votes / votos_validos * 100), 2) if votos_validos > 0 else 0.0
        pct_abstencao = round((faltosos / aptos * 100), 2) if aptos > 0 else 0.0
        margem = lula_votes - opositores_votes
        
        # Nomenclatura Estatística
        if pct_lula >= 75.0:
            status = "Ampla Maioria Lula (≥75%)"
            prioridade = "Monitoramento Estatístico"
        elif pct_lula >= 65.0:
            status = "Maioria Absoluta Lula (65-75%)"
            prioridade = "Manutenção de Tendência"
        elif pct_lula >= 55.0:
            status = "Margem Moderada Lula (55-65%)"
            prioridade = "Consolidação de Votos"
        else:
            status = "Zona de Vulnerabilidade / Oposição Alta (<55%)"
            prioridade = "Recuperação de Margem / Alvo Tático"
            
        pdf_info = pdf_locations.get(sec, {})
        local_oficial = pdf_info.get('local_nome', local_votacao_tse)
        endereco_oficial = pdf_info.get('endereco', '')
        distrito = get_bairro_distrito(endereco_oficial, local_oficial)
        
        sec_data = {
            'secao': sec,
            'zona': '0076',
            'municipio': '14630 - Mauriti/CE',
            'local_votacao': local_votacao_tse,
            'local_oficial': local_oficial,
            'endereco_oficial': endereco_oficial,
            'distrito': distrito,
            'aptos': aptos,
            'comparecimento': comparecimento,
            'faltosos': faltosos,
            'pct_abstencao': pct_abstencao,
            'votos_nominais': votos_nominais,
            'votos_branco': votos_branco,
            'votos_nulo': votos_nulo,
            'total_apurado': total_apurado,
            'votos_validos': votos_validos,
            'candidatos': {
                '13_LULA': lula_votes,
                '22_FLAVIO_BOLSONARO': flavio_votes,
                '14_RENAN_SANTOS': renan_votes,
                '55_RONALDO_CAIADO': caiado_votes,
                '70_AUGUSTO_CURY': cury_votes
            },
            'lula_votos': lula_votes,
            'opositores_votos': opositores_votes,
            'pct_lula': pct_lula,
            'pct_opositores': pct_opositores,
            'margem_lula': margem,
            'status_tatico': status,
            'prioridade_tatica': prioridade
        }
        
        dataset.append(sec_data)
        
        # Agregação por Distrito
        if distrito not in distritos_stats:
            distritos_stats[distrito] = {
                'distrito': distrito,
                'secoes_count': 0,
                'aptos': 0,
                'comparecimento': 0,
                'faltosos': 0,
                'lula_votos': 0,
                'flavio_votos': 0,
                'opositores_votos': 0,
                'votos_validos': 0
            }
            
        ds = distritos_stats[distrito]
        ds['secoes_count'] += 1
        ds['aptos'] += aptos
        ds['comparecimento'] += comparecimento
        ds['faltosos'] += faltosos
        ds['lula_votos'] += lula_votes
        ds['flavio_votos'] += flavio_votes
        ds['opositores_votos'] += opositores_votes
        ds['votos_validos'] += votos_validos
        
        elapsed = time.time() - t_start
        if idx % 10 == 0 or idx == len(active_secs):
            print(f"⚡ [{idx}/{len(active_secs)}] Sec {sec} ({elapsed:.2f}s) | Lula: {lula_votes} ({pct_lula}%) vs Opp: {opositores_votes}")

    driver.quit()

    total_time = time.time() - t0
    print(f"\n🎉 Coleta concluída em {total_time:.1f}s. Seções raspadas: {len(dataset)}. Falhas: {len(failed_secs)}")

    # Calcular percentuais dos distritos
    distrito_list = []
    for d_name, d_data in distritos_stats.items():
        vv = d_data['votos_validos']
        l_v = d_data['lula_votos']
        op_v = d_data['opositores_votos']
        ap = d_data['aptos']
        ft = d_data['faltosos']
        
        d_data['pct_lula'] = round((l_v / vv * 100), 2) if vv > 0 else 0.0
        d_data['pct_opositores'] = round((op_v / vv * 100), 2) if vv > 0 else 0.0
        d_data['pct_abstencao'] = round((ft / ap * 100), 2) if ap > 0 else 0.0
        d_data['margem'] = l_v - op_v
        distrito_list.append(d_data)

    distrito_list.sort(key=lambda x: x['pct_lula'])

    # Exportar dataset JSON
    output_file = 'dados_eleicoes_mauriti.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'municipio': 'Mauriti / CE',
                'zona_eleitoral': '0076',
                'eleicao': 'Eleição Ordinária Federal - 2026',
                'data_coleta': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_secoes_ativas': len(dataset),
                'secoes_agregadas_ignoradas': len(agregadas_map),
                'pdf_locais_mapeados': True
            },
            'distritos': distrito_list,
            'secoes': dataset
        }, f, indent=2, ensure_ascii=False)

    print(f"💾 Dataset exportado com sucesso para '{output_file}'.")

if __name__ == "__main__":
    run_tse_scraper()
