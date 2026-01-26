from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import List, Dict, Optional
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from app.config import settings

class ResumeMatcher:
    # Class-level model instance for lazy loading (shared across all instances)
    _model: Optional[SentenceTransformer] = None
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=settings.openai_api_key,
            temperature=0.3
        )
    
    @classmethod
    def _get_model(cls) -> SentenceTransformer:
        """Lazy load the Sentence Transformer model (only loads once)"""
        if cls._model is None:
            print("Loading Sentence Transformer model (all-MiniLM-L6-v2)...")
            cls._model = SentenceTransformer('all-MiniLM-L6-v2')
            print("Model loaded successfully!")
        return cls._model
    
    async def match_resume_to_jobs(self, resume_text: str, jobs: List[Dict]) -> List[Dict]:
        resume_analysis = await self._analyze_resume(resume_text)
        
        matched_jobs = []
        for job in jobs:
            match_details = self._calculate_match_score(resume_analysis, job)
            
            # Debug logging to see all scores
            print(f"Job: {job.get('title', 'Unknown')} | Company: {job.get('company', 'Unknown')} | Score: {round(match_details['final_score'], 2)}%")
            
            if match_details['final_score'] >= 60:
                job_copy = job.copy()
                job_copy["match_score"] = round(match_details['final_score'], 2)
                job_copy["match_level"] = self._get_match_level(match_details['final_score'])
                job_copy["matched_skills"] = match_details['matched_skills']
                job_copy["missed_skills"] = match_details['missed_skills']
                job_copy["title_score"] = round(match_details['title_score'] * 100, 2)
                job_copy["skill_score"] = round(match_details['skill_score'] * 100, 2)
                job_copy["semantic_score"] = round(match_details['semantic_score'] * 100, 2)
                matched_jobs.append(job_copy)
        
        matched_jobs.sort(key=lambda x: x["match_score"], reverse=True)
        
        return matched_jobs
    
    async def _analyze_resume(self, resume_text: str) -> Dict:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert resume analyzer. Extract the following information from the resume:
            1. Job titles/roles the candidate has held
            2. Technical skills (programming languages, frameworks, tools)
            3. Key responsibilities and achievements
            4. Years of experience (estimate if not explicit)
            5. Education level
            
            Return the analysis in a structured format."""),
            ("user", "Resume:\n{resume_text}")
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"resume_text": resume_text})
        
        skills = self._extract_skills(resume_text)
        job_titles = self._extract_job_titles(resume_text)
        
        # Debug: Print extracted skills and titles
        print(f"\n=== RESUME EXTRACTION DEBUG ===")
        print(f"Skills extracted: {skills}")
        print(f"Titles extracted: {job_titles}")
        print(f"Resume text length: {len(resume_text)} chars")
        print(f"Resume preview: {resume_text[:200]}...")
        print("=" * 50 + "\n")
        
        return {
            "raw_text": resume_text,
            "skills": skills,
            "job_titles": job_titles,
            "llm_analysis": response.content
        }
    
    def _extract_skills(self, text: str) -> List[str]:
        common_skills = [
            # Programming Languages
            "python", "javascript", "typescript", "java", "c++", "c#", "ruby", "php", "golang", "rust", "shell", "bash",
            # Web Frameworks
            "react", "vue", "angular", "node.js", "express", "django", "flask", "fastapi",
            "next.js", "nextjs", "nuxt", "svelte", "sveltekit", "remix",
            # State Management
            "redux", "redux toolkit", "mobx", "zustand", "recoil",
            # Visualization
            "d3.js", "d3", "three.js", "chart.js", "recharts", "streamlit", "spacy",
            # Styling
            "tailwind", "tailwindcss", "sass", "scss", "styled-components", "emotion", "css modules",
            # Build Tools
            "webpack", "vite", "rollup", "parcel", "esbuild", "turbopack",
            # Testing
            "jest", "cypress", "playwright", "vitest", "testing library", "mocha", "chai", "selenium",
            # Design
            "figma", "sketch", "adobe xd",
            # Databases
            "sql", "postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch", "sqlite", "digitalocean", "rabbitmq",
            "meilisearch", "snowflake", "bigquery", "redshift",
            # Cloud & DevOps
            "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s", "terraform", "pulumi", "s3", "ec2", "lambda", "cloud run", "container registry",
            "automl", "vertex", "vertex ai", "sagemaker", "gcloud sdk", "compute engine", "cloud storage",
            # CI/CD & Version Control
            "git", "ci/cd", "jenkins", "github actions", "uvicorn", "github",
            # ML/AI Frameworks & Libraries
            "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn", "sklearn",
            "huggingface", "transformers", "sentence transformers", "simpletransformers", "adapters",
            "haystack", "deepavlov", "keras", "jax", "onnx", "mlflow", "weights & biases", "wandb",
            "apex", "mixed precision", "data parallel", "multi-gpu",
            # NLP Libraries
            "nlp", "natural language processing", "spacy", "nltk", "gensim", "beautifulsoup", "beautiful soup",
            "bert", "gpt", "t5", "roberta", "distilbert", "xlm", "deberta", "xlnet", "bart", "pegasus",
            # Data Science & ML Tools
            "pandas", "numpy", "scipy", "matplotlib", "seaborn", "jupyter", "conda", "dataframe", "arrow",
            "data.table", "eda", "dplyr", "airflow", "dagster", "spark", "flink", "kafka", "kinesis",
            # APIs & Architecture
            "rest api", "graphql", "microservices", "agile", "scrum", "fastapi", "gunicorn", "websocket",
            "etl", "elt", "data pipeline", "mlops", "feature store",
            # Web Technologies
            "websockets", "webgl", "canvas", "html", "css", "linux", "debian",
            # Performance & Accessibility
            "lighthouse", "web vitals", "core web vitals", "performance optimization",
            "wcag", "accessibility", "a11y", "aria",
            # Specialized AI/ML
            "computer vision", "nlp models", "dialogue modeling", "parlai", "serverless", "boto3", "django",
            "generative ai", "genai", "llm", "large language model", "fine-tuning", "model training",
            "inference", "model deployment", "vector database", "embedding"
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        # Skills that need word boundary matching to avoid false positives
        word_boundary_skills = ['rust', 'java', 'ruby', 'php', 'sql', 'git', 'css', 'html', 'r', 'c', 'golang']
        
        for skill in common_skills:
            if skill in word_boundary_skills:
                # Use word boundary matching for short skills
                import re
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills.append(skill)
            else:
                # Regular substring matching for longer skills
                if skill in text_lower:
                    found_skills.append(skill)
        
        return found_skills
    
    def _extract_job_titles(self, text: str) -> List[str]:
        common_titles = [
            # Software Engineering
            "software engineer", "senior software engineer", "staff engineer", "principal engineer",
            "frontend developer", "frontend engineer", "front-end developer", "front-end engineer", "front end developer", "front end engineer",
            "backend developer", "backend engineer", "back-end developer", "back-end engineer", "back end developer", "back end engineer",
            "full stack developer", "full stack engineer", "fullstack developer", "fullstack engineer", "full-stack developer", "full-stack engineer",
            # DevOps & Infrastructure
            "devops engineer", "sre", "site reliability engineer", "platform engineer", "cloud engineer",
            # AI/ML/Data Science
            "data scientist", "machine learning engineer", "ml engineer", "ai engineer", "artificial intelligence engineer",
            "deep learning engineer", "nlp engineer", "natural language processing engineer", "computer vision engineer",
            "ai/ml engineer", "applied scientist", "research scientist", "data engineer",
            "mlops engineer", "ai software engineer", "generative ai engineer", "genai engineer",
            # Leadership & Architecture
            "engineering manager", "tech lead", "technical lead", "architect", "solutions architect",
            # Web & UI/UX
            "web developer", "ui engineer", "ux engineer", "ui/ux engineer"
        ]
        
        text_lower = text.lower()
        found_titles = []
        
        for title in common_titles:
            if title in text_lower:
                found_titles.append(title)
        
        return found_titles
    
    def _calculate_match_score(self, resume_analysis: Dict, job: Dict) -> Dict:
        title_score = self._calculate_title_similarity(resume_analysis["job_titles"], job["title"])
        
        skill_details = self._calculate_skill_overlap(resume_analysis["skills"], job["description"])
        skill_score = skill_details['score']
        matched_skills = skill_details['matched_skills']
        
        # Store skill score for semantic boost calculation
        self._last_skill_score = skill_score
        
        semantic_score = self._calculate_semantic_similarity(
            resume_analysis["raw_text"],
            job["description"]
        )
        
        # Calculate domain expertise boost
        domain_boost = self._get_domain_expertise_boost(
            resume_analysis["raw_text"],
            job["description"]
        )
        
        # Optimized weights for technical roles: 40% skills, 35% semantic, 25% title
        # Skills are most important for technical alignment, semantic provides context
        base_score = (title_score * 0.25) + (skill_score * 0.40) + (semantic_score * 0.35)
        
        # Apply domain expertise boost
        final_score = base_score * (1 + domain_boost)
        
        # Calculate missed skills (skills in resume but not in job description)
        all_resume_skills = resume_analysis['skills']
        missed_skills = [skill for skill in all_resume_skills if skill not in matched_skills]
        
        # Debug: Print component scores for detailed analysis
        job_title = job.get('title', 'Unknown')
        
        if 'voxel' in job.get('company', '').lower() or 'senior frontend' in job_title.lower():
            print(f"\n=== DETAILED SCORE BREAKDOWN for {job_title} ===")
            print(f"Company: {job.get('company', 'Unknown')}")
            print(f"Resume titles found: {resume_analysis['job_titles']}")
            print(f"Resume skills found ({len(all_resume_skills)} total): {all_resume_skills}")
            print(f"Matched skills ({len(matched_skills)}): {matched_skills}")
            print(f"Missed skills ({len(missed_skills)}): {missed_skills}")
            print(f"Job description length: {len(job.get('description', ''))} chars")
            print(f"Job description preview: {job.get('description', '')[:150]}...")
            print(f"Title Score: {title_score:.2f} (weight: 25%)")
            print(f"Skill Score: {skill_score:.2f} (weight: 40%)")
            print(f"Semantic Score: {semantic_score:.2f} (weight: 35%)")
            print(f"Final Score: {final_score * 100:.2f}%")
            print("=" * 50 + "\n")
        
        return {
            'final_score': min(final_score * 100, 100),
            'title_score': title_score,
            'skill_score': skill_score,
            'semantic_score': semantic_score,
            'matched_skills': matched_skills,
            'missed_skills': missed_skills[:10]  # Limit to top 10 missed skills to avoid clutter
        }
    
    def _calculate_title_similarity(self, resume_titles: List[str], job_title: str) -> float:
        if not resume_titles:
            return 0.3
        
        # Normalize title: remove hyphens and split compound words
        def normalize_title(title):
            title = title.lower().replace('-', ' ')
            title = title.replace('frontend', 'front end')
            title = title.replace('backend', 'back end')
            title = title.replace('fullstack', 'full stack')
            return title
        
        job_title_normalized = normalize_title(job_title)
        
        for resume_title in resume_titles:
            resume_title_normalized = normalize_title(resume_title)
            
            if resume_title_normalized in job_title_normalized or job_title_normalized in resume_title_normalized:
                return 1.0
            
            resume_words = set(resume_title_normalized.split())
            job_words = set(job_title_normalized.split())
            
            common_words = resume_words.intersection(job_words)
            if len(common_words) >= 2:
                return 0.8
        
        return 0.4
    
    def _get_equivalent_skills(self) -> Dict[str, List[str]]:
        """Map equivalent or related technologies"""
        return {
            "kafka": ["rabbitmq", "kinesis", "pulsar", "event streaming"],
            "rabbitmq": ["kafka", "kinesis", "message queue"],
            "spark": ["flink", "beam", "distributed computing", "data pipeline"],
            "hadoop": ["spark", "distributed computing", "big data"],
            "airflow": ["dagster", "prefect", "orchestration"],
            "aws": ["gcp", "azure", "cloud"],
            "gcp": ["aws", "azure", "google cloud"],
            "azure": ["aws", "gcp", "cloud"],
            "kubernetes": ["k8s", "docker", "container orchestration"],
            "docker": ["kubernetes", "containerization"],
            "mlflow": ["sagemaker", "vertex ai", "ml lifecycle"],
            "sagemaker": ["mlflow", "vertex ai", "automl"],
            "vertex ai": ["sagemaker", "mlflow", "automl"],
            "snowflake": ["bigquery", "redshift", "data warehouse"],
            "bigquery": ["snowflake", "redshift", "data warehouse"],
            "redshift": ["snowflake", "bigquery", "data warehouse"],
            "pytorch": ["tensorflow", "deep learning"],
            "tensorflow": ["pytorch", "deep learning"],
            "transformers": ["huggingface", "bert", "gpt", "nlp"],
            "bert": ["transformers", "roberta", "distilbert", "nlp"],
            "nlp": ["natural language processing", "transformers", "text processing"],
            # Recommendation system related
            "recommendation": ["personalization", "ranking", "search", "retrieval"],
            "recommender systems": ["personalization", "ranking", "search", "retrieval"],
            "personalization": ["recommendation", "ranking", "user modeling"],
            "ranking": ["recommendation", "search", "retrieval", "personalization"],
            "search": ["ranking", "retrieval", "elasticsearch", "semantic similarity"],
            "retrieval": ["search", "ranking", "recommendation"],
        }
    
    def _get_domain_expertise_boost(self, resume_text: str, job_description: str) -> float:
        """Calculate boost for domain expertise and transferable skills"""
        resume_lower = resume_text.lower()
        job_lower = job_description.lower()
        boost = 0.0
        
        # NLP/Search expertise is valuable for recommendation systems
        if any(term in job_lower for term in ['recommendation', 'recommender', 'personalization', 'ranking']):
            nlp_indicators = ['nlp', 'natural language', 'transformers', 'bert', 'semantic similarity', 'search engine']
            nlp_count = sum(1 for term in nlp_indicators if term in resume_lower)
            if nlp_count >= 3:
                boost += 0.10  # 10% boost for strong NLP background
        
        # Real-time/streaming experience is valuable for production ML
        if any(term in job_lower for term in ['real-time', 'streaming', 'production', 'scale']):
            streaming_indicators = ['rabbitmq', 'kafka', 'websocket', 'real-time', 'streaming', 'production']
            streaming_count = sum(1 for term in streaming_indicators if term in resume_lower)
            if streaming_count >= 2:
                boost += 0.08  # 8% boost for streaming/production experience
        
        # Deep learning expertise for ML roles
        if any(term in job_lower for term in ['deep learning', 'neural network', 'machine learning']):
            dl_indicators = ['pytorch', 'tensorflow', 'deep learning', 'neural', 'gpu', 'training', 'fine-tuning']
            dl_count = sum(1 for term in dl_indicators if term in resume_lower)
            if dl_count >= 4:
                boost += 0.10  # 10% boost for deep DL experience
        
        # Senior/leadership experience
        if any(term in job_lower for term in ['senior', 'lead', 'staff', 'principal']):
            leadership_indicators = ['founder', 'head of', 'lead', 'senior', 'managed', 'architected']
            leadership_count = sum(1 for term in leadership_indicators if term in resume_lower)
            if leadership_count >= 2:
                boost += 0.07  # 7% boost for leadership
        
        return min(boost, 0.25)  # Cap at 25% total boost
    
    def _calculate_skill_overlap(self, resume_skills: List[str], job_description: str) -> Dict:
        if not resume_skills:
            return {'score': 0.3, 'matched_skills': []}
        
        job_desc_lower = job_description.lower()
        equivalent_skills = self._get_equivalent_skills()
        
        matched_skill_list = []
        
        for skill in resume_skills:
            # Direct match
            if skill in job_desc_lower:
                matched_skill_list.append(skill)
            # Check for equivalent skills
            elif skill in equivalent_skills:
                for equiv in equivalent_skills[skill]:
                    if equiv in job_desc_lower:
                        matched_skill_list.append(skill)
                        break
        
        matching_skills = len(matched_skill_list)
        
        # Improved scoring with more granular levels
        if matching_skills == 0:
            score = 0.2
        elif matching_skills <= 2:
            score = 0.4
        elif matching_skills <= 4:
            score = 0.55
        elif matching_skills <= 6:
            score = 0.7
        elif matching_skills <= 9:
            score = 0.85
        else:
            score = 1.0
        
        return {
            'score': score,
            'matched_skills': matched_skill_list
        }
    
    def _calculate_semantic_similarity(self, resume_text: str, job_description: str) -> float:
        """
        Enhanced semantic similarity using chunked analysis and key section matching.
        This captures meaning beyond keywords and understands context better.
        """
        try:
            model = self._get_model()
            
            # Extract key sections from job description
            job_sections = self._extract_key_sections(job_description)
            resume_sections = self._extract_key_sections(resume_text)
            
            # Calculate overall similarity
            embeddings = model.encode([resume_text, job_description])
            overall_similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            
            # Calculate section-specific similarities for better matching
            section_similarities = []
            
            # Compare responsibilities/experience sections
            if job_sections['responsibilities'] and resume_sections['experience']:
                resp_emb = model.encode([resume_sections['experience'], job_sections['responsibilities']])
                resp_sim = cosine_similarity([resp_emb[0]], [resp_emb[1]])[0][0]
                section_similarities.append(resp_sim)
            
            # Compare requirements/skills sections
            if job_sections['requirements'] and resume_sections['skills']:
                req_emb = model.encode([resume_sections['skills'], job_sections['requirements']])
                req_sim = cosine_similarity([req_emb[0]], [req_emb[1]])[0][0]
                section_similarities.append(req_sim)
            
            # Weighted combination: 60% overall, 40% section-specific
            if section_similarities:
                section_avg = sum(section_similarities) / len(section_similarities)
                final_similarity = (overall_similarity * 0.6) + (section_avg * 0.4)
            else:
                final_similarity = overall_similarity
            
            # Apply boost for strong technical alignment
            # If many skills match, boost semantic score
            boost_factor = 1.0
            if hasattr(self, '_last_skill_score') and self._last_skill_score > 0.7:
                boost_factor = 1.15
            
            return min(float(final_similarity * boost_factor), 1.0)
            
        except Exception as e:
            print(f"Error calculating semantic similarity with Sentence Transformers: {e}")
            return 0.5
    
    def _extract_key_sections(self, text: str) -> Dict[str, str]:
        """Extract key sections from text for better semantic matching"""
        text_lower = text.lower()
        sections = {
            'responsibilities': '',
            'requirements': '',
            'experience': '',
            'skills': ''
        }
        
        # Split text into lines
        lines = text.split('\n')
        current_section = None
        section_content = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Detect section headers
            if any(keyword in line_lower for keyword in ['responsibilities', 'what you\'ll do', 'role', 'duties']):
                if current_section and section_content:
                    sections[current_section] = ' '.join(section_content)
                current_section = 'responsibilities'
                section_content = []
            elif any(keyword in line_lower for keyword in ['requirements', 'qualifications', 'required', 'must have']):
                if current_section and section_content:
                    sections[current_section] = ' '.join(section_content)
                current_section = 'requirements'
                section_content = []
            elif any(keyword in line_lower for keyword in ['experience', 'work history', 'employment']):
                if current_section and section_content:
                    sections[current_section] = ' '.join(section_content)
                current_section = 'experience'
                section_content = []
            elif any(keyword in line_lower for keyword in ['skills', 'technical skills', 'technologies']):
                if current_section and section_content:
                    sections[current_section] = ' '.join(section_content)
                current_section = 'skills'
                section_content = []
            elif current_section and line.strip():
                section_content.append(line.strip())
        
        # Add last section
        if current_section and section_content:
            sections[current_section] = ' '.join(section_content)
        
        return sections
    
    def _get_match_level(self, score: float) -> str:
        if score >= 80:
            return "Strong Match"
        elif score >= 60:
            return "Moderate Match"
        else:
            return "Weak Match"
