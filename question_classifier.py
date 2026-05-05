#!/usr/bin/env python3
# coding: utf-8

import os
import ahocorasick

class QuestionClassifier:
    def __init__(self):
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        self.disease_path = os.path.join(cur_dir, 'dict/disease.txt')
        self.department_path = os.path.join(cur_dir, 'dict/department.txt')
        self.check_path = os.path.join(cur_dir, 'dict/check.txt')
        self.drug_path = os.path.join(cur_dir, 'dict/drug.txt')
        self.food_path = os.path.join(cur_dir, 'dict/food.txt')
        self.producer_path = os.path.join(cur_dir, 'dict/producer.txt')
        self.symptom_path = os.path.join(cur_dir, 'dict/symptom.txt')
        self.deny_path = os.path.join(cur_dir, 'dict/deny.txt')
        self.disease_wds = [i.strip() for i in open(self.disease_path, encoding='utf-8') if i.strip()]
        self.department_wds = [i.strip() for i in open(self.department_path, encoding='utf-8') if i.strip()]
        self.check_wds = [i.strip() for i in open(self.check_path, encoding='utf-8') if i.strip()]
        self.drug_wds = [i.strip() for i in open(self.drug_path, encoding='utf-8') if i.strip()]
        self.food_wds = [i.strip() for i in open(self.food_path, encoding='utf-8') if i.strip()]
        self.producer_wds = [i.strip() for i in open(self.producer_path, encoding='utf-8') if i.strip()]
        self.symptom_wds = [i.strip() for i in open(self.symptom_path, encoding='utf-8') if i.strip()]
        self.region_words = set(self.department_wds + self.disease_wds + self.check_wds + self.drug_wds + self.food_wds + self.producer_wds + self.symptom_wds)
        self.deny_words = [i.strip() for i in open(self.deny_path, encoding='utf-8') if i.strip()]
        self.region_tree = self.build_actree(list(self.region_words))
        self.wdtype_dict = self.build_wdtype_dict()
        self.symptom_qwds = ['症状', '表征', '现象', '症候', '表现']
        self.cause_qwds = ['原因', '成因', '为什么', '怎么会', '会导致', '会造成']
        self.acompany_qwds = ['并发症', '并发', '伴随', '共现']
        self.food_qwds = ['饮食', '吃', '食', '喝', '忌口', '补品', '食物', '菜']
        self.drug_qwds = ['药', '药品', '用药', '胶囊', '口服液', '炎片']
        self.prevent_qwds = ['预防', '防范', '防止', '避免', '免得']
        self.lasttime_qwds = ['周期', '多久', '多长时间', '多少时间', '几天', '几年']
        self.cureway_qwds = ['怎么治疗', '如何医治', '怎么治', '怎么办', '咋办']
        self.cureprob_qwds = ['几率', '能治', '可治', '可以治', '能治好']
        self.easyget_qwds = ['易感人群', '什么人', '哪些人', '感染']
        self.check_qwds = ['检查', '检查项目', '查出', '测出']
        self.belong_qwds = ['什么科', '科室', '属于']
        self.cure_qwds = ['治疗什么', '治啥', '主治', '有什么用', '用来', '能治啥']
        print('model init finished .......')
        return

    def classify(self, question):
        data = {}
        medical_dict = self.check_medical(question)
        if not medical_dict:
            return {}
        data['args'] = medical_dict
        types = []
        for type_ in medical_dict.values():
            types += type_
        question_types = []

        if self.check_words(self.symptom_qwds, question) and ('disease' in types):
            question_types.append('disease_symptom')
        if self.check_words(self.symptom_qwds, question) and ('symptom' in types):
            question_types.append('symptom_disease')
        if self.check_words(self.cause_qwds, question) and ('disease' in types):
            question_types.append('disease_cause')
        if self.check_words(self.acompany_qwds, question) and ('disease' in types):
            question_types.append('disease_acompany')
        if self.check_words(self.food_qwds, question) and 'disease' in types:
            deny_status = self.check_words(self.deny_words, question)
            if deny_status:
                question_types.append('disease_not_food')
            else:
                question_types.append('disease_do_food')
        if self.check_words(self.food_qwds + self.cure_qwds, question) and 'food' in types:
            deny_status = self.check_words(self.deny_words, question)
            if deny_status:
                question_types.append('food_not_disease')
            else:
                question_types.append('food_do_disease')
        if self.check_words(self.drug_qwds, question) and 'disease' in types:
            question_types.append('disease_drug')
        if self.check_words(self.cure_qwds, question) and 'drug' in types:
            question_types.append('drug_disease')
        if self.check_words(self.check_qwds, question) and 'disease' in types:
            question_types.append('disease_check')
        if self.check_words(self.check_qwds + self.cure_qwds, question) and 'check' in types:
            question_types.append('check_disease')
        if self.check_words(self.prevent_qwds, question) and 'disease' in types:
            question_types.append('disease_prevent')
        if self.check_words(self.lasttime_qwds, question) and 'disease' in types:
            question_types.append('disease_lasttime')
        if self.check_words(self.cureway_qwds, question) and 'disease' in types:
            question_types.append('disease_cureway')
        if self.check_words(self.cureprob_qwds, question) and 'disease' in types:
            question_types.append('disease_cureprob')
        if self.check_words(self.easyget_qwds, question) and 'disease' in types:
            question_types.append('disease_easyget')
        if question_types == [] and 'disease' in types:
            question_types = ['disease_desc']
        if question_types == [] and 'symptom' in types:
            question_types = ['symptom_disease']
        data['question_types'] = question_types
        return data

    def build_wdtype_dict(self):
        wd_dict = dict()
        for wd in self.region_words:
            wd_dict[wd] = []
            if wd in self.disease_wds:
                wd_dict[wd].append('disease')
            if wd in self.department_wds:
                wd_dict[wd].append('department')
            if wd in self.check_wds:
                wd_dict[wd].append('check')
            if wd in self.drug_wds:
                wd_dict[wd].append('drug')
            if wd in self.food_wds:
                wd_dict[wd].append('food')
            if wd in self.symptom_wds:
                wd_dict[wd].append('symptom')
            if wd in self.producer_wds:
                wd_dict[wd].append('producer')
        return wd_dict

    def build_actree(self, wordlist):
        actree = ahocorasick.Automaton()
        for index, word in enumerate(wordlist):
            actree.add_word(word, (index, word))
        actree.make_automaton()
        return actree

    def check_medical(self, question):
        region_wds = []
        for i in self.region_tree.iter(question):
            wd = i[1][1]
            region_wds.append(wd)
        stop_wds = []
        for wd1 in region_wds:
            for wd2 in region_wds:
                if wd1 in wd2 and wd1 != wd2:
                    stop_wds.append(wd1)
        final_wds = [i for i in region_wds if i not in stop_wds]
        final_dict = {i: self.wdtype_dict.get(i) for i in final_wds}
        return final_dict

    def check_words(self, wds, sent):
        for wd in wds:
            if wd in sent:
                return True
        return False


if __name__ == '__main__':
    handler = QuestionClassifier()
    while 1:
        question = input('input an question:')
        data = handler.classify(question)
        print(data)