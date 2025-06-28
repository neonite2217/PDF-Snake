PDF_FILE_TEMPLATE = """
%PDF-1.6

% Root
1 0 obj
<<
  /AcroForm <<
    /Fields [ ###FIELD_LIST### ]
  >>
  /Pages 2 0 R
  /OpenAction 17 0 R
  /Type /Catalog
>>
endobj

2 0 obj
<<
  /Count 1
  /Kids [
    16 0 R
  ]
  /Type /Pages
>>

%% Annots Page 1 (also used as overall fields list)
21 0 obj
[
  ###FIELD_LIST###
]
endobj

###FIELDS###

%% Page 1
16 0 obj
<<
  /Annots 21 0 R
  /Contents 3 0 R
  /CropBox [
    0.0
    0.0
    612.0
    792.0
  ]
  /MediaBox [
    0.0
    0.0
    612.0
    792.0
  ]
  /Parent 2 0 R
  /Resources <<
  >>
  /Rotate 0
  /Type /Page
>>
endobj

3 0 obj
<< >>
stream
endstream
endobj

17 0 obj
<<
  /JS 42 0 R
  /S /JavaScript
>>
endobj


42 0 obj
<< >>
stream

// Hacky wrapper to work with a callback instead of a string 
function setInterval(cb, ms) {
	evalStr = "(" + cb.toString() + ")();";
	return app.setInterval(evalStr, ms);
}

var rand_seed = Date.now() % 2147483647;
function rand() {
	return rand_seed = rand_seed * 16807 % 2147483647;
}

var TICK_INTERVAL = 150;

// Globals
var pixel_fields = [];
var field = [];
var score = 0;
var game_running = false;
var interval = 0;

// Snake data
var snake = [];
var direction = { x: 1, y: 0 }; // Start moving right
var food = { x: 0, y: 0 };

function spawn_food() {
	var attempts = 0;
	do {
		food.x = Math.floor(rand() / 2147483647 * ###GRID_WIDTH###);
		food.y = Math.floor(rand() / 2147483647 * ###GRID_HEIGHT###);
		attempts++;
	} while (is_snake_at(food.x, food.y) && attempts < 100);
}

function is_snake_at(x, y) {
	for (var i = 0; i < snake.length; i++) {
		if (snake[i].x === x && snake[i].y === y) {
			return true;
		}
	}
	return false;
}

function set_controls_visibility(state) {
	this.getField("T_input").hidden = !state;
	this.getField("B_up").hidden = !state;
	this.getField("B_down").hidden = !state;
	this.getField("B_left").hidden = !state;
	this.getField("B_right").hidden = !state;
}

function game_init() {
	// Initialize snake in the middle
	snake = [
		{ x: Math.floor(###GRID_WIDTH### / 2), y: Math.floor(###GRID_HEIGHT### / 2) },
		{ x: Math.floor(###GRID_WIDTH### / 2) - 1, y: Math.floor(###GRID_HEIGHT### / 2) },
		{ x: Math.floor(###GRID_WIDTH### / 2) - 2, y: Math.floor(###GRID_HEIGHT### / 2) }
	];
	
	direction = { x: 1, y: 0 };
	
	// Gather references to pixel field objects
	// and initialize game state
	for (var x = 0; x < ###GRID_WIDTH###; ++x) {
		pixel_fields[x] = [];
		field[x] = [];
		for (var y = 0; y < ###GRID_HEIGHT###; ++y) {
			pixel_fields[x][y] = this.getField(`P_${x}_${y}`);
			field[x][y] = 0;
		}
	}

	score = 0;
	game_running = true;
	
	spawn_food();

	// Start timer
	interval = setInterval(game_tick, TICK_INTERVAL);

	// Hide start button
	this.getField("B_start").hidden = true;

	// Show input box and controls
	set_controls_visibility(true);
	
	draw_updated_score();
}

function game_over() {
	game_running = false;
	app.clearInterval(interval);
	app.alert(`Game over! Your snake was ${snake.length} blocks long!\\nScore: ${score}\\nRefresh to restart.`);
}

function handle_input(event) {
	if (!game_running) return;
	
	// Check last character typed 
	var inputField = this.getField("T_input");
	var inputValue = inputField.value;
	var lastChar = "";
	
	if (inputValue && inputValue.length > 0) {
		lastChar = inputValue.charAt(inputValue.length - 1);
		// Clear the field to prevent buildup
		inputField.value = "";
	}
	
	switch (lastChar) {
		case '8': // Up arrow equivalent
		case 'w':
		case 'W':
			move_up(); 
			break;
		case '4': // Left arrow equivalent  
		case 'a':
		case 'A':
			move_left(); 
			break;
		case '2': // Down arrow equivalent
		case 's':
		case 'S':
			move_down(); 
			break;
		case '6': // Right arrow equivalent
		case 'd':
		case 'D':
			move_right(); 
			break;
	}
}

function move_up() {
	if (direction.y !== 1) { // Can't reverse
		direction = { x: 0, y: -1 };
	}
}

function move_down() {
	if (direction.y !== -1) { // Can't reverse
		direction = { x: 0, y: 1 };
	}
}

function move_left() {
	if (direction.x !== 1) { // Can't reverse
		direction = { x: -1, y: 0 };
	}
}

function move_right() {
	if (direction.x !== -1) { // Can't reverse
		direction = { x: 1, y: 0 };
	}
}

function update_snake() {
	if (!game_running) return;
	
	// Calculate new head position
	var head = snake[0];
	var new_head = {
		x: head.x + direction.x,
		y: head.y + direction.y
	};
	
	// Check wall collision
	if (new_head.x < 0 || new_head.x >= ###GRID_WIDTH### || 
		new_head.y < 0 || new_head.y >= ###GRID_HEIGHT###) {
		game_over();
		return;
	}
	
	// Check self collision
	if (is_snake_at(new_head.x, new_head.y)) {
		game_over();
		return;
	}
	
	// Add new head
	snake.unshift(new_head);
	
	// Check food collision
	if (new_head.x === food.x && new_head.y === food.y) {
		score += 10;
		draw_updated_score();
		spawn_food();
	} else {
		// Remove tail if no food eaten
		snake.pop();
	}
}

function draw_updated_score() {
	this.getField("T_score").value = `Score: ${score} | Length: ${snake.length}`;
}

function set_pixel(x, y, color) {
	if (x < 0 || y < 0 || x >= ###GRID_WIDTH### || y >= ###GRID_HEIGHT###) {
		return;
	}
	
	// Flip Y coordinate for display
	var field_obj = pixel_fields[x][###GRID_HEIGHT### - 1 - y];
	
	if (color === 0) {
		field_obj.hidden = true;
	} else {
		field_obj.hidden = false;
		// We can't easily change colors in PDF forms, so we'll use visibility
		// Green for snake (visible), Red for food (visible but different field)
	}
}

function clear_field() {
	for (var x = 0; x < ###GRID_WIDTH###; ++x) {
		for (var y = 0; y < ###GRID_HEIGHT###; ++y) {
			set_pixel(x, y, 0);
		}
	}
}

function draw_snake() {
	for (var i = 0; i < snake.length; i++) {
		set_pixel(snake[i].x, snake[i].y, 1);
	}
}

function draw_food() {
	// For food, we'll make it blink by alternating visibility
	var blink = Math.floor(Date.now() / 300) % 2;
	if (blink) {
		set_pixel(food.x, food.y, 2);
	}
}

function draw() {
	clear_field();
	draw_snake();
	draw_food();
}

function game_tick() {
	update_snake();
	draw();
}

// Hide controls to start with
set_controls_visibility(false);

// Zoom to fit (on FF)
app.execMenuItem("FitPage");

endstream
endobj


18 0 obj
<<
  /JS 43 0 R
  /S /JavaScript
>>
endobj


43 0 obj
<< >>
stream



endstream
endobj

trailer
<<
  /Root 1 0 R
>>

%%EOF
"""

PLAYING_FIELD_OBJ = """
###IDX### obj
<<
  /FT /Btn
  /Ff 1
  /MK <<
    /BG [
      0.9
    ]
    /BC [
      0 0 0
    ]
  >>
  /Border [ 0 0 2 ]
  /P 16 0 R
  /Rect [
    ###RECT###
  ]
  /Subtype /Widget
  /T (playing_field)
  /Type /Annot
>>
endobj
"""

PIXEL_OBJ = """
###IDX### obj
<<
  /FT /Btn
  /Ff 1
  /MK <<
    /BG [
      ###COLOR###
    ]
    /BC [
      0.3 0.3 0.3
    ]
  >>
  /Border [ 0 0 1 ]
  /P 16 0 R
  /Rect [
    ###RECT###
  ]
  /Subtype /Widget
  /T (P_###X###_###Y###)
  /Type /Annot
>>
endobj
"""

BUTTON_AP_STREAM = """
###IDX### obj
<<
  /BBox [ 0.0 0.0 ###WIDTH### ###HEIGHT### ]
  /FormType 1
  /Matrix [ 1.0 0.0 0.0 1.0 0.0 0.0]
  /Resources <<
    /Font <<
      /HeBo 10 0 R
    >>
    /ProcSet [ /PDF /Text ]
  >>
  /Subtype /Form
  /Type /XObject
>>
stream
q
0.75 g
0 0 ###WIDTH### ###HEIGHT### re
f
Q
q
1 1 ###WIDTH### ###HEIGHT### re
W
n
BT
/HeBo 10 Tf
0 g
###TEXT_X### 8 Td
(###TEXT###) Tj
ET
Q
endstream
endobj
"""

BUTTON_OBJ = """
###IDX### obj
<<
  /A <<
	  /JS ###SCRIPT_IDX### R
	  /S /JavaScript
	>>
  /AP <<
    /N ###AP_IDX### R
  >>
  /F 4
  /FT /Btn
  /Ff 65536
  /MK <<
    /BG [
      0.75
    ]
    /CA (###LABEL###)
  >>
  /P 16 0 R
  /Rect [
    ###RECT###
  ]
  /Subtype /Widget
  /T (###NAME###)
  /Type /Annot
>>
endobj
"""

TEXT_OBJ = """
###IDX### obj
<<
	/AA <<
		/K <<
			/JS ###SCRIPT_IDX### R
			/S /JavaScript
		>>
		/F <<
			/JS ###SCRIPT_IDX### R
			/S /JavaScript
		>>
	>>
	/F 4
	/FT /Tx
	/MK <<
	>>
	/MaxLen 0
	/P 16 0 R
	/Rect [
		###RECT###
	]
	/Subtype /Widget
	/T (###NAME###)
	/V (###LABEL###)
	/Type /Annot
>>
endobj
"""

STREAM_OBJ = """
###IDX### obj
<< >>
stream
###CONTENT###
endstream
endobj
"""

# Game configuration
PX_SIZE = 18
GRID_WIDTH = 20
GRID_HEIGHT = 20
GRID_OFF_X = 150
GRID_OFF_Y = 250

fields_text = ""
field_indexes = []
obj_idx_ctr = 50

def add_field(field):
	global fields_text, field_indexes, obj_idx_ctr
	fields_text += field
	field_indexes.append(obj_idx_ctr)
	obj_idx_ctr += 1

# Playing field outline
playing_field = PLAYING_FIELD_OBJ
playing_field = playing_field.replace("###IDX###", f"{obj_idx_ctr} 0")
playing_field = playing_field.replace("###RECT###", f"{GRID_OFF_X-2} {GRID_OFF_Y-2} {GRID_OFF_X+GRID_WIDTH*PX_SIZE+2} {GRID_OFF_Y+GRID_HEIGHT*PX_SIZE+2}")
add_field(playing_field)

# Create pixel grid
for x in range(GRID_WIDTH):
	for y in range(GRID_HEIGHT):
		pixel = PIXEL_OBJ
		pixel = pixel.replace("###IDX###", f"{obj_idx_ctr} 0")
		
		# Different colors for variety
		if (x + y) % 2 == 0:
			pixel = pixel.replace("###COLOR###", "0.2 0.6 0.2")  # Green
		else:
			pixel = pixel.replace("###COLOR###", "0.1 0.5 0.1")  # Darker green
			
		pixel = pixel.replace("###RECT###", f"{GRID_OFF_X+x*PX_SIZE} {GRID_OFF_Y+y*PX_SIZE} {GRID_OFF_X+x*PX_SIZE+PX_SIZE} {GRID_OFF_Y+y*PX_SIZE+PX_SIZE}")
		pixel = pixel.replace("###X###", f"{x}")
		pixel = pixel.replace("###Y###", f"{y}")
		add_field(pixel)

def add_button(label, name, x, y, width, height, js):
	script = STREAM_OBJ
	script = script.replace("###IDX###", f"{obj_idx_ctr} 0")
	script = script.replace("###CONTENT###", js)
	add_field(script)

	ap_stream = BUTTON_AP_STREAM
	ap_stream = ap_stream.replace("###IDX###", f"{obj_idx_ctr} 0")
	ap_stream = ap_stream.replace("###TEXT###", label)
	ap_stream = ap_stream.replace("###WIDTH###", f"{width}")
	ap_stream = ap_stream.replace("###HEIGHT###", f"{height}")
	# Center text in button
	text_x = max(5, (width - len(label) * 6) // 2)
	ap_stream = ap_stream.replace("###TEXT_X###", f"{text_x}")
	add_field(ap_stream)

	button = BUTTON_OBJ
	button = button.replace("###IDX###", f"{obj_idx_ctr} 0")
	button = button.replace("###SCRIPT_IDX###", f"{obj_idx_ctr-2} 0")
	button = button.replace("###AP_IDX###", f"{obj_idx_ctr-1} 0")
	button = button.replace("###LABEL###", label)
	button = button.replace("###NAME###", name if name else f"B_{obj_idx_ctr}")
	button = button.replace("###RECT###", f"{x} {y} {x + width} {y + height}")
	add_field(button)

def add_text(label, name, x, y, width, height, js):
	script = STREAM_OBJ
	script = script.replace("###IDX###", f"{obj_idx_ctr} 0")
	script = script.replace("###CONTENT###", js)
	add_field(script)

	text = TEXT_OBJ
	text = text.replace("###IDX###", f"{obj_idx_ctr} 0")
	text = text.replace("###SCRIPT_IDX###", f"{obj_idx_ctr-1} 0")
	text = text.replace("###LABEL###", label)
	text = text.replace("###NAME###", name)
	text = text.replace("###RECT###", f"{x} {y} {x + width} {y + height}")
	add_field(text)

# Control buttons arranged in cross pattern
btn_size = 40
btn_spacing = 50
center_x = GRID_OFF_X + (GRID_WIDTH * PX_SIZE) // 2 - btn_size // 2
center_y = GRID_OFF_Y - 120

add_button("^", "B_up", center_x, center_y + btn_spacing, btn_size, btn_size, "move_up();")
add_button("v", "B_down", center_x, center_y - btn_spacing, btn_size, btn_size, "move_down();")
add_button("<", "B_left", center_x - btn_spacing, center_y, btn_size, btn_size, "move_left();")
add_button(">", "B_right", center_x + btn_spacing, center_y, btn_size, btn_size, "move_right();")

# Start button
add_button("Start Snake Game", "B_start", 
           GRID_OFF_X + (GRID_WIDTH*PX_SIZE)//2 - 75, 
           GRID_OFF_Y + (GRID_HEIGHT*PX_SIZE)//2 - 25, 
           150, 50, "game_init();")

# Input field for keyboard controls - updated instructions
add_text(" ", "T_input",
         GRID_OFF_X, GRID_OFF_Y - 50, GRID_WIDTH*PX_SIZE, 30, "handle_input(event);")

# Score display - moved to top of grid
add_text("Score: 0 | Length: 3", "T_score", 
         GRID_OFF_X, GRID_OFF_Y + GRID_HEIGHT*PX_SIZE + 10, 
         GRID_WIDTH*PX_SIZE, 25, "")

# Generate final PDF
filled_pdf = PDF_FILE_TEMPLATE.replace("###FIELDS###", fields_text)
filled_pdf = filled_pdf.replace("###FIELD_LIST###", " ".join([f"{i} 0 R" for i in field_indexes]))
filled_pdf = filled_pdf.replace("###GRID_WIDTH###", f"{GRID_WIDTH}")
filled_pdf = filled_pdf.replace("###GRID_HEIGHT###", f"{GRID_HEIGHT}")

# Write to file
with open("snake_game.pdf", "w") as pdffile:
    pdffile.write(filled_pdf)

print("Snake game PDF generated successfully!")
print("File saved as: snake_game.pdf")
print(f"Grid size: {GRID_WIDTH}x{GRID_HEIGHT}")
print("Controls: Arrow keys or click the directional buttons")
print("Objective: Eat the blinking food to grow your snake!")
