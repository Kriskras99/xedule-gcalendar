from requests import Session
from bs4 import BeautifulSoup
from enum import Enum


class Xedule:
    def __init__(self, username: str, password: str):
        self.s = Session()
        r = self.s.get("https://sa-saxion.xedule.nl/")
        r = self.s.post(r.url, data={'UserName': username, 'Password': password, 'AuthMethod': 'FormsAuthentication'})
        r = self.s.post("https://engine.surfconext.nl/authentication/sp/consume-assertion", data={
            'SAMLResponse': BeautifulSoup(r.text, 'lxml').input['value']})
        soup = BeautifulSoup(r.text, 'lxml')
        self.s.post("https://sso.xedule.nl/AssertionService.aspx", data={
            "SAMLResponse": soup.find_all("input")[0]['value'],
            "RelayState": soup.find_all("input")[1]['value']})

    def organisational_unit(self) -> dict:
        """
        Get the current supported academies and their ids/yea(r)s.

        Example:
        academies['LED'] == academies['3'] ==
            {"code": "LED","id": "3","timeZone": "W. Europe Standard Time","yeas": ["3_2018"]}
        """
        r = self.s.get("https://sa-saxion.xedule.nl/api/organisationalUnit").json()
        academies = {}
        for i in r:
            academies[i['code']] = i
            academies[i['id']] = i
        return academies

    def docent(self) -> dict:
        """
        Get all the teachers in the schedule system. Keys are teacher code or id

        Example:
        teachers['CSL02'] == teachers['44'] ==
            {"attGLs":[],"attTLs":[],"code": "CSL02","id":"44","name":null,"orus":[2],"tsss":["2_2018___44"]}
        """
        r = self.s.get("https://sa-saxion.xedule.nl/api/docent").json()
        teachers = {}
        for i in r:
            teachers[i['code']] = i
            teachers[i['id']] = i
        return teachers

    def year(self) -> list:
        """
        Get info on the years returned by the organisational_units.

        Example:
        [{
            "avis": null,
            "cal": "3_2018",
            "deps": null,
            "firstDayOfWeek": 1,
            "hasCalendar": true,
            "iEnd": "2019-08-24T00:00:00",
            "iEndOfDay": "21:30:00",
            "iStart": "2018-08-27T00:00:00",
            "iStartOfDay": "08:30:00",
            "id": "3_2018",
            "lastDayOfWeek": 5,
            "oru": 3,
            "periodCount": 5,
            "schs": [
                22,
                24,
                25,
                19,
                21,
                20,
                23,
                27,
                26,
                28
            ],
            "year": 2018
        }]
        """
        return self.s.get("https://sa-saxion.xedule.nl/api/docent").json()

    def group(self) -> dict:
        """
        Get all groups as a dictionary. Keys are group code or group id.

        Example:
        groups['EEL1ID'] == groups['3353'] == {"attDLs":[],"code":"EEL1ID","id":"3353","orus":[3]}
        """
        r = self.s.get("https://sa-saxion.xedule.nl/api/group").json()
        groups = {}
        for i in r:
            groups[i['code']] = i
            groups[i['id']] = i
        return groups

    def team(self) -> list:
        """
        No clue, api currently returns an empty list.
        """
        return self.s.get("https://sa-saxion.xedule.nl/api/team").json()

    def facility(self) -> dict:
        """
        Get the classrooms. Keys are room number or room id.

        Example:
        fac['W3.10'] == fac['408'] == {"code":"W3.10","id":"408","orus":[2,3]}
        """
        r = self.s.get("https://sa-saxion.xedule.nl/api/facility").json()
        facilities = {}
        for i in r:
            facilities[i['code']] = i
            facilities[i['id']] = i
        return facilities

    def student(self, ids: list) -> list:
        """
        Get student specific schedule I guess?
        Currently always returns an empty list.
        """
        data = {}
        i = 0
        for j in ids:
            data['ids[%s]' % i] = j
            i += 1
        return self.s.get("https://sa-saxion.xedule.nl/api/student", params=data).json()

    def schedule(self, ids: list, week: int, year=2018, academy=3) -> list:
        """
        Get the week schedule of the specified ids.
        Format: academy_year_week_id
        For example to get the schedule for week 21 (2019), for the school year 2018-2019,
            and the class EEL1ID (LED): 3_2018_21_3353
        """
        data = {}
        i = 0
        for j in ids:
            data['ids[%s]' % i] = '%s_%s_%s_%s' % (academy, year, week, j)
            i += 1
        r = self.s.get("https://sa-saxion.xedule.nl/api/schedule", params=data).json()
        added_ids = []
        courses = []
        for i in r:
            for j in i['apps']:
                if j['id'] not in added_ids:
                    added_ids.append(j['id'])
                    courses.append(j)
        return courses

    def calendar(self, academy_id, year) -> dict:
        """
        Get information on this school year for this academy.
        """
        return self.s.get("https://sa-saxion.xedule.nl/api/calendar/" + academy_id + '_' + year).json()

    @staticmethod
    def parse_name(name: str) -> dict:
        """
        Parses a course name on the schedule to something useful.
        """
        if name.count('_') < 3:
            return {
                "name": name,
                "bison_code": None,
                "teaching_method": None
            }
        else:
            split = name.split('_')
            return {
                "bison_code": split[0],
                "teaching_method": TeachingMethod(split[1]),
                "name": split[2]
            }


class TeachingMethod(Enum):
    LECTURE = 'HC'
    SEMINAR = 'WC'
    PRACTICUM = 'PR'
    PROJECT = 'PJ'
    SLB = 'SL'
