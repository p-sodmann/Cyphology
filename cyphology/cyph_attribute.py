class CyphAttribute:
    def __init__(self, string_representation):
        string_representation = string_representation.strip()
        parts = string_representation.split()

        self.type = None
        self.direction = None
        self.uid = None
        
        # representations need at least 3 groups: Type direction UID
        if len(parts) < 3:
            raise Exception(f"Error 03: in line: '{string_representation}' seems to be an error")
        
        if len(parts) == 3:
            self.type = parts[0]
            self.direction = parts[1]
            self.uid = parts[2]

    def __str__(self):
        return f"{self.type} {self.direction} {self.uid}"