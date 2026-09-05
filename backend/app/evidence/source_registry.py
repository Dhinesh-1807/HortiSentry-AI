from typing import Dict, List, Optional
from app.evidence.models import TrustedSource

class TrustedSourceRegistry:
    """Registry of authoritative agricultural research institutions & extension sources."""

    _SOURCES: Dict[str, TrustedSource] = {
        "icar": TrustedSource(
            source_id="icar",
            source_name="ICAR — Indian Council of Agricultural Research",
            domain="icar.gov.in",
            authority_tier=1,
            authority_description="Apex autonomous organization for agricultural research and education in India.",
            enabled=True,
            weight=1.0
        ),
        "tnau": TrustedSource(
            source_id="tnau",
            source_name="TNAU Agritech Portal",
            domain="agritech.tnau.ac.in",
            authority_tier=1,
            authority_description="Tamil Nadu Agricultural University Agritech Portal for crop protection & pest management.",
            enabled=True,
            weight=1.0
        ),
        "fao": TrustedSource(
            source_id="fao",
            source_name="FAO — Food and Agriculture Organization",
            domain="fao.org",
            authority_tier=1,
            authority_description="United Nations agency leading international efforts to defeat hunger and support crop safety.",
            enabled=True,
            weight=0.95
        ),
        "eppo": TrustedSource(
            source_id="eppo",
            source_name="EPPO Global Database",
            domain="gd.eppo.int",
            authority_tier=1,
            authority_description="European and Mediterranean Plant Protection Organization diagnostic database.",
            enabled=True,
            weight=0.95
        ),
        "ppqs": TrustedSource(
            source_id="ppqs",
            source_name="Govt of India Plant Protection (PPQS)",
            domain="ppqs.gov.in",
            authority_tier=1,
            authority_description="Directorate of Plant Protection, Quarantine & Storage, Ministry of Agriculture, India.",
            enabled=True,
            weight=1.0
        ),
        "cabi": TrustedSource(
            source_id="cabi",
            source_name="CABI Plantwise Knowledge Bank",
            domain="plantwiseplusknowledgebank.org",
            authority_tier=2,
            authority_description="Global database providing actionable plant health guidance for farmers.",
            enabled=True,
            weight=0.85
        ),
        "iihr": TrustedSource(
            source_id="iihr",
            source_name="ICAR-IIHR — Indian Institute of Horticultural Research",
            domain="iihr.res.in",
            authority_tier=2,
            authority_description="Premier institute conducting research on horticultural crops.",
            enabled=True,
            weight=0.85
        ),
        "cpri": TrustedSource(
            source_id="cpri",
            source_name="ICAR-CPRI — Central Potato Research Institute",
            domain="cpri.icar.gov.in",
            authority_tier=2,
            authority_description="National institute dedicated to potato crop disease research.",
            enabled=True,
            weight=0.85
        ),
        "nrcb": TrustedSource(
            source_id="nrcb",
            source_name="ICAR-NRCB — National Research Centre for Banana",
            domain="nrcb.res.in",
            authority_tier=2,
            authority_description="Apex research centre for banana crop protection.",
            enabled=True,
            weight=0.85
        ),
        "agri_ext": TrustedSource(
            source_id="agri_ext",
            source_name="State Agricultural Extension Service",
            domain="extension.org",
            authority_tier=3,
            authority_description="Peer-reviewed university extension guidance for crop disease management.",
            enabled=True,
            weight=0.70
        )
    }

    @classmethod
    def get_all_sources(cls) -> List[TrustedSource]:
        return [s for s in cls._SOURCES.values() if s.enabled]

    @classmethod
    def get_source_by_id(cls, source_id: str) -> Optional[TrustedSource]:
        return cls._SOURCES.get(source_id.lower())

    @classmethod
    def get_source_by_domain(cls, domain: str) -> Optional[TrustedSource]:
        for src in cls._SOURCES.values():
            if src.enabled and src.domain.lower() in domain.lower():
                return src
        return None

    @classmethod
    def get_tier_weight(cls, authority_tier: int) -> float:
        if authority_tier == 1:
            return 1.0
        elif authority_tier == 2:
            return 0.80
        return 0.60
