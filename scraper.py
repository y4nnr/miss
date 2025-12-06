import requests
from bs4 import BeautifulSoup
import re
from app import app, db, Candidate

def scrape_candidates():
    """Scrape candidate data from Le Parisien website"""
    url = "https://www.leparisien.fr/culture-loisirs/miss-france/miss-france-2026-decouvrez-les-30-portraits-officiels-des-pretendantes-a-la-couronne-10-11-2025-C6KJMX43PFCEXJMTYTHYDNORXU.php"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    candidates_data = []
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all h2 tags that contain candidate names
        h2_tags = soup.find_all('h2')
        
        for h2 in h2_tags:
            text = h2.get_text(strip=True)
            
            # Check if this is a candidate header (format: "Name, Miss Region")
            if 'Miss' in text and not text.startswith('Miss France') and ',' in text:
                # Extract name and region
                parts = text.split(',')
                if len(parts) >= 2:
                    name = parts[0].strip()
                    region = parts[1].strip()
                    
                    # Skip if it's not a valid candidate header
                    if not name or not region.startswith('Miss'):
                        continue
                    
                    # Find image - look for img tags near this h2
                    image_url = None
                    
                    # Method 1: Look for figure or div with img after h2
                    current = h2.find_next_sibling()
                    search_count = 0
                    while current and search_count < 10:
                        if current.name == 'figure':
                            img = current.find('img')
                            if img:
                                image_url = img.get('src') or img.get('data-src')
                                if image_url:
                                    break
                        elif current.name == 'div':
                            img = current.find('img')
                            if img:
                                image_url = img.get('src') or img.get('data-src')
                                if image_url:
                                    break
                        elif current.name == 'img':
                            image_url = current.get('src') or current.get('data-src')
                            if image_url:
                                break
                        current = current.find_next_sibling()
                        search_count += 1
                    
                    # Method 2: Look backwards for images in parent containers
                    if not image_url:
                        parent = h2.find_parent(['article', 'div', 'section'])
                        if parent:
                            # Find all images in the parent, get the one closest to this h2
                            images = parent.find_all('img')
                            for img in images:
                                # Check if image is after this h2
                                if img.find_previous('h2') == h2:
                                    image_url = img.get('src') or img.get('data-src')
                                    if image_url:
                                        break
                    
                    # Fix image URL
                    if image_url:
                        if image_url.startswith('//'):
                            image_url = 'https:' + image_url
                        elif image_url.startswith('/'):
                            image_url = 'https://www.leparisien.fr' + image_url
                        elif not image_url.startswith('http'):
                            image_url = 'https://www.leparisien.fr' + image_url
                    
                    # Extract description and age from following paragraphs
                    description = ""
                    age = None
                    current = h2.find_next_sibling()
                    para_count = 0
                    while current and para_count < 5:
                        if current.name == 'p':
                            text_content = current.get_text(strip=True)
                            if text_content and len(text_content) > 20:  # Only meaningful paragraphs
                                description += text_content + " "
                                # Try to extract age
                                age_match = re.search(r'(\d{1,2})\s*ans', text_content)
                                if age_match and not age:
                                    try:
                                        age = int(age_match.group(1))
                                    except:
                                        pass
                                para_count += 1
                        elif current.name == 'h2':  # Stop at next candidate
                            break
                        current = current.find_next_sibling()
                    
                    if name and region:
                        candidates_data.append({
                            'name': name,
                            'region': region,
                            'image_url': image_url or '',
                            'age': age,
                            'description': description.strip()
                        })
        
        print(f"Scraped {len(candidates_data)} candidates from website")
        
    except Exception as e:
        print(f"Error scraping website: {e}")
        import traceback
        traceback.print_exc()
    
    # Known candidates from the article (with image URLs pattern)
    known_candidates = {
        'Miss Alsace': {'name': 'Julie Decroix', 'age': 20, 'description': 'Originaire de Blotzheim, étudiante en psychologie à l\'université de Strasbourg'},
        'Miss Aquitaine': {'name': 'Aïnhoa Lahitete', 'age': 19, 'description': 'Originaire d\'Hendaye, étudiante en première année de médecine'},
        'Miss Auvergne': {'name': 'Alice De Lima Guimaraes', 'age': 19, 'description': 'Native de Vichy, classe préparatoire littéraire à Clermont-Ferrand'},
        'Miss Bourgogne': {'name': 'Charlène Laurin', 'age': 22, 'description': 'Originaire de L\'Abergement-Sainte-Colombe, préparatrice en pharmacie'},
        'Miss Bretagne': {'name': 'Ninon Crolas', 'age': 18, 'description': 'Originaire de Ploërmel, étudiante infirmière à Pontivy'},
        'Miss Centre-Val-de-Loire': {'name': 'Anna Valero', 'age': 19, 'description': 'Originaire d\'Orléans, étudiante en troisième année de médecine à Tours'},
        'Miss Champagne-Ardenne': {'name': 'Ynès Lallemand', 'age': 19, 'description': 'Rémoise, étudiante en droit à l\'Institut Catholique de Paris'},
        'Miss Réunion': {'name': 'Priya Padavatan', 'age': 19, 'description': 'De Bras-Panon, étudiante en troisième année de licence de droit'},
        'Miss Rhône-Alpes': {'name': 'Noémie Baiamonte', 'age': 21, 'description': 'Originaire de Replonges, étudiante en première année de marketing de luxe à Villeurbanne'},
        'Miss Roussillon': {'name': 'Déborah Adelin-Chabal', 'age': 18, 'description': 'Perpignanaise, danseuse professionnelle'},
        'Miss Tahiti': {'name': 'Hinaupoko Devèze', 'age': 24, 'description': 'Native de Mahina, secrétaire administrative'},
    }
    
    # All 30 Miss France regions (standard list)
    all_regions = [
        'Miss Alsace', 'Miss Aquitaine', 'Miss Auvergne', 'Miss Bourgogne',
        'Miss Bretagne', 'Miss Centre-Val-de-Loire', 'Miss Champagne-Ardenne',
        'Miss Corse', 'Miss Côte d\'Azur', 'Miss Franche-Comté',
        'Miss Guadeloupe', 'Miss Guyane', 'Miss Île-de-France', 'Miss Languedoc',
        'Miss Limousin', 'Miss Lorraine', 'Miss Martinique', 'Miss Mayotte',
        'Miss Midi-Pyrénées', 'Miss Normandie', 'Miss Nord-Pas-de-Calais',
        'Miss Nouvelle-Calédonie', 'Miss Pays de Loire', 'Miss Picardie',
        'Miss Poitou-Charentes', 'Miss Provence', 'Miss Réunion',
        'Miss Rhône-Alpes', 'Miss Roussillon', 'Miss Tahiti'
    ]
    
    # If we didn't get enough candidates from scraping, merge with known data
    if len(candidates_data) < 30:
        # Create a dict from scraped data for easy lookup
        scraped_dict = {c['region']: c for c in candidates_data}
        
        # Build complete list
        final_candidates = []
        for region in all_regions:
            if region in scraped_dict:
                # Use scraped data
                final_candidates.append(scraped_dict[region])
            elif region in known_candidates:
                # Use known data, try to get image URL
                candidate = known_candidates[region].copy()
                candidate['region'] = region
                # Try to construct image URL (SIPA images pattern)
                # Images are typically hosted on leparisien.fr or sipa images
                candidate['image_url'] = ''  # Will be filled if we can find it
                final_candidates.append(candidate)
            else:
                # Placeholder for unknown candidates
                final_candidates.append({
                    'name': f'Candidate {region}',
                    'region': region,
                    'age': None,
                    'description': '',
                    'image_url': ''
                })
        
        candidates_data = final_candidates
    
    # Try to find images for candidates that don't have them
    # Look for images with SIPA in the URL or alt text
    if candidates_data:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            all_images = soup.find_all('img')
            
            # Create a mapping of candidate names to image URLs
            name_to_image = {}
            for img in all_images:
                src = img.get('src') or img.get('data-src', '')
                alt = img.get('alt', '')
                
                # Look for SIPA images (official photos)
                if 'SIPA' in src or 'SIPA' in alt:
                    # Try to extract candidate name from alt or nearby text
                    parent = img.find_parent(['figure', 'div', 'article'])
                    if parent:
                        # Look for h2 with candidate name nearby
                        h2 = parent.find('h2') or parent.find_previous('h2')
                        if h2:
                            h2_text = h2.get_text(strip=True)
                            if ',' in h2_text:
                                name = h2_text.split(',')[0].strip()
                                if src:
                                    if src.startswith('//'):
                                        src = 'https:' + src
                                    elif src.startswith('/'):
                                        src = 'https://www.leparisien.fr' + src
                                    elif not src.startswith('http'):
                                        src = 'https://www.leparisien.fr' + src
                                    name_to_image[name] = src
            
            # Update candidates with found images
            for candidate in candidates_data:
                if not candidate.get('image_url') and candidate['name'] in name_to_image:
                    candidate['image_url'] = name_to_image[candidate['name']]
        except:
            pass
    
    return candidates_data

def populate_candidates():
    """Populate database with scraped candidate data"""
    with app.app_context():
        # Scrape candidates
        candidates_data = scrape_candidates()
        
        # Update or create candidates
        for data in candidates_data:
            # Try to find existing candidate by region
            candidate = Candidate.query.filter_by(region=data['region']).first()
            
            if candidate:
                # Update existing candidate
                candidate.name = data['name']
                if data.get('image_url'):
                    candidate.image_url = data['image_url']
                if data.get('age'):
                    candidate.age = data['age']
                if data.get('description'):
                    candidate.description = data['description']
            else:
                # Create new candidate
                candidate = Candidate(
                    name=data['name'],
                    region=data['region'],
                    image_url=data.get('image_url', ''),
                    age=data.get('age'),
                    description=data.get('description', '')
                )
                db.session.add(candidate)
        
        db.session.commit()
        print(f"✅ Updated/Added {len(candidates_data)} candidates to the database")
        
        # Print summary
        all_candidates = Candidate.query.all()
        with_images = sum(1 for c in all_candidates if c.image_url)
        print(f"📸 {with_images} candidates have images")
        print(f"📊 Total candidates in database: {len(all_candidates)}")

if __name__ == '__main__':
    populate_candidates()
