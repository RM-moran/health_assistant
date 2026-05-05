#!/usr/bin/env python3
# coding: utf-8

from py2neo import Graph

class AnswerSearcher:
    def __init__(self):
        self.g = Graph(
            "bolt://127.0.0.1:7687",  # 使用 bolt 协议
            auth=("neo4j", "12345678")  # 使用 auth 参数
            )
        self.num_limit = 20

    def search_main(self, sqls):
        final_answers = []
        for sql_ in sqls:
            question_type = sql_['question_type']
            queries = sql_['sql']
            answers = []
            for query in queries:
                ress = self.g.run(query).data()
                answers += ress
            final_answer = self.answer_prettify(question_type, answers)
            if final_answer:
                final_answers.append(final_answer)
        return final_answers

    def answer_prettify(self, question_type, answers):
        final_answer = []
        if not answers:
            return ''
        if question_type == 'disease_symptom':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '「{}」的症状包括：{}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'symptom_disease':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '症状「{}」可能染上的疾病有：{}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'disease_cause':
            desc = [i['m.cause'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '「{}」可能的成因有：{}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'disease_prevent':
            desc = [i['m.prevent'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '「{}」的预防措施包括：{}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'disease_lasttime':
            desc = [i['m.cure_lasttime'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '「{}」治疗可能持续的周期为：{}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'disease_cureway':
            desc = [';'.join(i['m.cure_way']) for i in answers]
            subject = answers[0]['m.name']
            final_answer = '「{}」可以尝试如下治疗：{}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'disease_cureprob':
            desc = [i['m.cured_prob'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '「{}」治愈的概率为（仅供参考）：{}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'disease_easyget':
            desc = [i['m.easy_get'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '「{}」的易感人群包括：{}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'disease_desc':
            desc = [i['m.desc'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '「{}」，熟悉一下：{}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'disease_acompany':
            desc1 = [i['n.name'] for i in answers]
            desc2 = [i['m.name'] for i in answers]
            subject = answers[0]['m.name']
            desc = [i for i in desc1 + desc2 if i != subject]
            final_answer = '「{}」的并发症包括：{}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'disease_not_food':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '「{}」忌食的食物包括有：{}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'disease_do_food':
            do_desc = [i['n.name'] for i in answers if i['r.name'] == '宜吃']
            recommand_desc = [i['n.name'] for i in answers if i['r.name'] == '推荐食谱']
            subject = answers[0]['m.name']
            final_answer = '「{}」宜食的食物包括有：{}\n推荐食谱包括有：{}'.format(
                subject, ';'.join(list(set(do_desc))[:self.num_limit]),
                ';'.join(list(set(recommand_desc))[:self.num_limit]))
        elif question_type == 'food_not_disease':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '患有{}的人最好不要吃「{}」'.format('；'.join(list(set(desc))[:self.num_limit]), subject)
        elif question_type == 'food_do_disease':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '患有{}的人建议多试试「{}」'.format('；'.join(list(set(desc))[:self.num_limit]), subject)
        elif question_type == 'disease_drug':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '「{}」通常的使用的药品包括：{}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'drug_disease':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '「{}」主治的疾病有{}，可以试试'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'disease_check':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '「{}」通常可以通过以下方式检查出来：{}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'check_disease':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '通常可以通过「{}」检查出来的疾病有{}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))
        return final_answer


if __name__ == '__main__':
    searcher = AnswerSearcher()