import struct
import constants
import os

class Sequential_file:
    def __init__(self, filename, record, blocking_factor, empty_key=-1):
        self.filename = filename
        self.record = record
        self.header_size = struct.calcsize("ii")
        self.record_size = struct.calcsize(self.record.format) #velicina sloga
        self.blocking_factor = blocking_factor
        self.block_size = self.record_size * self.blocking_factor #velicina bloka
        self.empty_key = empty_key

    def initialize_file(self):
        with open(self.filename, "wb") as f:
            header = [5, 0]
            br_slogova=[int(i) for i in header]
            r = struct.pack("ii", *br_slogova)
            f.write(r)
            block = self.blocking_factor * [self.get_empty_rec()] #napravi blok pun praznih slogova
            self.write_block(f, block)

    def __find_in_block(self, block, rec):
        for j in range(self.blocking_factor):
            if block[j].get("evidencioni broj") == self.empty_key or block[j].get("evidencioni broj") > rec.get("evidencioni broj"):
                return (True, j)

        return (False, None)

    def insert_record(self, rec):
        if self.find_by_id(rec.get("evidencioni broj")):  # Svakom upisu prethodi trazenje
            print("Already exists with ID {}".format(rec.get("evidencioni broj")))
            return

        with open(self.filename, "rb+") as f:
            f.seek(self.header_size)
            while True:
                block = self.read_block(f)

                if not block:           # EOF
                    break

                last = self.__is_last(block)
                here, j = self.__find_in_block(block, rec)

                if not here:
                    continue

                # save last record for inserting into next block
                tmp_rec = block[self.blocking_factor-1]
                for k in range(self.blocking_factor-1, j, -1):
                    block[k] = block[k-1]               # move records
                block[j] = rec                          # insert
                rec = tmp_rec                           # new record for insertion

                f.seek(-self.block_size, 1)
                self.write_block(f, block)

                # last block without empty rec?
                if last and block[self.blocking_factor-1].get("evidencioni broj") != self.empty_key:
                    block = self.blocking_factor*[self.get_empty_rec()]
                    self.write_block(f, block)

    def __is_last(self, block):
        for i in range(self.blocking_factor):
            if block[i].get("evidencioni broj") == self.empty_key:
                return True
        return False

    def print_file(self):
        i = 0
        with open(self.filename, "rb") as f:
            #header = f.read(self.header_size)
            #print("Header " + str(struct.unpack("ii", header)))
            f.seek(self.header_size)
            while True:
                block = self.read_block(f)

                if not block:
                    break

                i += 1
                print("Block {}".format(i))
                self.print_block(block)

    def find_by_id(self, id):
        i = 0
        with open(self.filename, "rb") as f:
            f.seek(self.header_size)
            while True:
                block = self.read_block(f)

                if not block:
                    return None

                for j in range(self.blocking_factor):
                    if block[j].get("evidencioni broj") == id:
                        return (i, j)
                    if block[j].get("evidencioni broj") > id:
                        return None
                i += 1

    def delete_by_id(self, id):
        found = self.find_by_id(id)

        if not found:
            return

        block_idx = found[0]
        rec_idx = found[1]
        next_block = None

        with open(self.filename, "rb+") as f:
            #f.seek(self.header_size)
            while True:
                f.seek(8 + block_idx * self.block_size)  # last block
                block = self.read_block(f)

                for i in range(rec_idx, self.blocking_factor-1):
                    block[i] = block[i+1]       # move records

                if self.__is_last(block):              # is last block full?
                    f.seek(-self.block_size, 1)
                    self.write_block(f, block)
                    break

                next_block = self.read_block(f)
                # first record of next block is now the last of current one
                block[self.blocking_factor-1] = next_block[0]
                f.seek(-2*self.block_size, 1)
                self.write_block(f, block)

                block_idx += 1
                rec_idx = 0

        if next_block and next_block[0].get("evidencioni broj") == self.empty_key:
            os.ftruncate(os.open(self.filename, os.O_RDWR),
                         block_idx * self.block_size)

    def write_block(self, file, block):
        binary_data = bytearray()   # Niz bita koji bi trebalo da se upise u datoteku

        # Svaki slog u bloku serijalizujemo i dodamo u niz bajta
        for rec in block:
            rec_binary_data = self.record.dict_to_encoded_values(rec)
            binary_data.extend(rec_binary_data)

        file.write(binary_data)

    def read_block(self, file):
        # Citanje od trenutne pozicije
        binary_data = file.read(self.block_size)
        block = []

        if len(binary_data) == 0:
            return block

        for i in range(self.blocking_factor):   # slajsingom izdvajamo niz bita za svaki slog, i potom vrsimo otpakivanje
            begin = self.record_size*i
            end = self.record_size*(i+1)
            block.append(self.record.encoded_tuple_to_dict(
                binary_data[begin:end]))

        return block

    def write_record(self, f, rec):
        binary_data = self.record.dict_to_encoded_values(rec)
        f.write(binary_data)

    def read_record(self, f):
        binary_data = f.read(self.record_size)

        if len(binary_data) == 0:
            return None

        return self.record.encoded_tuple_to_dict(binary_data)

    def print_block(self, b):
        for i in range(self.blocking_factor):
            print(b[i])

    def get_empty_rec(self):
        return {"evidencioni broj": self.empty_key, "registarska oznaka": "", "datum i vreme": "", "oznaka parking mesta": "", "duzina boravka": "", "status": 0}