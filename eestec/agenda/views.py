# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.core.exceptions import ValidationError
from django.http import JsonResponse, Http404
# Create your views here.
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .models import Agenda, Section, Topic
from .utils.agenda_json import agenda_json
from .utils.PositionFixing import fixPosition


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
                oldList=list(agenda.section_set.all().order_by("position"))
                normalizer=0
                for index,s in enumerate(list(agenda.section_set.all().order_by("position"))[data["position"]:]):
                    if index==data["position"]:
                        normalizer+=1
                    s.position =index+normalizer
                    s.save()
                agenda.section_set.create(section_name=data["section_name"], position=data["position"])
            agenda.save()
        except ValidationError:
            return JsonResponse({"status": 400, "msg": "wrong format"})
        return JsonResponse({"status": 200, "agenda": agenda_json(agenda)})
    else:
        return JsonResponse({"status":400,"msg":"you didn't sent all the necessary information"})


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
    else:
        return JsonResponse({"status":400,"msg":"you didn't sent all the necessary information"})

@csrf_exempt
def updateAgenda(request):
    data = json.loads(request.body)
    if "agenda_id" in data and "new_agenda" in data:
        agenda = get_object_or_404(Agenda, pk=data["agenda_id"])
        newAgenda=data["new_agenda"]
        try:
            if "lc" in newAgenda:
                agenda.lc = newAgenda["lc"]
            if "date" in newAgenda:
                agenda.date = newAgenda["date"]
            agenda.save()
        except:
            return JsonResponse({"status": 400, "msg": "wrong format"})
        return JsonResponse({"status":200,"agenda":agenda_json(agenda)})
    else:
        return JsonResponse({"status":400,"msg":"you didn't sent all the necessary information"})


@csrf_exempt
def updateSection(request):
    data = json.loads(request.body)
    if "agenda_id" in data and "section_position" in data and "section_json" in data:
        agenda = get_object_or_404(Agenda, pk=data["agenda_id"])
        newSection = data["section_json"]
        try:
            if "section_name" in newSection:
                section = get_object_or_404(Section,agenda=data["agenda_id"],position=data["section_position"])
                section.section_name = newSection["section_name"]
                section.save()
            if "position" in newSection:
                section = get_object_or_404(Section,agenda=data["agenda_id"],position=data["section_position"])
                old = list(agenda.section_set.all().order_by("position"))
                element = old[data["section_position"]]
                newList = []
                index = 0
                for s in range(len(old)+1):
                    if s == newSection["position"]:
                        newList.append(element)
                        continue
                    newList.append(old[index])
                    index += 1
                fixPosition(newList)
                section.position = newSection["position"]
                section.save()
            agenda.save()
        except:
            return JsonResponse({"status": 400, "msg": "wrong format"})
        return JsonResponse({"status": 200, "agenda": agenda_json(agenda)})
    else:
        return JsonResponse({"status":400,"msg":"you didn't sent all the necessary information"})


@csrf_exempt
def updateTopic(request):
    data = json.loads(request.body)
    if "agenda_id" in data and "section_position" in data and "topic_position" in data:
        agenda = get_object_or_404(Agenda, pk=data["agenda_id"])
        section=get_object_or_404(Section,agenda=data["agenda_id"],position=data["section_position"])

        topic=section.topic_set.get(position=data["topic_position"])
        newTopic=data["topic_json"]
        try:
            if "topic_name" in newTopic:
                topic.topic_name=newTopic["topic_name"]
            if "votable" in newTopic:
                topic.votable=newTopic["votable"]
            if "yes_no_vote" in newTopic:
                topic.yes_no_vote=newTopic["yes_no_vote"]
            if "open_ballot" in newTopic:
                topic.open_ballot=newTopic["open_ballot"]
            if "possible_answers" in newTopic:
                topic.set_answers(newTopic["possible_answers"])
            topic.save()
            if "position" in newTopic:
                #Todo: make this a function and use it in everything
                old = list(section.topic_set.all().order_by("position"))
                element = old[data["topic_position"]]
                newList = []
                index = 0
                for s in range(len(old)+1):
                    if s == newTopic["position"]:
                        newList.append(element)
                        continue
                    newList.append(old[index])
                    index += 1
                fixPosition(newList)
        except:
            return JsonResponse({"status": 400, "msg": "wrong format"})
        return JsonResponse({"status": 200, "agenda": agenda_json(agenda)})
    else:
        return JsonResponse({"status":400,"msg":"you didn't sent all the necessary information"})


@csrf_exempt
def deleteAgenda(request):
    data = json.loads(request.body)
    if "agenda_id" in data:
        agenda=get_object_or_404(Agenda,pk=data["agenda_id"])
        try:
            agenda.delete()
        except:
            return JsonResponse({"status":500,"msg":"Couldnt delete it due to internal problem"})
        return JsonResponse({"status":200})
    return JsonResponse({"status":400,"msg":"you didn't sent all the necessary information"})


@csrf_exempt
def deleteSection(request):
    data = json.loads(request.body)
    if "agenda_id" in data and "section_position" in data:
        agenda=get_object_or_404(Agenda,pk=data["agenda_id"])
        section=get_object_or_404(Section,agenda=agenda.id,position=data["section_position"])
        try:
            section.delete()
            fixPosition(agenda.section_set.all().order_by("position"))
        except:
            return JsonResponse({"status":500,"msg":"Couldnt delete it due to internal problem"})
        return JsonResponse({"status":200})
    return JsonResponse({"status":400,"msg":"you didn't sent all the necessary information"})


@csrf_exempt
def deleteTopic(request):
    data = json.loads(request.body)
    if "agenda_id" in data and "section_position" in data and "topic_position" in data:
        agenda=get_object_or_404(Agenda,pk=data["agenda_id"])
        section=get_object_or_404(Section,agenda=agenda.id, position=data["section_position"])
        topic=get_object_or_404(Topic,section=section.id,position=data["topic_position"])
        try:
            topic.delete()
            fixPosition(section.topic_set.all().order_by("position"))
        except:
            return JsonResponse({"status":500,"msg":"Couldnt delete it due to internal problem"})
        return JsonResponse({"status":200})
    return JsonResponse({"status":400,"msg":"you didn't sent all the necessary information"})

