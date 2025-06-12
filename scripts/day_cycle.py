# scripts/day_cycle.py
import math

class DayCycle:
    def __init__(self, message_log_func):
        self.hour = 0
        self.max_hours_before_exhaustion = 12
        self.night_starts_at_hour = 8
        self.message_log = message_log_func
        self._night_announced = False # To prevent spamming "Night has fallen"
        self._dusk_announced = False  # To prevent spamming "Dusk is upon you"

    def increment_hour(self, value=1):
        """
        Increments the current hour by the given value.
        Logs messages related to time of day changes.
        Returns True if the day ends due to exhaustion, False otherwise.
        """
        self.hour += value
        # self.message_log(f"Hour: {self.hour}") # Removed, as hour is in the top panel

        if self.hour >= self.max_hours_before_exhaustion:
            self.message_log('') # Add a blank line for spacing before exhaustion message
            self.message_log('Exhaustion takes you.')
            return True # Indicates day should end / player should rest

        if self.hour >= self.night_starts_at_hour:
            if not self._night_announced:
                self.message_log('Night has fallen.')
                self._night_announced = True
                self._dusk_announced = True # If night is announced, dusk was also effectively announced
        elif self.hour >= self.night_starts_at_hour - 1: # Announce dusk one hour before night
             if not self._dusk_announced:
                self.message_log('Dusk is upon you.')
                self._dusk_announced = True
        else:
            # Reset announcement flags if it's clearly daytime again (e.g., after resting)
            if self.hour < self.night_starts_at_hour -1:
                self._night_announced = False
                self._dusk_announced = False
        
        return False # Day continues

    def is_night(self):
        """Returns True if it's currently night time, False otherwise."""
        return self.hour >= self.night_starts_at_hour

    def reset_day(self):
        """Resets the hour to the start of a new day."""
        self.hour = 0
        self._night_announced = False
        self._dusk_announced = False
        self.message_log('A new dawn breaks.')
        # self.message_log(f"Hour: {self.hour}") # Removed, as hour is in the top panel

    def get_enemy_night_modifier(self):
        """Returns a stat modifier for enemies if it's night."""
        if self.is_night():
            return 2 
        return 1.0