class Device:
    def __init__(self, **kwargs):
        self.id = kwargs["id"]
        self.latitude = kwargs.get('latitude', 0)
        self.longitude = kwargs.get('longitude', 0)
        self.score = kwargs.get('score', float('inf'))
        self.token = kwargs.get('token', '')
        self.probability = kwargs.get('probability', 0)
        self.tasksSatisfied = kwargs.get('tasksSatisfied', 0)
        self.selected_times = kwargs.get("selected_times", 0)
        self.bat_level = kwargs.get("bat_level", 0)
        self.bat_status = kwargs.get("bat_status", '')
        self.unpredictability = kwargs.get("unpredictability", 0)
        self.predictability = kwargs.get("predictability", 0)

    def __contains__(self, item):
        return self.id == item.id

    def __str__(self):
        return "id: " + str(self.id) +\
               ", latitude: " + str(self.latitude) +\
               ", longitude: " + str(self.longitude) + \
               ", score: " + str(self.score) +\
               ", token: " + str(self.token) +\
               ", probability: " + str(self.probability) +\
               ", bat_level: " + str(self.bat_level) +\
               ", bat_status: " + str(self.bat_status)+\
               ", unpredictability : " + str(self.unpredictability) +\
               ", predictability : " + str(self.predictability)
