import json, os, time
from money import money as m
from modules import PriceHistory, Performance, Price, ReturnHistory

class HistoryPrompt:
    def __init__(self):
        pass
    def ask_range(self, txt):
        answer_key = {
            'a': '5y',
            'b': '2y',
            'c': '1y',
            'd': 'ytd',
            'e': '6m',
            'f': '3m',
            'g': '1m',
            'h': '1d'
        }
        return answer_key[input(txt)]

class Prompt:
    def __init__(self):
        self.options = ['history', 'price', 'performance']
        self.mainquestions = []
        self.subquestions = {'history': []}
        self.load_messages()
    def load_questions(self, base_path, filenames):
        questions = []
        for filename in filenames:
            with open('{}\\{}'.format(base_path, filename), 'r') as f:
                questions.append(f.read())
        return questions
    def load_messages(self):
        realpath = os.path.realpath(__file__)
        dirpath = os.path.dirname(realpath)
        msg_dirpath = dirpath + '\\messages'

        # load the main messages / questions
        with open(msg_dirpath + '\\order.json', 'r') as q:

            m_qs = self.load_questions(msg_dirpath, json.loads(q.read())) # main questions
            self.mainquestions = list(m_qs)

        # load the universal questions
        uni_path = msg_dirpath + '\\universal'
        universal_files = os.listdir(uni_path)
        self.universal_qs = self.load_questions(uni_path, universal_files)


        # load the options specific questions
        for option in list(self.subquestions.keys()):
            base_msg_path = msg_dirpath + '\\' + option
            order_path = base_msg_path + '\\order.json'

            with open(order_path, 'r') as f:
                s_qs = self.load_questions(base_msg_path, json.loads(f.read()))
                self.subquestions[option] = s_qs
    def begin_questions(self):
        qs = self.mainquestions
        self.show_welcome(qs[0]) # display welcome message
        self.ask_symbols(qs[1]) # which symbols should I look up
        self.ask_action(qs[2]) # what data should I grab
    def show_welcome(self, text):
        print(text)
        time.sleep(4)
    def ask_symbols(self, question):
        self.symbols = input(question).split(',')
    def ask_action(self, text):
        answer_key = {'a': 'price_history', 'b': 'summary_performance', 'c': 'return_history', 'd': 'last_price'}
        choice = answer_key[input(text).lower()]
        option_actions = {
            'price_history': PriceHistory,
            'return_history': ReturnHistory,
            'summary_performance': Performance,
            'last_price': Price,
        }

        if choice == 'price_history':
            self.handle_price_hist_act(option_actions[choice])
        elif choice == 'summary_performance':
            self.handle_perf_smry_act(option_actions[choice])
        elif choice == 'return_history':
            self.handle_rtrn_hist_act(option_actions[choice])
        elif choice == 'last_price':
            self.handle_price_act(option_actions[choice])
    def handle_price_hist_act(self, action):
        qs = self.subquestions['history']
        us = self.universal_qs
        HP = HistoryPrompt()
        range = HP.ask_range(qs[0])
        path = input(us[0])
        action(self.symbols, path, range)
    def handle_perf_smry_act(self, action):
        us = self.universal_qs
        path = input(us[0])
        action(self.symbols, path)
    def handle_price_act(self, action):
        us = self.universal_qs
        path = input(us[0])
        action(self.symbols, path)
    def handle_rtrn_hist_act(self, action):
        qs = self.subquestions['history']
        us = self.universal_qs
        HP = HistoryPrompt()
        range = HP.ask_range(qs[0])
        path = input(us[0])
        action(self.symbols, path, range)