import json
import pandapower as pp

with open("simuladores/power_sim/data/ieee14_protecao.json") as f:
    data = json.load(f)

print(type(data["pandapower_net"]))  # Deve ser <class 'str'>
net = pp.from_json(data["pandapower_net"])
print(type(net))  # Deve ser <class 'pandapower.pandapowerNet'>
print(net.bus)
