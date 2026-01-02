"""
Event Log Manager
Handles all event logging functionality for City Rogue
"""

class EventLogManager:
    """Manages game event logs with scrolling support"""
    
    def __init__(self, max_log_lines=5):
        """
        Initialize the event log manager
        
        Args:
            max_log_lines: Maximum number of visible log lines
        """
        self.logs = []  # List of tuples: (text, color)
        self.log_scroll_offset = 0
        self.max_log_lines = max_log_lines
    
    def log(self, text, color=(255, 255, 255)):
        """
        Add a new log entry
        
        Args:
            text: The log message text
            color: RGB color tuple for the log message
        """
        self.logs.append((text, color))
        # Auto-scroll to bottom when new log is added
        if len(self.logs) > self.max_log_lines:
            self.log_scroll_offset = len(self.logs) - self.max_log_lines
    
    def handle_scroll(self, y_change):
        """
        Handle scroll events in the log window
        
        Args:
            y_change: Scroll direction and amount (positive = scroll up)
        """
        if len(self.logs) <= self.max_log_lines:
            return
        
        self.log_scroll_offset -= y_change
        max_offset = len(self.logs) - self.max_log_lines
        self.log_scroll_offset = max(0, min(self.log_scroll_offset, max_offset))
    
    def get_visible_logs(self):
        """
        Get the currently visible log entries based on scroll offset
        
        Returns:
            List of (text, color) tuples for visible logs
        """
        if len(self.logs) <= self.max_log_lines:
            return self.logs
        
        start = self.log_scroll_offset
        end = start + self.max_log_lines
        return self.logs[start:end]
    
    def clear(self):
        """Clear all logs"""
        self.logs = []
        self.log_scroll_offset = 0
    
    def get_all_logs(self):
        """
        Get all logs for saving
        
        Returns:
            List of all (text, color) tuples
        """
        return self.logs
    
    def load_logs(self, logs_data):
        """
        Load logs from saved data
        
        Args:
            logs_data: List of (text, color) tuples or (text, list) tuples
        """
        # Handle both tuple colors and list colors from JSON
        self.logs = [(t, tuple(c) if isinstance(c, list) else c) for t, c in logs_data]
        
        # Restore scroll position to show latest logs
        if len(self.logs) > self.max_log_lines:
            self.log_scroll_offset = len(self.logs) - self.max_log_lines
        else:
            self.log_scroll_offset = 0
    
    def can_scroll_up(self):
        """Check if scrolling up is possible"""
        return self.log_scroll_offset > 0
    
    def can_scroll_down(self):
        """Check if scrolling down is possible"""
        return len(self.logs) > self.max_log_lines and \
               self.log_scroll_offset < len(self.logs) - self.max_log_lines
