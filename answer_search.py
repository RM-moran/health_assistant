#!/usr/bin/env python3
# coding: utf-8

from py2neo import Graph

class AnswerSearcher:
    def __init__(self):
        self.g = Graph(
            "bolt://127.0.0.1:7687",
            auth=("neo4j", "12345678")
        )
        self.num_limit = 20

    def search_main(self, sqls):
        final_answers = []
        for sql_ in sqls:
            question_type = sql_['question_type']
            queries = sql_['sql']
            answers = []
            for query in queries:
                try:
                    ress = self.g.run(query).data()
                    answers += ress
                except Exception as e:
                    print(f"查询出错: {query}, 错误: {e}")
            final_answer = self.answer_prettify(question_type, answers)
            if final_answer:
                final_answers.append(final_answer)
        return final_answers

    def answer_prettify(self, question_type, answers):
        final_answer = ''
        if not answers:
            return ''

        try:
            if question_type == 'disease_symptom':
                desc = [i['n.name'] for i in answers]
                subject = answers[0]['m.name']
                final_answer = '「{}」的症状包括：{}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

            elif question_type == 'symptom_disease':
                desc = [i['m.name'] for i in answers]
                subject = answers[0]['n.name']
                final_answer = '症状「{}」可能染上的疾病有：{}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

            elif question_type == 'disease_cause':
                # 处理 cause 可能是列表或字符串的情况
                desc = []
                for i in answers:
                    cause = i.get('m.cause', '')
                    if isinstance(cause, list):
                        desc.extend(cause)
                    elif cause:
                        desc.append(str(cause))
                subject = answers[0]['m.name']
                final_answer = '「{}」可能的成因有：{}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

            elif question_type == 'disease_prevent':
                desc = []
                for i in answers:
                    prevent = i.get('m.prevent', '')
                    if isinstance(prevent, list):
                        desc.extend(prevent)
                    elif prevent:
                        desc.append(str(prevent))
                subject = answers[0]['m.name']
                final_answer = '「{}」的预防措施包括：{}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

            elif question_type == 'disease_lasttime':
                desc = []
                for i in answers:
                    lasttime = i.get('m.cure_lasttime', '')
                    if isinstance(lasttime, list):
                        desc.extend(lasttime)
                    elif lasttime:
                        desc.append(str(lasttime))
                subject = answers[0]['m.name']
                final_answer = '「{}」治疗可能持续的周期为：{}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

            elif question_type == 'disease_cureway':
                # 修复 cure_way 的 join 问题
                desc = []
                for i in answers:
                    cure_way = i.get('m.cure_way', '')
                    if isinstance(cure_way, list):
                        desc.append('；'.join([str(x) for x in cure_way]))
                    elif cure_way:
                        desc.append(str(cure_way))
                subject = answers[0]['m.name']
                final_answer = '「{}」可以尝试如下治疗：{}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

            elif question_type == 'disease_cureprob':
                desc = []
                for i in answers:
                    prob = i.get('m.cured_prob', '')
                    if isinstance(prob, list):
                        desc.extend(prob)
                    elif prob:
                        desc.append(str(prob))
                subject = answers[0]['m.name']
                final_answer = '「{}」治愈的概率为（仅供参考）：{}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

            elif question_type == 'disease_easyget':
                desc = []
                for i in answers:
                    easy_get = i.get('m.easy_get', '')
                    if isinstance(easy_get, list):
                        desc.extend(easy_get)
                    elif easy_get:
                        desc.append(str(easy_get))
                subject = answers[0]['m.name']
                final_answer = '「{}」的易感人群包括：{}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

            elif question_type == 'disease_desc':
                desc = []
                for i in answers:
                    desc_text = i.get('m.desc', '')
                    if isinstance(desc_text, list):
                        desc.extend(desc_text)
                    elif desc_text:
                        desc.append(str(desc_text))
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
                do_desc = [i['n.name'] for i in answers if i.get('r.name') == '宜吃']
                recommand_desc = [i['n.name'] for i in answers if i.get('r.name') == '推荐食谱']
                subject = answers[0]['m.name']
                final_answer = '「{}」宜食的食物包括有：{}\n推荐食谱包括有：{}'.format(
                    subject, 
                    '；'.join(list(set(do_desc))[:self.num_limit]) if do_desc else '无',
                    '；'.join(list(set(recommand_desc))[:self.num_limit]) if recommand_desc else '无'
                )

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

        except Exception as e:
            print(f"格式化答案出错: {e}")
            print(f"问题类型: {question_type}")
            print(f"原始数据: {answers}")
            return '抱歉，处理该问题时出现错误，请重新提问。'

        return final_answer


if __name__ == '__main__':
    searcher = AnswerSearcher()
    # 测试代码
    test_sqls = [{
        'question_type': 'disease_symptom',
        'sql': ["MATCH (m:Disease)-[r:has_symptom]->(n:Symptom) where m.name = '感冒' return m.name, r.name, n.name"]
    }]
    result = searcher.search_main(test_sqls)
    print(result)