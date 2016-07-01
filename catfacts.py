from random import choice


class CatFacts(object):

  facts = []
  subscribers = {} # Format: {user_id: {fact_key: fact_count}}
  fact_count = 0

  def __init__(self):
    self.facts = open('facts.txt').readlines()

    self.fact_count = len(self.facts)

    subs = open('subscribers.txt')
    for line in subs:
      chunks = line.split(',')

      received_facts = {}
      for fact in chunks[1:]:
        fact = fact.split(':')
        received_facts[fact[0]] = int(fact[1])

      self.subscribers[chunks[0]] = received_facts

  def add_subscriber(self, user_id):
    if user_id in self.subscribers: return

    self.subscribers[user_id] = {}

  def remove_subscriber(self, user_id):
    if user_id not in self.subscribers: return
    self.subscribers.pop(user_id)

  def get_fact(self, subscriber = None):
    if subscriber != None and subscriber not in self.subscribers:
      subscriber = None

    fact = choice(range(self.fact_count))

    i = 0
    while subscriber != None and \
          fact in self.subscribers[subscriber] and \
          self.subscribers[subscriber][fact] == max(self.subscribers[subscriber].values()) and \
          i < 10:
      i += 1
      fact = choice(range(self.fact_count))

    if subscriber != None:
      if fact not in self.subscribers[subscriber]:
        self.subscribers[subscriber][fact] = 1
      else:
        self.subscribers[subscriber][fact] += 1

    return self.facts[fact]

  def write_subscribers(self):
    subs = open('subscribers.txt', 'w')
    for user, facts in self.subscribers.items():
      print('  Writing {}.'.format(user))
      subs.write(user)
      for fact, count in facts.items():
        subs.write(',' + str(fact) + ':' + str(count))
      subs.write('\n')
    subs.close

  def get_subscribers(self):
    return self.subscribers.keys()

  def list_subscribers(self):
    return '```' + '\n'.join(self.subscribers.keys()) + '```'
