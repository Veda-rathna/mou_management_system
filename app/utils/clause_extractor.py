import re
import spacy
from collections import defaultdict

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    # If model not available, use a simpler approach
    nlp = None

def extract_clauses(text):
    """
    Extract key legal clauses from MOU text
    """
    clauses = {
        'validity': None,
        'termination': None,
        'confidentiality': None,
        'governing_law': None
    }
    
    # Define patterns for each clause type
    patterns = {
        'validity': [
            r'(?:ARTICLE|CLAUSE|Section)[\s\d\.]*(?:VALIDITY|DURATION|TERM|PERIOD).*?(?:\n\n|\n(?:ARTICLE|CLAUSE|Section))',
            r'(?:validity|duration|term|period|effective).*?(?:of|for|this).*?(?:agreement|MOU).*?(?:\.|;|\n)',
            r'This.*?(?:agreement|MOU).*?(?:valid|effective).*?(?:for|period|duration).*?(?:\.|;|\n)'
        ],
        'termination': [
            r'(?:ARTICLE|CLAUSE|Section)[\s\d\.]*(?:TERMINATION).*?(?:\n\n|\n(?:ARTICLE|CLAUSE|Section))',
            r'(?:termination|terminate).*?(?:agreement|MOU).*?(?:\.|;|\n)',
            r'(?:Either|Any).*?(?:party|organization).*?(?:terminate|termination).*?(?:\.|;|\n)'
        ],
        'confidentiality': [
            r'(?:ARTICLE|CLAUSE|Section)[\s\d\.]*(?:CONFIDENTIALITY).*?(?:\n\n|\n(?:ARTICLE|CLAUSE|Section))',
            r'(?:confidential|confidentiality).*?(?:information|data|material).*?(?:\.|;|\n)',
            r'(?:parties|organizations).*?(?:maintain|keep|ensure).*?(?:confidentiality|confidential).*?(?:\.|;|\n)'
        ],
        'governing_law': [
            r'(?:ARTICLE|CLAUSE|Section)[\s\d\.]*(?:GOVERNING LAW|APPLICABLE LAW|JURISDICTION).*?(?:\n\n|\n(?:ARTICLE|CLAUSE|Section))',
            r'(?:governed|governed by|subject to).*?(?:laws|law|jurisdiction).*?(?:of|in).*?(?:\.|;|\n)',
            r'(?:disputes|disagreements).*?(?:resolved|settled).*?(?:courts|jurisdiction|arbitration).*?(?:of|in).*?(?:\.|;|\n)'
        ]
    }
    
    # Try to extract clauses using regex patterns
    for clause_type, clause_patterns in patterns.items():
        for pattern in clause_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                clause_text = match.group(0).strip()
                # Clean up the text
                clause_text = re.sub(r'\n+', ' ', clause_text)
                clause_text = re.sub(r'\s+', ' ', clause_text)
                
                # If we found a clause, store it and break
                if clause_text and len(clause_text) > 20:  # Avoid short matches
                    clauses[clause_type] = clause_text
                    break
    
    # If spaCy is available, use NLP to improve extraction
    if nlp and text:
        # Process the text with spaCy
        doc = nlp(text[:1000000])  # Limit text size to avoid memory issues
        
        # Create a dictionary to store sentences by their relevance to clause types
        clause_sentences = defaultdict(list)
        
        # Keywords for each clause type
        keywords = {
            'validity': ['valid', 'validity', 'duration', 'period', 'term', 'effective', 'commence'],
            'termination': ['terminate', 'termination', 'end', 'cancel', 'revoke', 'rescind'],
            'confidentiality': ['confidential', 'confidentiality', 'secret', 'disclosure', 'proprietary'],
            'governing_law': ['govern', 'law', 'jurisdiction', 'court', 'arbitration', 'dispute', 'resolution']
        }
        
        # Analyze each sentence
        for sent in doc.sents:
            sent_text = sent.text.strip()
            
            # Skip short sentences
            if len(sent_text) < 20:
                continue
            
            # Check each clause type
            for clause_type, words in keywords.items():
                # If we already have this clause from regex, skip
                if clauses[clause_type]:
                    continue
                
                # Check if any keywords are in the sentence
                if any(word.lower() in sent_text.lower() for word in words):
                    clause_sentences[clause_type].append(sent_text)
        
        # For each clause type that wasn't found with regex, use the most relevant sentence
        for clause_type, sentences in clause_sentences.items():
            if not clauses[clause_type] and sentences:
                # Use the longest sentence as it likely contains more information
                clauses[clause_type] = max(sentences, key=len)
    
    return clauses
