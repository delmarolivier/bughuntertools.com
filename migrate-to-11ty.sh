#!/bin/bash

# Migration script: Convert existing HTML pages to 11ty structure
# Extracts content between <main> tags and adds frontmatter

cd /home/delmar/.openclaw/agents/jenn/workspace/projects/altclaw/bughuntertools.com

# Function to extract content and create new file
migrate_page() {
    local input_file=$1
    local output_file=$2
    local title=$3
    local description=$4
    
    # Extract content between <main> and </main>
    content=$(sed -n '/<main class="container">/,/<\/main>/p' "$input_file" | sed '1d;$d')
    
    # Create file with frontmatter
    cat > "$output_file" << EOF
---
layout: base.njk
title: $title
description: $description
---

$content
EOF
}

echo "Starting migration to 11ty..."

# For now, let's just build the current HTML as-is
# We'll do a proper migration in phases

echo "Phase 1: Test build with existing structure"
npx @11ty/eleventy --input=. --output=_site_test --formats=html

echo "Migration script complete"
