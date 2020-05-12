# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.db import models
# Create your models here.
from django.forms import model_to_dict


class Agenda(models.Model):
    date = models.DateField()
    lc = models.CharField(max_length=50)

    def __str__(self):
        return str(self.date) + " " + self.lc


class Section(models.Model):
    agenda = models.ForeignKey(Agenda, on_delete=models.CASCADE)
    section_name = models.CharField(max_length=200)
    position = models.IntegerField(default=0)

    def __str__(self):
        return self.section_name


class Topic(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    topic_name = models.CharField(max_length=200)
    votable = models.BooleanField()
    yes_no_vote = models.BooleanField()
    open_ballot = models.BooleanField()
    position = models.IntegerField(default=0)
    possible_answers = models.CharField(max_length=1000)

    @classmethod
    def create(cls, topic_name, votable, yes_no_vote, open_ballot, possible_answers):
        topic = Topic(topic_name=topic_name, votable=votable, yes_no_vote=yes_no_vote, open_ballot=open_ballot)
        topic.set_answers(possible_answers)
        return Topic

    def __str__(self):
        return self.topic_name

    def set_answers(self, x):
        self.possible_answers = json.dumps(x)

    def get_answers(self):
        return json.loads(self.possible_answers)
