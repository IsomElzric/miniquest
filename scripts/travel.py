from abc import ABC, abstractmethod
import os


LOCATION_PATH = 'assets/locations/'
ART_PATH = 'assets/art/'
SOUND_PATH = 'assets/sound/'


class Travel():
    def __init__(self):
        self.current_location = [0, 0]
        self.location_dictionary = {'lastholm': [], 'aethelwood': [], 'scorlends': [], 'shadowsun': []}

    def build_locations(self):
        for key in self.location_dictionary:
            loc = key
            file_description = []
            temp_list = []
            
            for filename in os.listdir(LOCATION_PATH + loc + '/'):
                file_path = os.path.join(LOCATION_PATH + loc + '/', filename)
                with open(file_path, 'r') as file:
                    file_description.append(file.read())
                
                location_class = Location()
                location_class.location_name = filename
                location_class.location_description = file_description
                file_description.clear()

                temp_list.append(location_class)            

            self.location_dictionary[loc] = temp_list

    def get_location(self, region, location):
        loc_index = 0
        for i in self.location_dictionary[region]:
            if i.location_name == location:
                loc_index = self.location_dictionary[region].index(i)

        return self.location_dictionary[region][loc_index]


class Location(ABC):
    def __init__(self) -> None:
        super().__init__()
        self._location_name = ''
        self._location_description = ''

    @property
    def location_name(self):
        return self._location_name
    
    @location_name.setter
    def location_name(self, value):
        removed_suffix = value.removesuffix('.txt')
        self._location_name = removed_suffix.capitalize()

    @property
    def location_description(self):
        return self._location_description

    @location_description.setter
    def location_description(self, value):
        for i in value:
            self._location_description += i + '\n'

    def get_location_name(self):
        return self.location_name

    def show_location_description(self):
        print(self.location_description)
        


class Region(Location):
    def __init__(self) -> None:
        super().__init__()
        self.location_dictionary = {}
        self.region_lore = ''

    def add_region_location(self, loc):
        self.location_dictionary[loc.location_name] = loc.location_description

    def get_location(self, loc):
        return self.location_dictionary[loc]