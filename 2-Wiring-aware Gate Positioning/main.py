class coord:
    def __init__(self, x, y):
        self.x, self.y = x, y

class Gate:
    def __init__(self, id, width, height):
        self.x = self.y = 0
        self.id, self.w, self.h = id, width, height
        self.pins, self.connections = {}, {}
        self.num, self.done = 0, False

    def add_pin(self, id, x, y):
        self.pins[id] = coord(x, y)

    def add_wire(self, id, other_gate, other_pin):
        self.connections.setdefault(other_gate, []).append((id, other_pin))

gates : list[Gate]=[]
wirings =[]
total_wire_length = 0
with open('input.txt','r') as file:
    for line in file:
        input=line.split()
        if input[0][0]=='g':
            new_gate=Gate(int(input[0][1:]),int(input[1]),int(input[2]))
            gates.append(new_gate)
        if input[0]=='pins':
            gate_id=input[1][1:]
            pin_coord=input[2:]
            input_pin_id=1
            for i in range(0,len(pin_coord),2):
                x,y= int(pin_coord[i]),int(pin_coord[i+1])
                gates[int(gate_id)-1].add_pin(input_pin_id,x,y)
                input_pin_id+=1
        if input[0]=='wire':
            gate1, pin1 = input[1].split('.')
            gate2, pin2 = input[2].split('.')
            gate1_id=int(gate1[1:])
            gate2_id=int(gate2[1:])
            pin1_id=int(pin1[1:])
            pin2_id=int(pin2[1:])
            wirings.append((gate1_id,gate2_id))
            gates[(gate1_id)-1].add_wire(pin1_id,gate2_id,pin2_id)
            gates[(gate2_id)-1].add_wire(pin2_id,gate1_id,pin1_id)
            gates[(gate2_id)-1].num+=1
            gates[(gate1_id)-1].num+=1

gates.sort(key=lambda x : x.num,reverse=True)

for gate in gates:
    gate.connections=dict(sorted(gate.connections.items(),key=lambda item: len(item[1]),reverse=True))

def wirelength(gate1,gate2):
    length=0
    for pin1,pin2 in gate1.connections[gate2.id]:
        pin1x=gate1.x+gate1.pins[pin1].x
        pin1y=gate1.y+gate1.pins[pin1].y
        pin2x=gate2.x+gate2.pins[pin2].x
        pin2y=gate2.y+gate2.pins[pin2].y        
        length += abs(pin1x-pin2x) + abs(pin1y- pin2y)
    return length

low=0
up=1
left=2
right=3

def check(pivot, gate, minWireLength, x, y, minlevel, level, new_gate):
    gate.x, gate.y = x, y
    length = wirelength(pivot, gate)
    if length < minWireLength:
        return length, coord(x, y), gate, level
    return minWireLength, new_gate, gate, minlevel

def place_gate(gate, pivot:Gate, levels):
    if gate.done:
        return
    global total_wire_length,low,up,left,right  
    minWireLength = float('inf')
    new_gate=coord(None,None)
    minLevel=None
    gate.done=True
    for level in levels:    #O(G) worst case 
        if level[up]!=None and level[low]!=None and level[up]-level[low] >= gate.h:
            # right-side-top
            x,y=level[right],level[up] - gate.h
            minWireLength,new_gate,gate,minLevel=check(pivot,gate,minWireLength,x,y,minLevel,level,new_gate)
            # right-side-bottom
            x,y=level[right],level[low]
            minWireLength,new_gate,gate,minLevel=check(pivot,gate,minWireLength,x,y,minLevel,level,new_gate)
            # left-side-top
            x,y=level[left]-gate.w,level[up] - gate.h
            minWireLength,new_gate,gate,minLevel=check(pivot,gate,minWireLength,x,y,minLevel,level,new_gate)
            # left-side-bottom
            x,y=level[left]-gate.w,level[low]
            minWireLength,new_gate,gate,minLevel=check(pivot,gate,minWireLength,x,y,minLevel,level,new_gate)

        # place above the top level
        elif level[up]==None:
            # top left corner of pivot
            x,y=pivot.x,level[low]
            minWireLength,new_gate,gate,minLevel=check(pivot,gate,minWireLength,x,y,minLevel,level,new_gate)  
            #top right corner of pivot
            x,y=pivot.x+pivot.w-gate.w,level[low]
            minWireLength,new_gate,gate,minLevel=check(pivot,gate,minWireLength,x,y,minLevel,level,new_gate)  

        # place below bottom level
        elif level[low]==None:
            #bottom left corner of pivot
            x,y=pivot.x,level[up]-gate.h
            minWireLength,new_gate,gate,minLevel=check(pivot,gate,minWireLength,x,y,minLevel,level,new_gate)  
            # bottom right corner of pivot
            x,y=pivot.x + pivot.w - gate.w,level[up]-gate.h
            minWireLength,new_gate,gate,minLevel=check(pivot,gate,minWireLength,x,y,minLevel,level,new_gate)  
    gate.x,gate.y=new_gate.x,new_gate.y 
    #updating left and right
    if minLevel[up]==None:
        minLevel[up]=gate.y+gate.h
        minLevel[left]=gate.x
        minLevel[right]=gate.x+gate.w
        levels.append([minLevel[up],None,None,None])
        
    elif minLevel[low]==None:
        minLevel[low]=gate.y
        minLevel[left]=gate.x
        minLevel[right]=gate.x + gate.w
        levels.append([None,minLevel[low],None,None])
        
    else:
        if gate.x==minLevel[right]:
            minLevel[right]=gate.x+gate.w
        else:
            minLevel[left]=gate.x

def find(gate_id): return next((gate for gate in gates if gate.id == gate_id), None)

def place_connected_gates(pivot, connected_gates, levels):
    connected_gates.append(pivot)
    for gate_id in pivot.connections:
        gate = find(gate_id)    #O(g)
        if not gate.done:
            place_gate(gate, pivot, levels)
            place_connected_gates(gate, connected_gates, levels)
    return connected_gates

def TotalLength(): return sum(wirelength(find(gate1_id), find(gate2_id)) for gate1_id, gate2_id in wirings)

components=[]
# start
for gate in gates:  #O(G)
    if not gate.done:
        gate.done=True
        min_x=float('inf')
        max_x=float('-inf')
        min_y=float('inf')
        max_y=float('-inf')
        #[low,high,left,right]
        levels=[[0,gate.h,0,gate.w],[None,0,None,None],[gate.h,None,None,None]]
        connected_gates=place_connected_gates(pivot=gate,connected_gates=[],levels=levels)
        for gate in connected_gates:
            min_x=min(min_x,gate.x)
            min_y=min(min_y,gate.y)
            max_x=max(max_x,gate.x+gate.w)
            max_y=max(max_y,gate.y+gate.h)
        components.append([min_x,min_y,max_x,max_y,connected_gates])

prev_x = 0
max_y = float('-inf')

for component in components:
    offset_x, offset_y = component[0], component[1]
    for gate in component[4]:
        gate.x += prev_x - offset_x
        gate.y -= offset_y
    max_y = max(max_y, component[3] - offset_y)
    prev_x += component[2] - offset_x

gates.sort(key=lambda x: x.id)

coordi = [max(gate.x + gate.w for gate in gates), max(gate.y + gate.h for gate in gates)]
       
Wiring = TotalLength()

print(f"Bounding-Box: ({coordi[0]}, {coordi[1]})")
for gate in gates:
    print(f"{gate.id} {gate.x} {gate.y}")
print(f"Total wire length: {Wiring}")

with open("output.txt", "w") as file:
    file.write(f"bounding_box {prev_x} {max_y}\n")
    for gate in gates:
        file.write(f"g{gate.id} {gate.x} {gate.y}\n")
    file.write(f"{Wiring}",)
