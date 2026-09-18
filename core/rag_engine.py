"""
EcoSort AI - IBM Granite Powered RAG (Retrieval-Augmented Generation) Engine
Retrieves relevant waste management guidelines, statutory rules (SWM 2016),
and circular economy best practices to answer user queries with verifiable citations.
"""

import json
import re
import math
from pathlib import Path
from typing import List, Dict, Any, Tuple

class GraniteRAGEngine:
    def __init__(self, kb_path: str = None):
        if kb_path is None:
            base_dir = Path(__file__).resolve().parent
            kb_path = str(base_dir / "waste_knowledge_base.json")
        
        self.kb_path = kb_path
        self.documents = []
        self.load_knowledge_base()

    def load_knowledge_base(self):
        try:
            with open(self.kb_path, "r", encoding="utf-8") as f:
                self.documents = json.load(f)
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            self.documents = []

    def _tokenize(self, text: str) -> List[str]:
        words = re.findall(r'\b\w+\b', text.lower())
        stopwords = {"the", "and", "is", "in", "to", "of", "it", "for", "on", "with", "as", "by", "at", "an", "be", "this", "which", "or", "from"}
        return [w for w in words if w not in stopwords and len(w) > 2]

    def retrieve_context(self, query: str, top_k: int = 2) -> List[Tuple[Dict[str, Any], float]]:
        query_tokens = set(self._tokenize(query))
        if not query_tokens:
            return [(doc, 0.5) for doc in self.documents[:top_k]]

        scored_docs = []
        for doc in self.documents:
            doc_text = f"{doc.get('title', '')} {doc.get('category', '')} {doc.get('content', '')} {' '.join(doc.get('keywords', []))}"
            doc_tokens = self._tokenize(doc_text)
            
            # Simple TF-IDF inspired overlap
            match_count = sum(1 for q in query_tokens if q in doc_tokens)
            keyword_match = sum(2 for k in doc.get('keywords', []) if any(q in k.lower() for q in query_tokens))
            
            score = (match_count * 1.5 + keyword_match * 2.0) / (len(query_tokens) + 1)
            scored_docs.append((doc, score))

        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return scored_docs[:top_k]

    def query_granite(self, query: str) -> Dict[str, Any]:
        """
        Simulates the IBM Granite 3.0 / watsonx.ai inference pipeline using RAG retrieval.
        Structures the prompt in IBM Granite special instruction tokens:
        <|start_of_role|>system<|end_of_role|> ... <|start_of_role|>user<|end_of_role|> ... <|start_of_role|>assistant<|end_of_role|>
        """
        retrieved_results = self.retrieve_context(query, top_k=2)
        top_docs = [doc for doc, score in retrieved_results]

        context_str = "\n\n".join([
            f"[Document: {d['title']}] (Source: {d['source']})\n{d['content']}"
            for d in top_docs
        ])

        # Prompt formatting in IBM Granite 3.0 standard template
        granite_prompt = (
            "<|start_of_role|>system<|end_of_role|>\n"
            "You are EcoSort-Granite, an AI Sustainability Specialist built on IBM Granite foundational models. "
            "Your role is to guide college campuses and municipal citizens on responsible waste segregation, circular disposal, "
            "and compliance with Indian Solid Waste Management (SWM) 2016 rules.\n\n"
            f"VERIFIED KNOWLEDGE BASE CONTEXT:\n{context_str}\n\n"
            "<|start_of_role|>user<|end_of_role|>\n"
            f"{query}\n"
            "<|start_of_role|>assistant<|end_of_role|>"
        )

        # Synthesize expert response grounded in context
        response_text, suggestions = self._generate_response(query, top_docs)

        citations = [
            {
                "id": d["id"],
                "title": d["title"],
                "source": d["source"],
                "category": d["category"]
            }
            for d in top_docs
        ]

        return {
            "query": query,
            "model": "IBM Granite 3.0-8B-Instruct (Simulated/Ready for watsonx.ai)",
            "response": response_text,
            "citations": citations,
            "suggested_followups": suggestions,
            "prompt_template_preview": granite_prompt
        }

    def _generate_response(self, query: str, docs: List[Dict[str, Any]]) -> Tuple[str, List[str]]:
        q_lower = query.lower()

        if any(w in q_lower for w in ["pizza", "grease", "oil", "food stain", "carton"]):
            answer = (
                "**Decision: Do NOT recycle the greasy portion in the Blue Paper Bin.**\n\n"
                "1. **The Science Behind It:** Paper recycling relies on mixing fiber with water to create a slurry. Oil and grease from cheese or sauces do not dissolve in water; they bond to cellulose fibers and create oil slicks that ruin entire metric tons of recycled paper batches.\n"
                "2. **Actionable SWM Protocol:**\n"
                "   - **Step A (Segregate Lid):** Tear off the clean cardboard lid (if unsoiled) and drop it into the **Blue Bin** for recycling.\n"
                "   - **Step B (Compost Base):** The greasy bottom portion should be shredded into small pieces and deposited into the **Green Bin (Compost)** or campus vermicompost pit.\n"
                "   - **Step C (Discard Inserts):** Remove any plastic dip cups or plastic center tripods.\n\n"
                "*Statutory Alignment: SWM Rules 2016 & Circular Economy Municipal Standards.*"
            )
            suggestions = [
                "Can composted greasy cardboard go into campus vermicompost pits?",
                "What other packaging contaminates paper recycling streams?",
                "How can food delivery vendors switch to biodegradable lining?"
            ]

        elif any(w in q_lower for w in ["battery", "phone", "laptop", "e-waste", "charger", "cable", "lithium"]):
            answer = (
                "**Decision: Critical Hazard — NEVER discard in household Blue or Green Bins.**\n\n"
                "1. **Fire & Chemical Risk:** Spent lithium-ion and dry cell batteries undergo thermal runaway when punctured by hydraulic compactors in municipal garbage trucks, triggering severe truck fires. Additionally, toxic heavy metals (lead, mercury, cadmium) leach into groundwater if dumped in unlined landfills.\n"
                "2. **Campus Disposal Protocol:**\n"
                "   - Tape the conductive terminals with clear cellophane tape to eliminate contact short-circuits.\n"
                "   - Deposit at the **Yellow Campus E-Waste Box** located in the Engineering Block Foyer or Student Activity Center.\n"
                "   - All items are channeled to CPCB-certified PRO (Producer Responsibility Organisation) recyclers for rare element hydrometallurgical recovery (Lithium, Cobalt, Nickel).\n\n"
                "*Statutory Alignment: E-Waste (Management) Rules 2022.*"
            )
            suggestions = [
                "Where is the nearest campus e-waste drop-off point?",
                "What valuable metals are extracted during battery recycling?",
                "How does EPR hold electronics manufacturers accountable?"
            ]

        elif any(w in q_lower for w in ["plastic", "pet", "bottle", "single-use", "sup", "chips", "wrapper"]):
            answer = (
                "**Decision: Segregate into High-Value Rigid Recyclables vs Multilayer Plastics.**\n\n"
                "1. **Plastic Bottles (SPI Code 1 - PET):** Empty all liquid, rinse lightly to avoid microbial odor, crush the bottle to conserve 70% storage volume, and place in the **Blue Bin**. The bottle caps (HDPE Code 2) can remain screwed on or be collected separately.\n"
                "2. **Multilayer Wrappers (Chips / Biscuits):** Multi-layered plastics (metalized BOPP films) cannot be recycled mechanically into clear plastic; they are diverted to cement kilns for co-processing (refuse-derived fuel) or road bitumen mixing under Extended Producer Responsibility (EPR).\n"
                "3. **Banned Single-Use Plastics:** Plastic straws, plastic cutlery, and thin polybags (<120 microns) are banned under Plastic Waste Management Rules.\n\n"
                "*Statutory Alignment: Plastic Waste Management Amendment Rules & CPCB Directives.*"
            )
            suggestions = [
                "What do the SPI resin numbers 1 through 7 signify?",
                "How can campuses incentivize plastic bottle deposits?",
                "What are the environmental alternatives to multi-layer snack packaging?"
            ]

        elif any(w in q_lower for w in ["sanitation", "worker", "picker", "glass", "sharp", "blade", "safety"]):
            answer = (
                "**Decision: Safe Packaging Mandatory to Protect Sanitation Workers.**\n\n"
                "1. **Occupational Health Threat:** Over 4 million informal waste pickers (Safai Karamcharis) in India manually handle municipal waste. Unwrapped broken glass, razor blades, and exposed needles cause severe lacerations, tetanus, and hepatitis infections.\n"
                "2. **Responsible AI Mandatory Step:**\n"
                "   - Wrap broken glassware in at least 4 layers of newspaper or sturdy cardboard.\n"
                "   - Seal with packaging tape and mark clearly with a prominent **Red Cross / Hazard Symbol**.\n"
                "   - Deposit in the **Red/Black Domestic Hazardous Bin** or hand directly to the collection worker with an explicit verbal warning.\n\n"
                "*Ethical Pillar: Dignity and Physical Safety of Frontline Sanitation Champions.*"
            )
            suggestions = [
                "How does source segregation improve the livelihood of informal waste pickers?",
                "What are the domestic hazardous waste guidelines under SWM 2016?",
                "Can broken glass cullet be reused in road construction?"
            ]

        else:
            # Context-based general synthesis
            doc_titles = ", ".join([f"'{d['title']}'" for d in docs])
            answer = (
                f"Based on {doc_titles}, waste segregation in Indian campuses and municipalities is governed by a **Three-Stream Protocol**:\n\n"
                "- **Green Bin (Wet / Biodegradable):** Kitchen leftovers, fruit and vegetable peels, canteen organic scraps, horticulture leaves. Converted into compost or biogas.\n"
                "- **Blue Bin (Dry / Recyclable):** Clean plastic containers, newspapers, corrugated cardboard, rinsed milk pouches, glass bottles, and beverage aluminum cans.\n"
                "- **Red/Black Bin (Domestic Hazardous):** Broken glass (wrapped in paper), diapers, mosquito coils, pesticide/detergent bottles, expired medications.\n"
                "- **Yellow E-Box (Electronics):** All batteries, chargers, ear buds, cables, and electronic components.\n\n"
                "Always ensure containers are emptied and rinsed to prevent pest infestation and odor in storage bays."
            )
            suggestions = [
                "How do I set up a 3-stream segregation station in my hostel room?",
                "What is the difference between biodegradable and oxo-degradable plastics?",
                "How can AI cameras audit campus bin contamination in real time?"
            ]

        return answer, suggestions
