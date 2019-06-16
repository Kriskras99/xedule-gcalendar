#!/usr/bin/env python3
from gcalendar import Calendar, Event
from xedule import Xedule, TeachingMethod


def main(username: str, password: str):
    x = Xedule(username, password)
    calendar = Calendar()

    # load all data
    academies = x.organisational_unit()
    teachers = x.docent()
    groups = x.group()
    facilities = x.facility()

    id_lookup = {}
    code_lookup = {}
    for i in academies:
        id_lookup[academies[i]['id']] = academies[i]
        code_lookup[academies[i]['code']] = academies[i]
    for i in teachers:
        id_lookup[teachers[i]['id']] = teachers[i]
        code_lookup[teachers[i]['code']] = teachers[i]
    for i in groups:
        id_lookup[groups[i]['id']] = groups[i]
        code_lookup[groups[i]['code']] = groups[i]
    for i in facilities:
        id_lookup[facilities[i]['id']] = facilities[i]
        code_lookup[facilities[i]['code']] = facilities[i]

    # what schedules and weeks to add
    ids = []
    inp = input("What should be in the schedule? (comma separated): ")
    for code in inp.split(','):
        code = code.strip()
        try:
            ids.append(code_lookup[code]['id'])
        except KeyError:
            print("%s not recognized, skipping " % code)
    weeks = []
    inp = input("What weeks should be added? (comma separated): ")
    for week in inp.split(','):
        weeks.append(int(week.strip()))

    # parse and add everything
    for week in weeks:
        schedule = x.schedule(ids, week)
        for schedule_i in schedule:
            parsed = x.parse_name(schedule_i['name'])
            title = parsed['name']
            if parsed['teaching_method'] == TeachingMethod.PRACTICUM:
                title = "Practicum - " + title
            rooms = []
            teachers = []
            classes = []
            description = ""

            for i in schedule_i['atts']:
                i = str(i)
                if 'attTLs' in id_lookup[i]:
                    teachers.append(id_lookup[i])
                elif 'attDLs' in id_lookup[i]:
                    classes.append(id_lookup[i])
                else:
                    rooms.append(id_lookup[i])

            if len(rooms):
                location = rooms[0]['code']
                if len(rooms) > 1:
                    description += "Rooms: " + location
                    for i in range(1, len(rooms)):
                        description += ", " + rooms[i]['code']
                    description += "\n"
            else:
                location = ""
            if len(teachers):
                description += "Teachers: " + teachers[0]['code']
                for i in range(1, len(teachers)):
                    description += ", " + teachers[i]['code']
                description += "\n"
            
            if len(classes):
                description += "Classes: " + classes[0]['code']
                for i in range(1, len(classes)):
                    description += ", " + classes[i]['code']

            start = schedule_i['iStart']
            end = schedule_i['iEnd']

            event = Event(title, location, description, start, end)
            if not filter_fun(event):
                calendar.add_event(event)


# modify this function to filter certain classes
def filter_fun(event: Event):
    return False


if __name__ == "__main__":
    username = input("Username: ")
    password = input("Password: ")
    main(username, password)
