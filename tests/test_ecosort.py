"""
Automated Test Suite for EcoSort AI
Validates classifier, IBM Granite RAG engine, impact calculator, and responsible AI governance.
"""

import unittest
from core.classifier import WasteClassifier
from core.rag_engine import GraniteRAGEngine
from core.impact_calculator import ImpactCalculator
from core.responsible_ai import ResponsibleAIGovernance

class TestEcoSortAI(unittest.TestCase):
    def setUp(self):
        self.classifier = WasteClassifier()
        self.rag_engine = GraniteRAGEngine()
        self.impact_calc = ImpactCalculator()
        self.governance = ResponsibleAIGovernance()

    def test_classifier_pet_bottle(self):
        result = self.classifier.classify_sample("pet_bottle")
        self.assertEqual(result["category_key"], "DRY_PLASTIC")
        self.assertEqual(result["bin"]["name"], "Blue Bin (Dry Recyclables)")
        self.assertFalse(result["is_contaminated"])
        self.assertGreaterEqual(result["confidence"], 0.90)

    def test_classifier_contamination_detection(self):
        result = self.classifier.classify_sample("greasy_pizza_box")
        self.assertEqual(result["category_key"], "CONTAMINATED_PAPER")
        self.assertTrue(result["is_contaminated"])
        self.assertIn("grease", result["contamination_details"].lower())

    def test_classifier_hazardous_battery(self):
        result = self.classifier.classify_sample("lithium_battery")
        self.assertEqual(result["category_key"], "E_WASTE")
        self.assertIn("Yellow", result["bin"]["name"])

    def test_rag_engine_retrieval(self):
        retrieved = self.rag_engine.retrieve_context("Can pizza boxes with oil grease be recycled?", top_k=2)
        self.assertGreater(len(retrieved), 0)
        top_doc, score = retrieved[0]
        self.assertIn("doc_paper_cardboard_contamination", top_doc["id"])

    def test_granite_rag_query(self):
        res = self.rag_engine.query_granite("Where do I dispose spent lithium batteries on campus?")
        self.assertIn("response", res)
        self.assertIn("Yellow", res["response"])
        self.assertGreater(len(res["citations"]), 0)
        self.assertIn("<|start_of_role|>", res["prompt_template_preview"])

    def test_impact_calculator(self):
        impact = self.impact_calc.calculate_item_impact("DRY_PLASTIC", 22.0)
        self.assertGreater(impact["co2_saved_kg"], 0)
        self.assertGreater(impact["water_saved_liters"], 0)
        self.assertGreater(impact["energy_saved_kwh"], 0)

        summary = self.impact_calc.get_session_summary()
        self.assertEqual(summary["session"]["items_sorted"], 1)

    def test_responsible_ai_governance(self):
        sample = self.classifier.classify_sample("broken_glass")
        audit = self.governance.audit_classification(sample)
        self.assertIn("pillars", audit)
        self.assertEqual(audit["pillars"]["fairness"]["status"], "VERIFIED_UNBIASED")
        self.assertIsNotNone(audit["pillars"]["ethics"]["worker_safety_alert"])
        self.assertIn("No human facial features", audit["pillars"]["privacy"]["facial_recognition_check"])

if __name__ == "__main__":
    unittest.main()
