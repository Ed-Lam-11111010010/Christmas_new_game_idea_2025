extends Node
class_name EventLogManager
## Manages event log messages for the game

const MAX_LOG_LINES: int = 5

var logs: Array = []  # Array of [text, color] pairs
var scroll_offset: int = 0

func _init(max_lines: int = MAX_LOG_LINES):
	pass

func log(text: String, color: Color = Color.WHITE) -> void:
	"""Add a new log entry"""
	logs.append([text, color])

func clear() -> void:
	"""Clear all logs"""
	logs.clear()
	scroll_offset = 0

func handle_scroll(delta: int) -> void:
	"""Handle scrolling through logs"""
	scroll_offset = clampi(scroll_offset + delta, 0, max(0, logs.size() - MAX_LOG_LINES))

func get_visible_logs() -> Array:
	"""Get the currently visible logs based on scroll offset"""
	var start_idx = max(0, logs.size() - MAX_LOG_LINES - scroll_offset)
	var end_idx = logs.size() - scroll_offset
	return logs.slice(start_idx, end_idx)

func get_all_logs() -> Array:
	"""Get all logs for saving"""
	return logs

func load_logs(serialized_logs: Array) -> void:
	"""Load logs from saved data"""
	logs.clear()
	for log_data in serialized_logs:
		if log_data is Array and log_data.size() >= 2:
			var text = log_data[0]
			var color_array = log_data[1]
			var color: Color
			if color_array is Array and color_array.size() >= 3:
				color = Color(color_array[0], color_array[1], color_array[2])
			else:
				color = Color.WHITE
			logs.append([text, color])
	scroll_offset = 0
