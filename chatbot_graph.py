#!/usr/bin/env python3
# coding: utf-8

from question_classifier import *
from question_parser import *
from answer_search import *

class ChatBotGraph:
    def __init__(self):
        self.classifier = QuestionClassifier()
        self.parser = QuestionPaser()
        self.searcher = AnswerSearcher()

    def chat_main(self, sent):
        answer = '您好，我是医药智能助理，希望可以帮到您。祝您身体棒棒！'
        res_classify = self.classifier.classify(sent)
        if not res_classify:
            return answer
        res_sql = self.parser.parser_main(res_classify)
        final_answers = self.searcher.search_main(res_sql)
        if not final_answers:
            return answer
        else:
            return '\n'.join(final_answers)

if __name__ == '__main__':
    handler = ChatBotGraph()
    print("=" * 60)
    print("  医疗问答助手已启动")
    print("  输入 exit 退出")
    print("=" * 60)
    while 1:
        question = input('\n用户: ')
        if question.lower() in ['exit', 'quit', '退出', 'q']:
            print('助手: 再见！祝您健康！')
            break
        answer = handler.chat_main(question)
        print('助手:', answer)