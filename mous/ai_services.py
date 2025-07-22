"""
AI Services for MOU Management System
Provides intelligent clause analysis, risk assessment, and recommendations
"""

import re
import json
import logging
from typing import Dict, List, Tuple, Optional
from decimal import Decimal
from datetime import datetime

# Optional imports - install when ready for AI features
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
    import torch
    from sentence_transformers import SentenceTransformer
    import spacy
    HAS_AI_LIBS = True
except ImportError:
    HAS_AI_LIBS = False
    print("AI libraries not installed. Install with: pip install transformers torch sentence-transformers spacy")

logger = logging.getLogger(__name__)

class ClauseAnalyzer:
    """Main AI service for analyzing MOU clauses and documents"""
    
    def __init__(self):
        self.is_ready = False
        if HAS_AI_LIBS:
            self._initialize_models()
        else:
            logger.warning("AI models not available. Using fallback analysis.")
    
    def _initialize_models(self):
        """Initialize AI models (load lazily to avoid startup delays)"""
        try:
            # Legal BERT model for clause classification
            self.tokenizer = AutoTokenizer.from_pretrained('nlpaueb/legal-bert-base-uncased')
            self.classification_model = AutoModelForSequenceClassification.from_pretrained('nlpaueb/legal-bert-base-uncased')
            
            # Sentence transformer for semantic similarity
            self.similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # NLP pipeline for named entity recognition
            self.nlp_pipeline = pipeline('ner', model='dbmdz/bert-large-cased-finetuned-conll03-english')
            
            self.is_ready = True
            logger.info("AI models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load AI models: {str(e)}")
            self.is_ready = False
    
    def analyze_document(self, pdf_text: str, mou_title: str = "") -> Dict:
        """
        Comprehensive document analysis
        
        Args:
            pdf_text: Full text extracted from PDF
            mou_title: Title of the MOU for context
            
        Returns:
            Dictionary containing analysis results
        """
        if not pdf_text.strip():
            return self._empty_analysis()
        
        analysis = {
            'document_title': mou_title,
            'analysis_timestamp': datetime.now().isoformat(),
            'model_version': '1.0.0',
            'clauses': [],
            'overall_risk_score': 0.0,
            'risk_factors': [],
            'recommendations': [],
            'compliance_status': 'pending',
            'key_entities': [],
            'summary_stats': {}
        }
        
        if self.is_ready:
            # AI-powered analysis
            clauses = self._extract_clauses_ai(pdf_text)
            analysis['key_entities'] = self._extract_entities(pdf_text)
        else:
            # Fallback rule-based analysis
            clauses = self._extract_clauses_fallback(pdf_text)
        
        # Analyze each clause
        total_risk = 0
        for clause in clauses:
            clause_analysis = self.analyze_clause(clause)
            analysis['clauses'].append(clause_analysis)
            total_risk += clause_analysis['risk_score']
        
        # Calculate overall risk score
        if len(clauses) > 0:
            analysis['overall_risk_score'] = min(total_risk / len(clauses), 10.0)
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_document_recommendations(analysis)
        analysis['compliance_status'] = self._assess_compliance(analysis)
        analysis['summary_stats'] = self._calculate_summary_stats(analysis)
        
        return analysis
    
    def analyze_clause(self, clause_text: str) -> Dict:
        """
        Analyze individual clause
        
        Args:
            clause_text: Text of the clause to analyze
            
        Returns:
            Dictionary containing clause analysis
        """
        clause_analysis = {
            'text': clause_text,
            'type': 'unknown',
            'confidence': 0.0,
            'risk_score': 5.0,  # Default medium risk
            'risk_factors': [],
            'suggestions': [],
            'key_terms': [],
            'sentiment': 'neutral'
        }
        
        if self.is_ready:
            # AI-powered clause analysis
            clause_analysis.update(self._analyze_clause_ai(clause_text))
        else:
            # Fallback rule-based analysis
            clause_analysis.update(self._analyze_clause_fallback(clause_text))
        
        return clause_analysis
    
    def _analyze_clause_ai(self, clause_text: str) -> Dict:
        """AI-powered clause analysis using BERT"""
        try:
            # Tokenize and classify
            inputs = self.tokenizer(clause_text, return_tensors="pt", max_length=512, truncation=True, padding=True)
            
            with torch.no_grad():
                outputs = self.classification_model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Get clause type and confidence
            clause_type = self._classify_clause_type_ai(clause_text)
            confidence = float(torch.max(predictions))
            
            # Risk assessment
            risk_factors = self._identify_risk_factors(clause_text, clause_type)
            risk_score = self._calculate_risk_score(risk_factors)
            
            # Generate suggestions
            suggestions = self._generate_clause_suggestions(clause_text, clause_type, risk_factors)
            
            return {
                'type': clause_type,
                'confidence': confidence,
                'risk_score': risk_score,
                'risk_factors': risk_factors,
                'suggestions': suggestions,
                'key_terms': self._extract_key_terms(clause_text),
                'sentiment': self._analyze_sentiment(clause_text)
            }
            
        except Exception as e:
            logger.error(f"AI clause analysis failed: {str(e)}")
            return self._analyze_clause_fallback(clause_text)
    
    def _analyze_clause_fallback(self, clause_text: str) -> Dict:
        """Rule-based fallback clause analysis"""
        clause_type = self._classify_clause_type_fallback(clause_text)
        risk_factors = self._identify_risk_factors_fallback(clause_text)
        risk_score = len(risk_factors) * 1.5  # Simple risk calculation
        
        return {
            'type': clause_type,
            'confidence': 0.7 if clause_type != 'unknown' else 0.3,
            'risk_score': min(risk_score, 10.0),
            'risk_factors': risk_factors,
            'suggestions': self._generate_fallback_suggestions(clause_type, risk_factors),
            'key_terms': self._extract_key_terms_fallback(clause_text),
            'sentiment': 'neutral'
        }
    
    def _extract_clauses_ai(self, text: str) -> List[str]:
        """Extract clauses using AI sentence segmentation"""
        # Use spacy for better sentence segmentation
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(text)
            
            clauses = []
            current_clause = ""
            
            for sent in doc.sents:
                sent_text = sent.text.strip()
                if len(sent_text) < 20:  # Too short to be a meaningful clause
                    current_clause += " " + sent_text
                else:
                    if current_clause:
                        clauses.append(current_clause.strip())
                    current_clause = sent_text
            
            if current_clause:
                clauses.append(current_clause.strip())
            
            return [c for c in clauses if len(c) > 50]  # Filter very short clauses
            
        except Exception as e:
            logger.error(f"AI clause extraction failed: {str(e)}")
            return self._extract_clauses_fallback(text)
    
    def _extract_clauses_fallback(self, text: str) -> List[str]:
        """Fallback rule-based clause extraction"""
        # Split by common clause indicators
        clause_patterns = [
            r'\n\d+\.\s',  # Numbered clauses
            r'\n[A-Z]\.\s',  # Letter clauses
            r'\n\([a-z]\)',  # Parenthetical clauses
            r'WHEREAS',
            r'NOW, THEREFORE',
            r'The parties agree',
            r'It is understood',
        ]
        
        clauses = []
        text_parts = [text]
        
        for pattern in clause_patterns:
            new_parts = []
            for part in text_parts:
                splits = re.split(pattern, part, flags=re.IGNORECASE | re.MULTILINE)
                new_parts.extend([s.strip() for s in splits if len(s.strip()) > 50])
            text_parts = new_parts
        
        return text_parts
    
    def _classify_clause_type_fallback(self, clause_text: str) -> str:
        """Rule-based clause type classification"""
        clause_lower = clause_text.lower()
        
        # Define keyword patterns for different clause types
        clause_patterns = {
            'termination': ['termination', 'terminate', 'end', 'expir', 'cancel'],
            'payment': ['payment', 'fee', 'cost', 'expense', 'invoice', 'billing'],
            'liability': ['liable', 'liability', 'damages', 'indemnif', 'responsible'],
            'confidentiality': ['confidential', 'non-disclosure', 'proprietary', 'secret'],
            'intellectual_property': ['intellectual property', 'copyright', 'patent', 'trademark', 'ip'],
            'dispute_resolution': ['dispute', 'arbitration', 'mediation', 'court', 'litigation'],
            'governing_law': ['governing law', 'jurisdiction', 'applicable law'],
            'force_majeure': ['force majeure', 'acts of god', 'unforeseeable'],
        }
        
        for clause_type, keywords in clause_patterns.items():
            if any(keyword in clause_lower for keyword in keywords):
                return clause_type
        
        return 'general'
    
    def _identify_risk_factors_fallback(self, clause_text: str) -> List[str]:
        """Identify risk factors using rule-based patterns"""
        risks = []
        clause_lower = clause_text.lower()
        
        # High-risk patterns
        high_risk_patterns = {
            'Unlimited liability': ['unlimited liability', 'unlimited damages'],
            'Vague termination': ['may terminate', 'at any time', 'without cause'],
            'No dispute resolution': len(re.findall(r'dispute|arbitration|mediation', clause_lower)) == 0,
            'Excessive penalties': ['penalty', 'fine', 'liquidated damages'],
            'Broad indemnification': ['indemnify.*all', 'hold harmless.*any'],
        }
        
        for risk_name, patterns in high_risk_patterns.items():
            if isinstance(patterns, bool):
                if patterns and 'termination' in clause_lower:
                    risks.append(risk_name)
            else:
                if any(re.search(pattern, clause_lower) for pattern in patterns):
                    risks.append(risk_name)
        
        return risks
    
    def _generate_fallback_suggestions(self, clause_type: str, risk_factors: List[str]) -> List[str]:
        """Generate suggestions based on clause type and risk factors"""
        suggestions = []
        
        if 'Unlimited liability' in risk_factors:
            suggestions.append("Consider limiting liability to a specific amount or percentage of contract value")
        
        if 'Vague termination' in risk_factors:
            suggestions.append("Add specific termination conditions and notice requirements")
        
        if clause_type == 'payment' and not any('payment' in risk.lower() for risk in risk_factors):
            suggestions.append("Ensure payment terms are clearly defined with specific due dates")
        
        if clause_type == 'confidentiality':
            suggestions.append("Define what constitutes confidential information and exceptions")
        
        return suggestions
    
    def _extract_key_terms_fallback(self, clause_text: str) -> List[str]:
        """Extract key terms using simple pattern matching"""
        # Look for capitalized terms, dates, monetary amounts
        terms = []
        
        # Find monetary amounts
        money_pattern = r'\$[\d,]+(?:\.\d{2})?'
        terms.extend(re.findall(money_pattern, clause_text))
        
        # Find dates
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\w+ \d{1,2}, \d{4}\b'
        terms.extend(re.findall(date_pattern, clause_text))
        
        # Find capitalized terms (potential proper nouns)
        cap_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
        terms.extend(re.findall(cap_pattern, clause_text))
        
        return list(set(terms))[:10]  # Return unique terms, max 10
    
    def _calculate_risk_score(self, risk_factors: List[str]) -> float:
        """Calculate risk score based on identified risk factors"""
        if not risk_factors:
            return 3.0  # Low default risk
        
        # Weight different risk factors
        risk_weights = {
            'Unlimited liability': 3.0,
            'Vague termination': 2.0,
            'No dispute resolution': 2.5,
            'Excessive penalties': 2.0,
            'Broad indemnification': 2.5,
        }
        
        total_risk = sum(risk_weights.get(risk, 1.5) for risk in risk_factors)
        return min(total_risk, 10.0)
    
    def _generate_document_recommendations(self, analysis: Dict) -> List[str]:
        """Generate overall document recommendations"""
        recommendations = []
        risk_score = analysis['overall_risk_score']
        
        if risk_score > 7:
            recommendations.append("High risk detected - recommend legal review before signing")
        elif risk_score > 5:
            recommendations.append("Medium risk - review flagged clauses carefully")
        
        # Check for missing standard clauses
        clause_types = [c['type'] for c in analysis['clauses']]
        standard_clauses = ['termination', 'liability', 'dispute_resolution', 'governing_law']
        
        missing_clauses = [c for c in standard_clauses if c not in clause_types]
        if missing_clauses:
            recommendations.append(f"Consider adding standard clauses: {', '.join(missing_clauses)}")
        
        return recommendations
    
    def _assess_compliance(self, analysis: Dict) -> str:
        """Assess compliance status based on analysis"""
        risk_score = analysis['overall_risk_score']
        high_risk_count = sum(1 for c in analysis['clauses'] if c['risk_score'] > 7)
        
        if high_risk_count > 2 or risk_score > 8:
            return 'non_compliant'
        elif high_risk_count > 0 or risk_score > 6:
            return 'review_required'
        else:
            return 'compliant'
    
    def _calculate_summary_stats(self, analysis: Dict) -> Dict:
        """Calculate summary statistics"""
        clauses = analysis['clauses']
        if not clauses:
            return {}
        
        return {
            'total_clauses': len(clauses),
            'high_risk_clauses': sum(1 for c in clauses if c['risk_score'] > 7),
            'medium_risk_clauses': sum(1 for c in clauses if 4 <= c['risk_score'] <= 7),
            'low_risk_clauses': sum(1 for c in clauses if c['risk_score'] < 4),
            'most_common_clause_type': self._most_common_clause_type(clauses),
            'average_confidence': sum(c['confidence'] for c in clauses) / len(clauses),
        }
    
    def _most_common_clause_type(self, clauses: List[Dict]) -> str:
        """Find the most common clause type"""
        types = [c['type'] for c in clauses]
        return max(set(types), key=types.count) if types else 'unknown'
    
    def _empty_analysis(self) -> Dict:
        """Return empty analysis structure"""
        return {
            'document_title': '',
            'analysis_timestamp': datetime.now().isoformat(),
            'model_version': '1.0.0',
            'clauses': [],
            'overall_risk_score': 0.0,
            'risk_factors': [],
            'recommendations': ['No content available for analysis'],
            'compliance_status': 'unknown',
            'key_entities': [],
            'summary_stats': {}
        }


# Helper functions for integration
def analyze_mou_document(pdf_text: str, mou_title: str = "") -> Dict:
    """
    Main function to analyze MOU document
    Usage: result = analyze_mou_document(pdf_text, mou_title)
    """
    analyzer = ClauseAnalyzer()
    return analyzer.analyze_document(pdf_text, mou_title)


def get_clause_recommendations(clause_text: str) -> Dict:
    """
    Get recommendations for a specific clause
    Usage: recommendations = get_clause_recommendations(clause_text)
    """
    analyzer = ClauseAnalyzer()
    return analyzer.analyze_clause(clause_text)
