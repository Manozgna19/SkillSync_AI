
import sys
import uuid
import logging

sys.path.insert(0, r"C:\Users\CVR\Desktop\personalized-learning\database\seed")  # data files live outside the app/ package

from skills_data import SKILLS, PREREQUISITES  # noqa: E402
from resources_data import RESOURCES  # noqa: E402
from assessments_data import ASSESSMENTS  # noqa: E402

from app.core.database import SessionLocal, engine, Base  # noqa: E402
from app.models.skill import Skill, SkillPrerequisite  # noqa: E402
from app.models.resource import Resource, ResourceSkill, ResourcePrerequisite  # noqa: E402
from app.models.progress import Assessment  # noqa: E402
from app.embeddings.embedder import embed_texts  # noqa: E402
import app.models  # noqa: E402,F401  (ensures all models are registered on Base)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")


def seed_skills(db):
    logger.info("Seeding skills...")
    name_to_skill = {}
    names = list(SKILLS.keys())
    descriptions = [SKILLS[n][0] for n in names]
    embeddings = embed_texts(descriptions)

    for name, embedding in zip(names, embeddings):
        existing = db.query(Skill).filter(Skill.name == name).first()
        if existing:
            name_to_skill[name] = existing
            continue
        desc, category, difficulty = SKILLS[name]
        skill = Skill(
            id=uuid.uuid4(), name=name, description=desc, category=category,
            difficulty=difficulty, embedding=embedding,
        )
        db.add(skill)
        name_to_skill[name] = skill
    db.commit()

    logger.info("Seeding skill prerequisites...")
    for skill_name, prereq_names in PREREQUISITES.items():
        skill = name_to_skill.get(skill_name)
        if not skill:
            continue
        for prereq_name in prereq_names:
            prereq = name_to_skill.get(prereq_name)
            if not prereq:
                continue
            existing = (
                db.query(SkillPrerequisite)
                .filter(
                    SkillPrerequisite.skill_id == skill.id,
                    SkillPrerequisite.prerequisite_skill_id == prereq.id,
                )
                .first()
            )
            if not existing:
                db.add(
                    SkillPrerequisite(
                        id=uuid.uuid4(), skill_id=skill.id, prerequisite_skill_id=prereq.id
                    )
                )
    db.commit()
    logger.info("Seeded %d skills.", len(name_to_skill))
    return name_to_skill


def seed_resources(db, name_to_skill):
    logger.info("Seeding resources (this computes embeddings, may take a moment)...")
    existing_titles = {r.title for r in db.query(Resource.title).all()}
    to_insert = [r for r in RESOURCES if r["title"] not in existing_titles]
    if not to_insert:
        logger.info("Resources already seeded, skipping.")
        return

    texts = [f"{r['title']}. {r['description']}" for r in to_insert]
    embeddings = embed_texts(texts)

    for res, embedding in zip(to_insert, embeddings):
        resource = Resource(
            id=uuid.uuid4(),
            title=res["title"],
            description=res["description"],
            provider=res["provider"],
            url=res["url"],
            resource_type=res["resource_type"],
            difficulty=res["difficulty"],
            estimated_hours=res["estimated_hours"],
            embedding=embedding,
        )
        db.add(resource)
        db.flush()

        for skill_name in res.get("skills", []):
            skill = name_to_skill.get(skill_name)
            if skill:
                db.add(ResourceSkill(id=uuid.uuid4(), resource_id=resource.id, skill_id=skill.id))

        for prereq_name in res.get("prerequisites", []):
            prereq_skill = name_to_skill.get(prereq_name)
            if prereq_skill:
                db.add(
                    ResourcePrerequisite(
                        id=uuid.uuid4(), resource_id=resource.id, prerequisite_skill_id=prereq_skill.id
                    )
                )
    db.commit()
    logger.info("Seeded %d resources.", len(to_insert))


def seed_assessments(db, name_to_skill):
    logger.info("Seeding assessments...")
    existing_titles = {a.title for a in db.query(Assessment.title).all()}
    count = 0
    for item in ASSESSMENTS:
        if item["title"] in existing_titles:
            continue
        skill = name_to_skill.get(item["skill"])
        db.add(
            Assessment(
                id=uuid.uuid4(),
                skill_id=skill.id if skill else None,
                title=item["title"],
                questions=item["questions"],
            )
        )
        count += 1
    db.commit()
    logger.info("Seeded %d assessments.", count)


def main():
    Base.metadata.create_all(bind=engine)  # safety net; migrations/001_init.sql is the source of truth
    db = SessionLocal()
    try:
        name_to_skill = seed_skills(db)
        seed_resources(db, name_to_skill)
        seed_assessments(db, name_to_skill)
        logger.info("Seeding complete.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
