# Pygame to Godot Migration Guide

This document explains how the Python/Pygame code was converted to GDScript/Godot.

## Core Concept Mappings

### Game Loop

**Pygame:**
```python
while True:
    for event in pygame.event.get():
        # Handle events
    
    screen.fill(BG_COLOR)
    # Draw everything
    pygame.display.flip()
    clock.tick(60)
```

**Godot:**
```gdscript
func _ready():
    # Initialize (runs once)
    pass

func _process(delta):
    # Update logic (runs every frame)
    queue_redraw()  # Request redraw

func _draw():
    # Rendering code
    pass

func _input(event):
    # Handle input events
    pass
```

### Data Structures

| Python | Godot GDScript | Notes |
|--------|----------------|-------|
| `list` / `[]` | `Array` | Similar syntax |
| `dict` / `{}` | `Dictionary` | Similar syntax |
| `tuple` / `()` | `Array` (immutable not enforced) | Use arrays |
| `None` | `null` | Keyword change |
| `True/False` | `true/false` | Lowercase |

### File I/O

**Python (JSON):**
```python
import json
with open("data.json", "r") as f:
    data = json.load(f)
```

**Godot (JSON):**
```gdscript
var file = FileAccess.open("res://data.json", FileAccess.READ)
if file:
    var json = JSON.new()
    var parse_result = json.parse(file.get_as_text())
    if parse_result == OK:
        var data = json.data
    file.close()
```

### Colors

**Pygame:**
```python
WHITE = (255, 255, 255)
RED = (220, 50, 50)
screen.fill(WHITE)
```

**Godot:**
```gdscript
const WHITE: Color = Color(1.0, 1.0, 1.0)  # 0-1 range
const RED: Color = Color(0.86, 0.2, 0.2)   # RGB / 255
draw_rect(rect, WHITE)
```

### Rendering

**Pygame (Blit-based):**
```python
screen.fill(BG_COLOR)
pygame.draw.rect(screen, color, rect)
text_surface = font.render("Hello", True, WHITE)
screen.blit(text_surface, (x, y))
```

**Godot (Immediate mode):**
```gdscript
func _draw():
    draw_rect(Rect2(pos, size), color)
    draw_string(font, position, "Hello", HORIZONTAL_ALIGNMENT_LEFT, -1, size, color)
```

### Input Handling

**Pygame:**
```python
for event in pygame.event.get():
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:  # Left click
            mx, my = event.pos
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
            # Handle space
```

**Godot:**
```gdscript
func _input(event):
    if event is InputEventMouseButton and event.pressed:
        if event.button_index == MOUSE_BUTTON_LEFT:
            var pos = event.position
    
    if event is InputEventKey and event.pressed:
        if event.keycode == KEY_SPACE:
            # Handle space
```

### Audio

**Pygame:**
```python
pygame.mixer.init()
sound = pygame.mixer.Sound("file.wav")
sound.set_volume(0.5)
sound.play()
```

**Godot:**
```gdscript
# Method 1: Preload
var sound = preload("res://sfx/file.wav")
var player = AudioStreamPlayer.new()
player.stream = sound
player.volume_db = linear_to_db(0.5)
player.play()

# Method 2: AudioStreamPlayer node in scene tree
$AudioPlayer.play()
```

## Specific Function Conversions

### Random Numbers

**Pygame:**
```python
import random
random.randint(0, 10)
random.choice([1, 2, 3])
```

**Godot:**
```gdscript
# In _ready():
randomize()  # Seed RNG

# Then:
randi_range(0, 10)  # Random int in range
randi() % array.size()  # Random index
```

### String Formatting

**Python:**
```python
f"Score: {score}"
f"Value: {value:+d}"  # +5, -3
"Text: %s, Num: %d" % (text, num)
```

**Godot:**
```gdscript
"Score: %d" % score
"Value: %+d" % value  # +5, -3
"Text: %s, Num: %d" % [text, num]
```

### Math Functions

**Python:**
```python
import math
max(a, b)
min(a, b)
abs(x)
int(x)
```

**Godot:**
```gdscript
max(a, b)
min(a, b)
abs(x)
int(x)
# Also: clampi(x, min, max), clampf(x, min, max)
```

### Grid/2D Coordinates

**Python (tuples):**
```python
pos = (r, c)
grid[r][c] = value
neighbors = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
```

**Godot (Vector2i):**
```gdscript
var pos = Vector2i(r, c)
grid[r][c] = value  # Still use arrays for grid
var neighbors = [
    Vector2i(r-1, c),
    Vector2i(r+1, c),
    Vector2i(r, c-1),
    Vector2i(r, c+1)
]
```

## Manager Classes

### Python Class

**Python:**
```python
class EventLogManager:
    def __init__(self, max_log_lines=5):
        self.logs = []
        self.max_lines = max_log_lines
    
    def log(self, text, color=(255, 255, 255)):
        self.logs.append([text, color])
```

**Godot:**
```gdscript
extends Node
class_name EventLogManager

const MAX_LOG_LINES: int = 5
var logs: Array = []

func _init(max_lines: int = MAX_LOG_LINES):
    pass

func log(text: String, color: Color = Color.WHITE):
    logs.append([text, color])
```

### Passing Methods as Callbacks

**Python:**
```python
def build(self, callback_func):
    callback_func("build")
    
# Usage:
manager.build(self.play_sound)
```

**Godot:**
```gdscript
func build(callback_func: Callable):
    callback_func.call("build")

# Usage:
manager.build(play_sound)
```

## Common Pitfalls

### 1. Array/Dictionary Access

❌ **Wrong:**
```gdscript
if (r, c) in network_map:  # Tuples don't work as keys
```

✅ **Correct:**
```gdscript
var key = Vector2i(r, c)
if network_map.has(key):
```

### 2. Integer Division

❌ **Wrong (Python behavior):**
```gdscript
var result = 5 / 2  # Result: 2.5 (float)
```

✅ **Correct (if you want int):**
```gdscript
var result = 5 / 2  # 2.5
var int_result = int(5 / 2)  # 2
# Or use integer division
var int_result = 5 // 2  # 2 (only in Godot 4.3+)
```

### 3. String Keys in Dictionaries

❌ **Wrong:**
```gdscript
var b_id = 5
var data = buildings[b_id]  # Error if keys are strings
```

✅ **Correct:**
```gdscript
var b_id = 5
var data = buildings[str(b_id)]  # Convert to string
```

### 4. File Paths

❌ **Wrong:**
```gdscript
var path = "data/game_data.json"
```

✅ **Correct:**
```gdscript
# For resources in project:
var path = "res://data/game_data.json"

# For user data (saves):
var path = "user://save_data.json"
```

### 5. Queue Redraw

❌ **Wrong:**
```gdscript
func _process(delta):
    # Modify state
    # Draw will use old state
```

✅ **Correct:**
```gdscript
func _process(delta):
    # Modify state
    queue_redraw()  # Request redraw with new state
```

## Performance Tips

1. **Use TileMap for large grids** instead of drawing each tile
2. **Minimize draw calls** - batch similar operations
3. **Cache font resources** instead of using ThemeDB.fallback_font repeatedly
4. **Use Nodes for UI** instead of manual drawing for complex interfaces
5. **Consider using Signals** instead of polling for events

## Additional Resources

- [GDScript Basics](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_basics.html)
- [Godot 2D Guide](https://docs.godotengine.org/en/stable/tutorials/2d/index.html)
- [Input Events](https://docs.godotengine.org/en/stable/tutorials/inputs/inputevent.html)
- [File System](https://docs.godotengine.org/en/stable/classes/class_fileaccess.html)
