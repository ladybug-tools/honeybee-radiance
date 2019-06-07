frit = '''
void glass glass_alt_mat
0
0
3 0.96 0.96 0.96

void brightfunc glass_angular_effect
2 A1+(1-A1) (exp(-5.85 Rdot)-0.00287989916)
0
1 0.08

glass_angular_effect mirror glass_mat
1 glass_alt_mat
0
3 1 1 1
'''


microshade = """
void glass microshade_air
0
0
4 1 1 1 1
void plastic microshade_metal
0
0
5 0.1 0.1 0.1 0.017 0.005


void mixfunc microshade_a_mat
4    microshade_air microshade_metal trans microshade_a.cal
0
1  0

"""

metal_cone = """
void metal new_wall 0 0 5 0.000 0.000 0.000 0.950 0.000
new_wall cone floor_0_0_0
0
0
8
-77.3022 -78.4625 415.900
-81.9842 -78.9436 420.900
10 20
"""
