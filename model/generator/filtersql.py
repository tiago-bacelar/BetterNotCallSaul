import sys

import re

r = re.compile(r'public\.(\w+)')

c1 = """CREATE TABLE dreapp_document (
    document_id INT PRIMARY KEY,
    parent_id INT,
    document_type VARCHAR(50),
    document_number VARCHAR(50),
    department VARCHAR(100),
    source_info VARCHAR(255),
    additional_info TEXT,
    is_public BOOLEAN,
    is_archived BOOLEAN,
    creation_date DATE,
    description TEXT,
    author VARCHAR(100),
    tags TEXT,
    is_active BOOLEAN,
    last_modified VARCHAR(255),
    is_deleted BOOLEAN,
    document_year VARCHAR(50),
    version INT,
    priority VARCHAR(10)
);"""

c2 = """CREATE TABLE dreapp_documenttext (
    documenttext_id INT PRIMARY KEY,
    document_id INT,
    timestamp VARCHAR(255),
    url VARCHAR(255),
    text_content TEXT
);"""

print(c1)
print(c2)


for line in sys.stdin:
    if line.startswith('SET') or line.startswith('SELECT'):
        continue
    else:
        print(re.sub(r,r'\1',line),end="")
    
        
    
    