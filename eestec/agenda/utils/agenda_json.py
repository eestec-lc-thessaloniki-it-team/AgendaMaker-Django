from django.forms import model_to_dict

from ..models import Agenda


def agenda_json(agenda: Agenda):
    json = {"lc": agenda.lc, "date": agenda.date}
    sections = []
    for s in agenda.section_set.all().order_by("position"):
        topics = []
        for t in s.topic_set.all().order_by("position"):
            topics.append(model_to_dict(t))
        sections.append({"section_name": s.section_name,"position":s.position, "topics": topics})
    json["sections"] = sections
    return json
