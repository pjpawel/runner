import os
from .counter import Counter


class ProgressBar:
    def __init__(self, max_value=100, width=50, use_counter=True):
        """
        Initialize progress bar with max value and display width

        Args:
            max_value (int): Maximum value for the progress bar
            width (int): Width of the progress bar in characters
            use_counter (bool): Whether to get value from _Counter class
        """
        self.max_value = max_value
        self.current_value = 0
        self.width = width
        self.use_counter = use_counter

    def set_max_value(self, max_value):
        """Set the maximum value for the progress bar"""
        if max_value <= 0:
            raise ValueError("Max value must be greater than 0")
        self.max_value = max_value
        # Adjust current value if it exceeds new max
        if self.current_value > max_value:
            self.current_value = max_value

    def get_current_value(self):
        """Function to check/get the actual current value"""
        if self.use_counter:
            return Counter.get_count()
        return self.current_value

    def get_max_value(self):
        """Get the maximum value"""
        return self.max_value

    def get_percentage(self):
        """Get the current percentage completed"""
        if self.max_value == 0:
            return 0
        return (self.current_value / self.max_value) * 100

    def set_value(self, value):
        """Set the current value (clamps between 0 and max_value)"""
        clamped_value = max(0, min(value, self.max_value))
        if self.use_counter:
            # Reset counter and set to new value
            Counter.reset()
            Counter.increment(clamped_value)
        else:
            self.current_value = clamped_value

    def increment(self, amount=1):
        """Increment the current value by specified amount"""
        if self.use_counter:
            new_value = min(Counter.get_count() + amount, self.max_value)
            current_count = Counter.get_count()
            if new_value > current_count:
                Counter.increment(new_value - current_count)
        else:
            self.set_value(self.current_value + amount)

    def decrement(self, amount=1):
        """Decrement the current value by specified amount"""
        self.set_value(self.current_value - amount)

    def reset(self):
        """Reset the progress bar to 0"""
        if self.use_counter:
            Counter.reset()
        else:
            self.current_value = 0

    def complete(self):
        """Set the progress bar to maximum value"""
        self.current_value = self.max_value

    def display(self, prefix="Progress", suffix="Complete"):
        """
        Display the progress bar

        Args:
            prefix (str): Text to display before the progress bar
            suffix (str): Text to display after the progress bar
        """
        percentage = self.get_percentage()
        current = self.get_current_value()
        filled_length = int(self.width * current // self.max_value)

        # Create the progress bar visual
        bar_fill = "█" * filled_length
        bar_empty = "░" * (self.width - filled_length)
        bar = bar_fill + bar_empty

        # Color coding based on percentage
        if percentage < 30:
            color_code = "\033[91m"  # Red
        elif percentage < 70:
            color_code = "\033[93m"  # Yellow
        else:
            color_code = "\033[92m"  # Green

        reset_code = "\033[0m"  # Reset color

        # Create the display string
        display_str = f"\r{prefix}: |{color_code}{bar}{reset_code}| {current}/{self.max_value} ({percentage:.1f}%) {suffix}"

        # Print without newline to allow updating
        print(display_str, end="", flush=True)

    def display_line(self, prefix="Progress", suffix="Complete"):
        """Display the progress bar with a newline (for final display)"""
        self.display(prefix, suffix)
        print()  # Add newline


def clear_screen():
    """Clear the terminal screen"""
    os.system("cls" if os.name == "nt" else "clear")
