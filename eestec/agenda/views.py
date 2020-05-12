# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .utils.agenda_json import agenda_json
import json

from django.core.exceptions import ValidationError
from django.forms.models import model_to_dict
from django.http import JsonResponse, Http404
# Create your views here.
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .models import Agenda, Section, Topic


@csrf_exempt
def create_agenda(request):
    json_data = json.loads(request.body)
    if "date" in json_data and "lc" in json_data:
        try:
            a = Agenda(date=json_data["date"], lc=json_data["lc"])
            a.save()
            return JsonResponse({"status": 200, "id": a.id})
        except ValidationError:
            return JsonResponse({"status": 400, "msg": "Wrong format"})
    else:
        return JsonResponse({"status": 400, "msg": "Not all fields are given"})


def getAgendaByID(request, agenda_id: int):
    agenda = get_object_or_404(Agenda, pk=agenda_id)
    return JsonResponse({"status": 200, "agenda": agenda_json(agenda)})


@csrf_exempt
def createSection(request):
    data = json.loads(request.body)
    if "agenda_id" in data and "section_name" in data:
        agenda = get_object_or_404(Agenda, pk=data["agenda_id"])
        try:
            if "position" not in data:
                agenda.section_set.create(section_name=data["section_name"], position=agenda.section_set.count())
            else:
                for s in list(agenda.section_set.all().order_by("position"))[data["position"]:]:
                    s.position += 1
                    s.save()
                agenda.section_set.create(section_name=data["section_name"], position=data["position"])
            agenda.save()
        except ValidationError:
            return JsonResponse({"status": 400, "msg": "wrong format"})
    return JsonResponse({"status": 200, "agenda": agenda_json(agenda)})


@csrf_exempt
def createTopic(request):
    data = json.loads(request.body)
    if "agenda_id" in data and "section_position" in data and "topic_position" in data and "topic_json" in data:
        agenda = get_object_or_404(Agenda, pk=data["agenda_id"])
        try:
            section = agenda.section_set.get(position=data["section_position"])
        except Section.DoesNotExist:
            raise Http404("Section does not exist")
        try:
            for t in list(section.topic_set.all().order_by("position"))[data["topic_position"]:]:
                t.position += 1
                t.save()
            topic = data["topic_json"]
            section.topic_set.create(topic_name=topic["topic_name"], votable=topic["votable"],
                                     yes_no_vote=topic["yes_no_vote"], open_ballot=topic["open_ballot"],
                                     possible_answers=topic["possible_answers"])
            section.save()
            agenda.save()
        except:
            JsonResponse({"status": 400, "msg": "you didn't sent all the necessary information"})
    return JsonResponse({"status": 200, "agenda": agenda_json(agenda)})

@csrf_exempt
def updateAgenda(request):
    data = json.loads(request.body)
    if "agenda_id" in data and "new_agenda" in data:
        agenda = get_object_or_404(Agenda, pk=data["agenda_id"])
        newAgenda=data["new_agenda"]
        try:
            agenda.lc=newAgenda["lc"]
            agenda.date=newAgenda["date"]
            agenda.save()
        except:
            return JsonResponse({"status": 400, "msg": "wrong format"})
    return JsonResponse({"status":200,"agenda":agenda_json(agenda)})


def updateSection(request):
    return JsonResponse()


def updateTopic(request):
    return JsonResponse()


def deleteAgenda(request):
    return JsonResponse()


def deleteSection(request):
    return JsonResponse()


def deleteTopic(request):
    return JsonResponse()
