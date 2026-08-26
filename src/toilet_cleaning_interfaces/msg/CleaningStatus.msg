# Cleaning state values. Keep these aligned with CleaningState in the manager.
uint8 IDLE=0
uint8 DETECT_LID=1
uint8 OPEN_LID=2
uint8 APPLY_BLEACH=3
uint8 BRUSH_CLEAN=4
uint8 RINSE=5
uint8 FINISH=6
uint8 DONE=7
uint8 ERROR=8

# Time at which this status was produced.
builtin_interfaces/Time stamp

# One of the state constants above.
uint8 state

# Stable state name for display and diagnostics, for example "BRUSH_CLEAN".
string state_name

# Overall progress in the inclusive range 0.0 to 1.0.
float32 progress

# True while a cleaning goal is active.
bool is_running

# Human-readable detail for logs and the UI.
string message
