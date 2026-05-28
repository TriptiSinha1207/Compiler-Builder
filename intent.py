from __future__ import annotations
import re
from typing import List, Optional
from pydantic import BaseModel, Field

FEATURE_KEYWORDS = {
    "login": ["login", "signin", "sign in", "log in"],
    "contacts": ["contacts", "clients", "customers"],
    "dashboard": ["dashboard"],
    "payments": ["payment", "payments", "stripe", "charge", "billing"],
    "analytics": ["analytics", "reports", "metrics", "insights"],
    "role_based_access": ["role-based access", "roles", "permissions", "admin", "user access"],
    "premium_plans": ["premium", "subscription", "plan", "paid", "membership"],
    "crm": ["crm", "customer relationship management"],
    "admin": ["admin", "administrator"],
}

ROLE_KEYWORDS = {
    "admin": ["admin", "administrator"],
    "user": ["user", "member", "customer", "client"],
    "manager": ["manager", "owner", "team lead"],
}

PAGE_KEYWORDS = ["dashboard", "contacts", "login", "register", "pricing", "analytics", "settings", "profile"]
ENTITY_KEYWORDS = {
    "user": ["user", "admin", "member", "account"],
    "contact": ["contact", "client", "customer"],
    "plan": ["plan", "subscription", "premium"],
    "payment": ["payment", "invoice", "billing"],
    "analytics": ["analytics", "report", "metric"],
}

class Intent(BaseModel):
    prompt: str
    app_type: str
    features: List[str]
    pages: List[str]
    entities: List[str]
    roles: List[str]
    plans: List[str]
    analytics: bool = False
    payments: bool = False
    auth_required: bool = False
    assumptions: List[str] = []
    needs_clarification: bool = False
    clarification_questions: Optional[List[str]] = None

class IntentExtractor:
    @classmethod
    def parse(cls, prompt: str) -> Intent:
        text = prompt.strip()
        normalized = text.lower()
        features = cls._extract_features(normalized)
        pages = cls._extract_pages(normalized)
        roles = cls._extract_roles(normalized)
        plans = cls._extract_plans(normalized)
        entities = cls._extract_entities(normalized, features)
        analytics = "analytics" in normalized or "report" in normalized or "metric" in normalized
        payments = "payment" in normalized or "premium" in normalized or "plan" in normalized or "billing" in normalized
        auth_required = bool(roles or any(feature in ["login", "role_based_access"] for feature in features))
        app_type = cls._extract_app_type(normalized)
        assumptions = []
        clarification_questions = []
        needs_clarification = False

        if not features:
            features = ["dashboard"]
            assumptions.append("No explicit features found; defaulting to dashboard-centric CRM architecture.")
        if not pages:
            pages = ["dashboard"]
            assumptions.append("No explicit pages found; adding dashboard page by default.")
        if auth_required and "login" not in features:
            features.append("login")
            assumptions.append("Role access detected; adding login flow automatically.")
        if payments and "premium_plans" not in features:
            features.append("premium_plans")
            assumptions.append("Premium or billing keywords found; adding premium plan support.")
        if not roles and auth_required:
            roles = ["admin", "user"]
            assumptions.append("No explicit roles provided; using default roles admin and user.")
        if "conflicting" in normalized or "contradict" in normalized:
            needs_clarification = True
            clarification_questions.append("Please clarify conflicting requirements or choose a consistent access model.")

        return Intent(
            prompt=text,
            app_type=app_type,
            features=sorted(set(features)),
            pages=sorted(set(pages)),
            entities=sorted(set(entities)),
            roles=sorted(set(roles)),
            plans=sorted(set(plans)),
            analytics=analytics,
            payments=payments,
            auth_required=auth_required,
            assumptions=assumptions,
            needs_clarification=needs_clarification,
            clarification_questions=clarification_questions or None,
        )

    @classmethod
    def _extract_features(cls, text: str) -> List[str]:
        found = []
        for feature, keywords in FEATURE_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                found.append(feature)
        return found

    @classmethod
    def _extract_pages(cls, text: str) -> List[str]:
        page_names = []
        for keyword in PAGE_KEYWORDS:
            if keyword in text:
                page_names.append(keyword)
        if "login" in text and "register" not in page_names:
            page_names.append("login")
        return page_names

    @classmethod
    def _extract_roles(cls, text: str) -> List[str]:
        roles = []
        for role, keywords in ROLE_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                roles.append(role)
        return roles

    @classmethod
    def _extract_plans(cls, text: str) -> List[str]:
        plans = []
        if "premium" in text:
            plans.append("premium")
        if "free" in text:
            plans.append("free")
        if "pro" in text:
            plans.append("pro")
        return plans

    @classmethod
    def _extract_entities(cls, text: str, features: List[str]) -> List[str]:
        entities = set()
        if "crm" in text or "contacts" in text:
            entities.add("contact")
        if "payment" in text or "billing" in text or "premium" in text or "plan" in text:
            entities.add("plan")
            entities.add("payment")
        if "login" in text or "user" in text or "admin" in text:
            entities.add("user")
        if "analytics" in text or "dashboard" in text or "report" in text:
            entities.add("analytics")
        if not entities and features:
            for feature in features:
                if feature == "contacts":
                    entities.add("contact")
                elif feature == "premium_plans":
                    entities.add("plan")
                elif feature == "payments":
                    entities.add("payment")
        return sorted(entities)

    @classmethod
    def _extract_app_type(cls, text: str) -> str:
        if "crm" in text:
            return "CRM"
        if "marketplace" in text:
            return "Marketplace"
        if "project" in text:
            return "ProjectManagement"
        return "WebApp"
