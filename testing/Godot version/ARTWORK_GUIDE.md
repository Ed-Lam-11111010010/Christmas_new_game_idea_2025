# City Rogue - Artwork Guide

## 🎨 Current Status & What You Can Do

Your game now shows **one emoji per building** (centered for 2x2 buildings). To make it look like the reference images (isometric city builders), you have several options:

---

## Option 1: Use Sprite Assets (Recommended)

### Where to Find Isometric Building Sprites

**Free Resources:**

1. **OpenGameArt.org**
   - Search: "isometric buildings"
   - URL: https://opengameart.org/
   - License: Check each asset (usually CC0 or CC-BY)
   - Good for: Complete building sets

2. **Kenney Assets**
   - URL: https://kenney.nl/assets
   - Search: "City Kit" or "Isometric"
   - License: CC0 (Public Domain)
   - Example: https://kenney.nl/assets/isometric-city
   - **Highly Recommended** - Professional quality, free!

3. **itch.io Asset Packs**
   - URL: https://itch.io/game-assets/tag-isometric
   - Many free and paid options
   - Search: "isometric city" or "pixel art buildings"

4. **Quaternius**
   - URL: https://quaternius.com/
   - Free low-poly 3D models you can render as sprites
   - License: CC0

**Paid Resources (High Quality):**

1. **GraphicRiver**
   - URL: https://graphicriver.net/
   - Search: "isometric building sprites"
   - Price: $5-$50 per pack

2. **Unity Asset Store**
   - Many 2D sprite packs work in Godot
   - Search: "2D isometric city"

### How to Implement Sprites in Your Game

Once you have sprite assets (PNG files):

1. **Organize your assets:**
   ```
   Godot version/
   └── assets/
       └── buildings/
           ├── house.png
           ├── office.png
           ├── power_plant.png
           ├── park.png
           └── ... (etc)
   ```

2. **Update game.gd to load sprites:**
   
   Add at the top of your script:
   ```gdscript
   var building_sprites: Dictionary = {}
   ```

   Add in `_ready()` function:
   ```gdscript
   func _ready():
       # ... existing code ...
       load_building_sprites()
   
   func load_building_sprites():
       building_sprites[1] = load("res://assets/buildings/house.png")
       building_sprites[2] = load("res://assets/buildings/office.png")
       building_sprites[3] = load("res://assets/buildings/power_plant.png")
       building_sprites[4] = load("res://assets/buildings/park.png")
       building_sprites[5] = load("res://assets/buildings/apartment.png")
       building_sprites[6] = load("res://assets/buildings/shop.png")
       building_sprites[7] = load("res://assets/buildings/road.png")
       building_sprites[8] = load("res://assets/buildings/bridge.png")
       building_sprites[9] = load("res://assets/buildings/garden.png")
       building_sprites[10] = load("res://assets/buildings/factory.png")
       building_sprites[11] = load("res://assets/buildings/mall.png")
       building_sprites[12] = load("res://assets/buildings/enhanced_park.png")
       building_sprites[13] = load("res://assets/buildings/botanical_garden.png")
   ```

3. **Replace the emoji drawing with sprite drawing:**
   
   In `draw_grid()` function, replace the emoji drawing section with:
   ```gdscript
   # Instead of:
   # draw_string(ThemeDB.fallback_font, text_pos, symbol, ...)
   
   # Use:
   if building_sprites.has(b_id):
       var sprite = building_sprites[b_id]
       var sprite_size = sprite.get_size() * zoom_level
       var sprite_pos = screen_pos + center_offset - sprite_size / 2
       draw_texture_rect(sprite, Rect2(sprite_pos, sprite_size), false)
   else:
       # Fallback to emoji if no sprite
       draw_string(ThemeDB.fallback_font, text_pos, symbol, ...)
   ```

---

## Option 2: AI-Generated Sprites

Use AI tools to generate building sprites:

1. **DALL-E 3 / Midjourney / Stable Diffusion**
   - Prompt example: "isometric pixel art house building sprite, transparent background, 64x64, game asset"
   - Prompt example: "isometric low poly office building, top-down view, game sprite, clean lines"

2. **Bing Image Creator** (Free)
   - URL: https://www.bing.com/images/create
   - Same prompts as above

3. **Remove.bg**
   - URL: https://remove.bg/
   - Remove backgrounds from generated images

### Tips for AI Generation:
- Generate at 512x512 or 1024x1024, then scale down
- Request "transparent background" or "white background" (easier to remove)
- Use keywords: "isometric", "pixel art", "game sprite", "clean"
- Be specific: "small house", "power plant with smokestack"

---

## Option 3: Create Your Own (Pixel Art)

### Tools:

1. **Aseprite** (Paid - $20, Best)
   - URL: https://www.aseprite.org/
   - Industry standard for pixel art
   - Export directly to PNG

2. **Piskel** (Free, Online)
   - URL: https://www.piskelapp.com/
   - Browser-based pixel art editor

3. **GIMP** (Free)
   - URL: https://www.gimp.org/
   - General image editor, can do pixel art

### Tutorial Resources:

- **YouTube**: Search "isometric pixel art building tutorial"
- **Recommended Channel**: "MortMort" - Great pixel art tutorials
- **PixelJoint.com**: Community with tutorials and examples

### Basic Process:

1. Start with a 64x64 canvas (for 2x2 buildings)
2. Use a limited color palette (5-10 colors per building)
3. Draw from an isometric perspective (30° angle)
4. Add shading for depth
5. Export as PNG with transparency

---

## Option 4: Use TileMap & Tilesets (Best for Performance)

Instead of drawing each tile individually, use Godot's TileMap:

### Benefits:
- Much better performance
- Built-in collision
- Easier to manage

### Setup:

1. Create a tileset image with all your buildings in a grid
2. In Godot: Create a TileSet resource
3. Add TileMap node to your scene
4. Paint tiles instead of drawing manually

### Tutorial:
- Godot Docs: https://docs.godotengine.org/en/stable/tutorials/2d/using_tilemaps.html

---

## Quick Win: Improve Current Look (No Assets Needed)

You can make the current emoji version look better:

### 1. Add Shadows & Depth

In `draw_grid()`, before drawing the main rect:
```gdscript
# Shadow
var shadow_offset = Vector2(2, 2) * zoom_level
draw_rect(Rect2(screen_pos + shadow_offset, Vector2(tile_size, tile_size)), Color(0, 0, 0, 0.3))

# Main tile
draw_rect(Rect2(screen_pos, Vector2(tile_size, tile_size)), color)
```

### 2. Add Gradient/Texture Effect

```gdscript
# Instead of solid color, add a gradient
var gradient_color = color.lightened(0.2)
draw_rect(Rect2(screen_pos, Vector2(tile_size, tile_size/2)), gradient_color)
draw_rect(Rect2(screen_pos + Vector2(0, tile_size/2), Vector2(tile_size, tile_size/2)), color)
```

### 3. Better Grid Lines

```gdscript
# Thicker, more visible grid
var grid_color = Color(0.2, 0.2, 0.2, 0.5)
draw_rect(Rect2(screen_pos, Vector2(tile_size, tile_size)), grid_color, false, 2)
```

### 4. Add Building Highlights

When buildings are connected/active:
```gdscript
if Vector2i(r, c) in active_buildings:
    # Add a subtle glow
    draw_rect(Rect2(screen_pos, Vector2(tile_size, tile_size)), Color(1, 1, 0, 0.2))
```

---

## Recommended Approach for Your Game

**Phase 1 (Quick - Do Now):**
1. ✅ Fix 2x2 emoji rendering (already done!)
2. Add shadows and better grid lines (5 minutes)
3. Improve empty land color (already done!)

**Phase 2 (Medium - This Week):**
1. Download Kenney's Isometric City pack (FREE)
2. Import sprites into Godot
3. Replace emojis with sprites (30 minutes)

**Phase 3 (Long-term - Future):**
1. Convert to TileMap for better performance
2. Add animations (smoke from factories, etc.)
3. Add particle effects

---

## Example: Kenney Asset Integration

1. **Download**: https://kenney.nl/assets/isometric-city
2. **Extract** PNG files to `assets/buildings/`
3. **Rename** files to match your buildings:
   - `house_typeA.png` → `house.png`
   - `office_large.png` → `office.png`
4. **Add to game.gd** as shown in Option 1
5. **Test** - should work immediately!

---

## Need Help?

- **Godot Community Discord**: Ask for asset recommendations
- **Reddit r/godot**: Great for asset discovery
- **itch.io Devlogs**: Many developers share free assets

## Style Matching Your Reference Images

Your reference images show:
1. **Isometric perspective** (30° angle view)
2. **Detailed building sprites** with roofs, windows, doors
3. **Roads with markings** and street details
4. **Shadows** underneath buildings
5. **Varied building heights** (tall skyscrapers, small houses)

To match this style:
- Use **Kenney's City Kit** (closest match, free)
- Or search **"SimCity 4 style sprites"** on OpenGameArt
- Or generate with AI: "isometric detailed city building sprite, similar to SimCity, game asset"

---

Good luck! Start with Kenney assets - they're free, high quality, and perfect for your game! 🎨
