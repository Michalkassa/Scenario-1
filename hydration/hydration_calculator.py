from enum import Enum

# | ----------------------- | ------ | ------------------- |
# | Body Weight             | BW     | kg                  |
# | Height                  | H      | cm                  |
# | Physical Activity Level | PA     | activity multiplier |
# | Exercise Duration       | D_ex   | hours               |
# | Ambient Temperature     | T      | °C                  |
# | Relative Humidity       | RH     | %                   |

# ```
# Sedentary = 0.4
# Light = 0.6
# Moderate = 1.0
# Vigorous = 1.4
# Elite = 2.0
# ```

class ActivityLevel(Enum):
    SEDENTARY = 0.4
    LIGHT = 0.6
    MODERATE = 1.0
    VIGOROUS = 1.4
    ELITE = 2.0

def calculate_goal(BW : int,H : int,PA : ActivityLevel,D_ex : int,T : float, RH : float) -> int:
    part1 = (0.033 * BW) + (0.25 * PA.value * D_ex)
    part2 = (0.00781 * pow(H, 0.725) * pow(BW,0.425)) / 1.9
    part3 = 1 + 0.02 * (T-20) + 0.005 * RH
    return part1 * part2 * part3