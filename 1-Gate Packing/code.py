class Gate:
    def __init__(self, name, w, h):
        self.name = name
        self.w = w
        self.h = h
        self.coordinates = (0, 0)

    def __repr__(self):
        return f"Gate(name={self.name}, w={self.w}, h={self.h}, coordinates={self.coordinates})"

def sort_by_w(gate):
    return gate.w

class GatePlacer:
    def __init__(self, gate_list):
        self.gates = gate_list
        self.sp = []
        self.bounding_box = [0, 0]

    def place_gates(self):
        # Sort gates by width
        self.gates.sort(key=sort_by_w, reverse=True)

        # Place the first gate at the origin
        self.gates[0].coordinates = (0, 0)
        self.sp = [[(0, self.gates[0].h), (self.gates[0].w, self.gates[0].h)]]
        self.bounding_box = [self.gates[0].w, self.gates[0].h]

        # Place the remaining gates
        for idx in range(1, len(self.gates)):
            self.place_gate(idx)

        return self.gates, self.bounding_box

    def place_gate(self, idx):
        min_area = float('inf')
        chosen_position = None
        selected_idx = -1
        temp_area = self.bounding_box[:]

        # Find the best position in existing spaces
        for space_idx, space in enumerate(self.sp):
            available_width = space[1][0] - space[0][0]
            new_height = space[1][1] + self.gates[idx].h

            if available_width >= self.gates[idx].w:
                if new_height > self.bounding_box[1]:  # Needs to extend the bounding box height
                    temp_area = [self.bounding_box[0], new_height]
                else:
                    temp_area = self.bounding_box

                new_area = temp_area[0] * temp_area[1]

                if new_area < min_area:
                    min_area = new_area
                    chosen_position = space[0]
                    selected_idx = space_idx

        # Evaluate extending the bounding box width
        new_area_with_width_extension = (self.bounding_box[0] + self.gates[idx].w) * max(self.bounding_box[1], self.gates[idx].h)
        if new_area_with_width_extension < min_area:
            min_area = new_area_with_width_extension
            chosen_position = (self.bounding_box[0], 0)
            selected_idx = -1

        # Place the gate
        if selected_idx != -1:
            # Place in existing space
            self.gates[idx].coordinates = tuple(chosen_position)
            space_to_split = self.sp[selected_idx]
            self.sp.pop(selected_idx)

            # Create new spaces based on where the gate is placed
            new_space_right = [(chosen_position[0] + self.gates[idx].w, chosen_position[1]), (space_to_split[1][0], space_to_split[1][1])]
            new_space_top = [(chosen_position[0], chosen_position[1] + self.gates[idx].h), (chosen_position[0] + self.gates[idx].w, space_to_split[1][1] + self.gates[idx].h)]

            if new_space_right[1][0] > new_space_right[0][0]:
                self.sp.append(new_space_right)

            if new_space_top[1][1] > new_space_top[0][1]:
                self.sp.append(new_space_top)

            self.bounding_box = temp_area
        else:
            # Extend bounding box width
            self.gates[idx].coordinates = (self.bounding_box[0], 0)
            self.sp.append([(self.bounding_box[0], self.gates[idx].h), (self.bounding_box[0] + self.gates[idx].w, self.gates[idx].h)])
            self.bounding_box[0] += self.gates[idx].w
            self.bounding_box[1] = max(self.bounding_box[1], self.gates[idx].h)

def read_input():
    gates = []
    with open('input.txt', 'r') as input_file:
        lines = input_file.readlines()

    for line in lines:
        parts = line.split()
        gates.append(Gate(parts[0], int(parts[1]), int(parts[2])))

    return gates

def write_output(gates, bounding_box):
    with open('output.txt', 'w') as output_file:
        output_file.write(f'bounding_box {bounding_box[0]} {bounding_box[1]}\n')
        for gate in gates:
            output_file.write(f'{gate.name} {gate.coordinates[0]} {gate.coordinates[1]}\n')

if __name__ == "__main__":
    gates = read_input()
    placer = GatePlacer(gates)
    placed_gates, bounding_box = placer.place_gates()
    print(placed_gates, bounding_box)
    write_output(placed_gates, bounding_box)