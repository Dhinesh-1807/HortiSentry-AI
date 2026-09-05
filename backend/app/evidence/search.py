import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Curated Agricultural Knowledge Base mapping crop & disease to authoritative ICAR / TNAU / FAO evidence items
LOCAL_AGRICULTURAL_KNOWLEDGE_BASE: List[Dict[str, Any]] = [
    {
        "crop": "tomato",
        "disease": "Early Blight",
        "scientific_name": "Alternaria solani",
        "source_name": "TNAU Agritech Portal",
        "domain": "agritech.tnau.ac.in",
        "url": "https://agritech.tnau.ac.in/crop_protection/crop_prot_crop_diseases_veg_tomato_1.html",
        "authority_tier": 1,
        "title": "Tomato Early Blight Management — TNAU Agritech",
        "symptoms": "Concentric ring brown spots on leaves surrounded by yellow chlorotic halo. Older leaves affected first.",
        "management": "Remove and destroy infected lower leaves. Maintain crop spacing for airflow. Avoid overhead irrigation.",
        "prevention": "Rotate crops with non-solanaceous crops for 2-3 years. Use disease-free seeds and resistant varieties."
    },
    {
        "crop": "tomato",
        "disease": "Late Blight",
        "scientific_name": "Phytophthora infestans",
        "source_name": "ICAR — Indian Council of Agricultural Research",
        "domain": "icar.gov.in",
        "url": "https://icar.gov.in/content/tomato-late-blight-management-guidelines",
        "authority_tier": 1,
        "title": "ICAR Guidelines for Tomato Late Blight Outbreak Control",
        "symptoms": "Water-soaked dark green to black lesions rapidly spreading on leaves and stems during cool, humid weather.",
        "management": "Promptly remove heavily blighted plants. Ensure good field drainage and reduce humidity.",
        "prevention": "Plant certified disease-free seeds. Monitor fields closely during cold wet spells."
    },
    {
        "crop": "tomato",
        "disease": "Leaf Spot",
        "scientific_name": "Septoria lycopersici",
        "source_name": "FAO — Food and Agriculture Organization",
        "domain": "fao.org",
        "url": "https://fao.org/plant-protection/septoria-leaf-spot-tomato",
        "authority_tier": 1,
        "title": "FAO Integrated Pest Management: Septoria Leaf Spot",
        "symptoms": "Numerous small circular spots with dark brown margins and gray centers containing tiny black pycnidia.",
        "management": "Clear leaf debris from field after harvest. Mulch soil surface to prevent spore splash from rain.",
        "prevention": "Prune lower foliage touching the soil. Practice 3-year crop rotation."
    },
    {
        "crop": "chilli",
        "disease": "Chilli Leaf Curl Virus",
        "scientific_name": "Begomovirus",
        "source_name": "ICAR-IIHR — Indian Institute of Horticultural Research",
        "domain": "iihr.res.in",
        "url": "https://iihr.res.in/advisory-chilli-leaf-curl-management",
        "authority_tier": 1,
        "title": "ICAR-IIHR Advisory on Chilli Leaf Curl Virus",
        "symptoms": "Upward leaf curling, puckering, reduced leaf size, stunting, and bushy yellow appearance caused by whitefly vector.",
        "management": "Remove virus-infected plants immediately. Set up yellow sticky traps to monitor and trap whiteflies.",
        "prevention": "Use vector-proof net nurseries. Intercrop with barrier crops like maize or sorghum."
    },
    {
        "crop": "chilli",
        "disease": "Anthracnose Fruit Rot",
        "scientific_name": "Colletotrichum capsici",
        "source_name": "TNAU Agritech Portal",
        "domain": "agritech.tnau.ac.in",
        "url": "https://agritech.tnau.ac.in/crop_protection/chilli_anthracnose.html",
        "authority_tier": 1,
        "title": "TNAU Advisory: Chilli Dieback and Anthracnose Fruit Rot",
        "symptoms": "Circular sunken lesions on green or ripe fruits with concentric rings of black acervuli. Twig dieback.",
        "management": "Collect and burn affected fruits and dried twigs. Avoid overhead sprinkling.",
        "prevention": "Seed treatment with Trichoderma viride. Maintain optimum field drainage."
    },
    {
        "crop": "brinjal",
        "disease": "Little Leaf Disease",
        "scientific_name": "Candidatus Phytoplasma",
        "source_name": "TNAU Agritech Portal",
        "domain": "agritech.tnau.ac.in",
        "url": "https://agritech.tnau.ac.in/crop_protection/brinjal_little_leaf.html",
        "authority_tier": 1,
        "title": "TNAU Guide: Brinjal Little Leaf Phytoplasma",
        "symptoms": "Extremely small narrow leaves, short internodes giving a bushy broom-like appearance. Plants become sterile.",
        "management": "Uproot and destroy phytoplasma-affected bushy plants. Control leafhopper vector with neem-based sprays.",
        "prevention": "Eradicate weed hosts around field margins before planting."
    },
    {
        "crop": "potato",
        "disease": "Potato Late Blight",
        "scientific_name": "Phytophthora infestans",
        "source_name": "ICAR — Central Potato Research Institute (CPRI)",
        "domain": "icar.gov.in",
        "url": "https://icar.gov.in/cpri-potato-late-blight-advisory",
        "authority_tier": 1,
        "title": "ICAR-CPRI Late Blight Management Advisory",
        "symptoms": "Water-soaked lesions on leaf tips turning purplish-black with white cottony growth under moist conditions.",
        "management": "Destroy infected haulms 10-15 days before harvesting tubers. Ensure proper earthing up of tubers.",
        "prevention": "Use resistant potato cultivars (e.g., Kufri Jyoti). Store seed tubers in cold storage."
    },
    {
        "crop": "mango",
        "disease": "Anthracnose",
        "scientific_name": "Colletotrichum gloeosporioides",
        "source_name": "ICAR-CISH — Central Institute for Subtropical Horticulture",
        "domain": "cish.res.in",
        "url": "https://cish.res.in/mango-anthracnose-management",
        "authority_tier": 1,
        "title": "ICAR-CISH Advisory: Mango Anthracnose Control",
        "symptoms": "Dark brown oval spots on leaves, blossom blight, and tear-stain black lesions on developing mango fruits.",
        "management": "Prune dead twigs after harvest. Spray tree canopy during flush and flowering stages with recommended bio-agents.",
        "prevention": "Prune inner branches to open tree canopy for sunlight penetration."
    },
    {
        "crop": "banana",
        "disease": "Sigatoka Leaf Spot",
        "scientific_name": "Mycosphaerella fijiensis",
        "source_name": "ICAR-NRCB — National Research Centre for Banana",
        "domain": "nrcb.res.in",
        "url": "https://nrcb.res.in/sigatoka-leaf-spot-advisory",
        "authority_tier": 1,
        "title": "ICAR-NRCB Advisory: Banana Sigatoka Management",
        "symptoms": "Yellowish-green streaks parallel to leaf veins turning into dark brown necrotic spots with gray centers.",
        "management": "Deleaf severely affected leaves and destroy them. Maintain field sanitation and weed control.",
        "prevention": "Provide adequate field drainage and avoid waterlogging. Ensure optimal plant spacing."
    }
]

class AgriculturalSearchEngine:
    """Structured evidence search engine operating over authoritative agricultural sources."""

    @classmethod
    def search_evidence(
        cls,
        crop: str,
        disease_candidate: str,
        symptoms: List[str]
    ) -> List[Dict[str, Any]]:
        crop_k = crop.lower()
        disease_k = disease_candidate.lower()
        
        matches = []
        for item in LOCAL_AGRICULTURAL_KNOWLEDGE_BASE:
            item_crop = item["crop"].lower()
            item_disease = item["disease"].lower()

            if item_crop == crop_k or crop_k in item_crop:
                relevance = 0.5
                if disease_k in item_disease or item_disease in disease_k:
                    relevance += 0.4
                for sym in symptoms:
                    if sym.lower() in item["symptoms"].lower():
                        relevance += 0.1
                
                match_item = dict(item)
                match_item["relevance"] = min(1.0, relevance)
                matches.append(match_item)

        # Sort by relevance
        matches.sort(key=lambda x: x["relevance"], reverse=True)
        return matches
