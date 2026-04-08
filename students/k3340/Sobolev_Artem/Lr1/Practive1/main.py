from typing import List, TypedDict

from fastapi import FastAPI

from models import Profession, RaceType, Skill, Warrior

app = FastAPI()

professions_db = [
    Profession(
        id=1,
        title="Влиятельный человек",
        description="Эксперт по всем вопросам",
    ),
    Profession(
        id=2,
        title="Дельфист-гребец",
        description="Уважаемый сотрудник",
    ),
]

temp_bd = [
    Warrior(
        id=1,
        race=RaceType.director,
        name="Мартынов Дмитрий",
        level=12,
        profession=professions_db[0],
        skills=[
            Skill(id=1, name="Управление", description="Умеет организовывать работу"),
            Skill(id=2, name="Переговоры", description="Умеет договариваться с людьми"),
        ],
    ),
    Warrior(
        id=2,
        race=RaceType.worker,
        name="Андрей Косякин",
        level=12,
        profession=professions_db[1],
        skills=[
            Skill(id=3, name="Плавание", description="Хорошо держится на воде"),
            Skill(id=4, name="Выносливость", description="Может долго работать"),
        ],
    ),
]


@app.get("/")
def hello():
    return "Hello, [username]!"


@app.get("/warriors_list")
def warriors_list():
    return temp_bd


@app.get("/warrior/{warrior_id}")
def warrior_get(warrior_id: int) -> List[Warrior]:
    return [warrior for warrior in temp_bd if warrior.id == warrior_id]


@app.post("/warrior")
def warrior_create(warrior: Warrior) -> TypedDict('Response', {"status": int, "data": Warrior}):
    warrior_to_append = warrior.model_dump()
    temp_bd.append(warrior_to_append)
    return {"status": 200, "data": warrior}


@app.delete("/warrior/delete{warrior_id}")
def warrior_delete(warrior_id: int):
    for i, warrior in enumerate(temp_bd):
        if warrior.id == warrior_id:
            temp_bd.pop(i)
            break
    return {"status": 201, "message": "deleted"}


@app.put("/warrior{warrior_id}")
def warrior_update(warrior_id: int, warrior: Warrior) -> List[Warrior]:
    for i, war in enumerate(temp_bd):
        if war.id == warrior_id:
            temp_bd[i] = warrior
    return temp_bd


@app.get("/professions_list")
def professions_list():
    return professions_db


@app.get("/profession/{profession_id}")
def profession_get(profession_id: int):
    return [profession for profession in professions_db if profession.id == profession_id]


@app.post("/profession")
def profession_create(profession: Profession)-> TypedDict('Response', {"status": int, "data": Profession}):
    professions_db.append(profession)
    return {"status": 200, "data": profession}


@app.delete("/profession/delete{profession_id}")
def profession_delete(profession_id: int):
    for i, profession in enumerate(professions_db):
        if profession.id == profession_id:
            professions_db.pop(i)
            break
    return {"status": 201, "message": "deleted"}


@app.put("/profession{profession_id}")
def profession_update(profession_id: int, profession: Profession):
    for i, prof in enumerate(professions_db):
        if prof.id == profession_id:
            professions_db[i] = profession
    return professions_db
