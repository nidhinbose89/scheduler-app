#!/usr/bin/env python

import datetime
import time
import random
import sys
# The conference has multiple tracks each of which has a morning and afternoon session.
# Each session contains multiple talks.
# Morning sessions begin at 9am and must finish by 12 noon, for lunch.
# Afternoon sessions begin at 1pm and must finish in time for the networking event.
# The networking event can start no earlier than 4:00 and no later than 5:00.
# No talk title has numbers in it.
# All talk lengths are either in minutes (not hours) or lightning (5 minutes).
# Presenters will be very punctual; there needs to be no gap between sessions.
conference_data = {
    'session': {'normal_duration': 180},
    'morning': {'begin_time': 9, 'finish_time': 12, 'duration': 180},
    'lunch': {'begin_time': '12:00PM', 'finish_time': 1, 'duration': 60},
    'afternoon': {'begin_time': 13, 'duration': 180, 'extra_duration': 60},
    'networking': {'name': ' Networking Event', 'start_upper_limit_time': 16, 'start_lower_limit_time': 17},
    'lightning': {'name': 'lightning', 'duration': 5},
}

test_data = """Writing Fast Tests Against Enterprise Rails 60min
Overdoing it in Python 45min
Lua for the Masses 30min
Ruby Errors from Mismatched Gem Versions 45min
Common Ruby Errors 45min
Rails for Python Developers lightning
Communicating Over Distance 60min
Accounting-Driven Development 45min
Woah 30min
Sit Down and Write 30min
Pair Programming vs Noise 45min
Rails Magic 60min
Ruby on Rails: Why We Should Move On 60min
Clojure Ate Scala (on my project) 45min
Programming in the Boondocks of Seattle 30min
Ruby vs. Clojure for Back-End Development 30min
Ruby on Rails Legacy App Maintenance 60min
A World Without HackerNews 30min
User Interface CSS in Rails Apps 30min
"""


class Scheduler():

    def __init__(self, data):
        self.data = data
        self.track_number = 0
        self.items = {}
        self.create_items()
        self.scheduler()

    def print_error_and_exit(self):
        print "Talk title cannot have numbers - ERROR"
        sys.exit()

    def create_items(self):
        for value in iter(self.data.splitlines()):
            duration = filter(str.isdigit, value)
            if value.endswith('lightning'):
                if filter(str.isdigit, value.split('lightning')[0]):
                    self.print_error_and_exit()
            if duration:
                if filter(str.isdigit, value.split(str(duration))[0]):
                    self.print_error_and_exit()
                duration = int(duration)
            else:
                duration = 'lightning'

            self.items.update({value: duration})

    def subsets_with_sum(self, itemz, target=0):
        """
            method to find the varios combination of items for a target Horus
            params
                itemz - dictionary containing events, they are made to various combinations
                        based on their duration to fit in the target hours
                        Eg - {'Rails Magic 60min': 60, 'Communicating Over Distance 60min': 60,
                            'Programming in the Boondocks of Seattle 30min': 30,
                            'Writing Fast Tests Against Enterprise Rails 60min': 60,
                            'Common Ruby Errors 45min': 45, 'Rails for Python Developers lightning': 5,
                            'Ruby on Rails: Why We Should Move On 60min': 60,
                            'Accounting-Driven Development 45min': 45}
                target - target hours; to find the combination for with the itemz dict.
                        Its the total duration of the session
                        Eg - 180 - morning session duration
        """
        x = 1
        enumr_items = dict(enumerate(itemz.items()))

        def _subsets_with_sum(idx, dik, oplist, targ):
            if targ == sum(dik.values()):
                oplist.append(dik)
            elif targ < sum(dik.values()):
                return
            for idd in range(idx, len(enumr_items)):
                key = dict(enumr_items)[idd][0]
                if itemz[key] == conference_data['lightning']['name']:
                    itemz[key] = conference_data['lightning']['duration']
                _subsets_with_sum(idd + x, dict(dik.items() + {key: itemz[key]}.items()), oplist, targ)
            return oplist
        return _subsets_with_sum(0, {}, [], target)

    def print_dict_events_to_time_schedule(self, start_time, event_items):
        """
            print dictionary of events to time schedule
            params
                    start_time - corresponding to the begining of a session in Horus in 24 hrs clock
                    Eg - morning session starts at 9
                         afternoon session starts at 13
                    event_items - dictionary of event items
                     Eg - {'Pair Programming vs Noise 45min': 45,
                           'Clojure Ate Scala (on my project) 45min': 45,
                           'Programming in the Boondocks of Seattle 30min': 30,
                           'Ruby vs. Clojure for Back-End Development 30min': 30,
                           'A World Without HackerNews 30min': 30}
        """
        self.remove_added_sessions_from_items(event_items)
        a = datetime.timedelta(hours=start_time)
        for i, (k, v) in enumerate(event_items.items()):
            if i == 0:
                print time.strftime("%I:%M%p", time.gmtime(a.seconds)), k
                if v == conference_data['lightning']['name']:
                    v = conference_data['lightning']['duration']
                a = a + datetime.timedelta(minutes=v)
                continue
            b_tim = time.strftime("%I:%M%p", time.gmtime(a.seconds))
            a = a + datetime.timedelta(minutes=v)
            print b_tim, k

    def remove_added_sessions_from_items(self, dict_item):
        """
            method to remove a dictionary from the whole "items" dictionary so that they wont be repeated once
            they are scheduled in a time slot
            dict_item - is the dictionary to be removed.
                    Eg- {'Rails Magic 60min': 60, 'Communicating Over Distance 60min': 60,
                        'Programming in the Boondocks of Seattle 30min': 30,
                        'Writing Fast Tests Against Enterprise Rails 60min': 60,
                        'Common Ruby Errors 45min': 45, 'Rails for Python Developers lightning': 5,
                        'Ruby on Rails: Why We Should Move On 60min': 60,
                        'Accounting-Driven Development 45min': 45}
        """
        for k, v in dict_item.items():
            self.items.pop(k, None)

    def print_last_session(self):
        """
            method to print the last session
        """
        networking = conference_data['networking']
        a = datetime.timedelta(hours=networking['start_upper_limit_time'])
        mandatory_end = datetime.timedelta(hours=conference_data['networking']['start_lower_limit_time'])
        is_not_filled = True
        while is_not_filled:
            for m, n in self.items.items():
                last_session_time = a
                a = a + datetime.timedelta(minutes=n)
                is_not_filled = a <= mandatory_end
                if is_not_filled:
                    a = a - datetime.timedelta(minutes=n)
                    a_tim = time.strftime("%I:%M%p", time.gmtime(a.seconds))
                    print a_tim, m
                    a = a + datetime.timedelta(minutes=n)
                    self.remove_added_sessions_from_items({m: n})
                    continue
                break
            else:
                if a.seconds < datetime.timedelta(hours=networking['start_upper_limit_time']).seconds:
                    print "04:00PM " + conference_data['networking']['name']
                elif a.seconds > datetime.timedelta(hours=networking['start_lower_limit_time']).seconds:
                    print "No networking session today"
                else:
                    print time.strftime("%I:%M%p", time.gmtime(a.seconds)) + conference_data['networking']['name']
                a = a - datetime.timedelta(minutes=n)
                break
        else:
            if last_session_time.seconds < datetime.timedelta(hours=networking['start_upper_limit_time']).seconds:
                print "04:00PM " + conference_data['networking']['name']
            elif last_session_time.seconds > datetime.timedelta(hours=networking['start_lower_limit_time']).seconds:
                print "No networking session today"
            else:
                print time.strftime("%I:%M%p", time.gmtime(last_session_time.seconds)) + conference_data['networking']['name']

    def scheduler(self):
        while self.items:
            not_found = True
            morning_session = {}
            evening_session = {}
            self.track_number += 1
            combination_probables = self.subsets_with_sum(self.items, conference_data['session']['normal_duration'])
            morning_session = combination_probables[0]
            combination_probables.remove(morning_session)
            while not_found:
                evening_session = random.choice(combination_probables)
                is_event_repeating = any(map(lambda each: each in morning_session, evening_session))
                if is_event_repeating:
                    continue
                else:
                    not_found = False
                    combination_probables.remove(evening_session)
                    break

            print "Track " + str(self.track_number) + ":"
            self.print_dict_events_to_time_schedule(conference_data['morning']['begin_time'], morning_session)
            print conference_data['lunch']['begin_time'] + " Lunch"
            self.print_dict_events_to_time_schedule(conference_data['afternoon']['begin_time'], evening_session)
            self.print_last_session()


if __name__ == '__main__':
    try:
        script, filename = sys.argv
        data = open(filename)
    except (ValueError, IOError):
        print "!!! INFO !!!"
        print "You can pass in the path of the file correctly along with the command to run application."
        print "Now using the test data."
        print "*** *** ***"
        data = test_data
    Scheduler(data)
