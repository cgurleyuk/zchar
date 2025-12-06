



NMOS_SWEEP_TEMPLATE = """
* NMOS gm/Id Sweep
.lib '{model_path}' mos_tt

* Supply
Vds d 0 DC {vds}
Vgate g 0 DC 0
Vbs b 0 DC {vbs}

* Device under test
Xn1 d g 0 b {model_name} w={width} l={length} ng={ng} m={m}

* Analysis
.dc Vgate 0 {vgs_max} {vgs_step}

.control
save all @n.xn1.n{model_name}[ids] @n.xn1.n{model_name}[gm] @n.xn1.n{model_name}[gds] @n.xn1.n{model_name}[cgg]
run
* Save variables
* We save: Id, gm, gds, cgg
* Note: wrdata stores [X Val1 X Val2 X Val3 ...]
* Vectors: ids, gm, gds, cgg
wrdata {output_file} @n.xn1.n{model_name}[ids] @n.xn1.n{model_name}[gm] @n.xn1.n{model_name}[gds] @n.xn1.n{model_name}[cgg]
.endc
.end
"""

PMOS_SWEEP_TEMPLATE = """
* PMOS gm/Id Sweep
.lib '{model_path}' mos_tt

* Supply
Vds d 0 DC -{vds}
Vgate g 0 DC 0
Vbs b 0 DC {vbs}

* Device
Xp1 d g 0 b {model_name} w={width} l={length} ng={ng} m={m}

* Analysis
.dc Vgate 0 -{vgs_max} -{vgs_step}

.control
save all @n.xp1.n{model_name}[ids] @n.xp1.n{model_name}[gm] @n.xp1.n{model_name}[gds] @n.xp1.n{model_name}[cgg]
run
* Save variables: Id, gm, gds, cgg
wrdata {output_file} @n.xp1.n{model_name}[ids] @n.xp1.n{model_name}[gm] @n.xp1.n{model_name}[gds] @n.xp1.n{model_name}[cgg]
.endc
.end
"""
