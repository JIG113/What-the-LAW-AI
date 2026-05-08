from sqlmodel import Session, select

from app.models.entities import RuleProfile


def get_percent_upper_bound(session: Session, profile_name: str) -> float:
    profile = session.exec(select(RuleProfile).where(RuleProfile.name == profile_name, RuleProfile.enabled == True)).first()  # noqa: E712
    if not profile:
        return 1000.0
    return float(profile.percent_upper_bound)
