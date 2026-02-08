#!/usr/bin/env python3
import os
import re
import yaml
from pathlib import Path

def extract_content(html_file):
    """Extract content between <main> and </main> tags"""
    with open(html_file, 'r') as f:
        content = f.read()
    
    # Extract title
    title_match = re.search(r'<title>(.*?)</title>', content)
    title = title_match.group(1) if title_match else "Bug Hunter Tools"
    
    # Extract description
    desc_match = re.search(r'<meta name="description" content="(.*?)"', content)
    description = desc_match.group(1) if desc_match else ""
    
    # Extract main content
    main_match = re.search(r'<main class="container">(.*?)</main>', content, re.DOTALL)
    main_content = main_match.group(1).strip() if main_match else ""
    
    return title, description, main_content

def create_njk_file(src_file, title, description, content, permalink):
    """Create .njk file with frontmatter using proper YAML"""
    # Use yaml.dump for proper escaping
    frontmatter_data = {
        'layout': 'base.njk',
        'title': title,
        'description': description,
        'permalink': permalink
    }
    
    frontmatter_yaml = yaml.dump(frontmatter_data, default_flow_style=False, allow_unicode=True)
    
    full_content = f"---\n{frontmatter_yaml}---\n\n{content}\n"
    
    with open(src_file, 'w') as f:
        f.write(full_content)
    print(f"✓ Created {src_file}")

# Convert index.html
print("Converting pages...")
title, desc, content = extract_content('index.html')
create_njk_file('src/index.njk', title, desc, content, '/index.html')

# Convert privacy.html
title, desc, content = extract_content('privacy.html')
create_njk_file('src/privacy.njk', title, desc, content, '/privacy.html')

# Convert articles
articles = [
    'articles/index.html',
    'articles/security-testing-tools-2026.html',
    'articles/bug-bounty-starter-kit.html',
    'articles/linkedin-api-bola-bypass.html',
    'articles/chainlit-ai-vulnerabilities-cve-2026-22218.html',
    'articles/n8n-rce-cve-2026-21858.html'
]

for article in articles:
    if os.path.exists(article):
        title, desc, content = extract_content(article)
        basename = os.path.basename(article)
        src_file = f'src/articles/{basename.replace(".html", ".njk")}'
        permalink = f'/articles/{basename}'
        create_njk_file(src_file, title, desc, content, permalink)

print("\n✅ All pages converted!")
