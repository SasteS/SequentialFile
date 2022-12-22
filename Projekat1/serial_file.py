import os
import struct

class Serial_File():
    def __init__(self, filename, record, blocking_factor, empty_key=-1):
        self.filename = filename
        self.record = record
        self.record_size = struct.calcsize(self.record.format) #velicina sloga
        self.blocking_factor = blocking_factor
        self.block_size = self.record_size * self.blocking_factor #velicina bloka
        self.empty_key = empty_key

    def init_file(self):
        with open(self.filename, "wb") as f:
            block = self.blocking_factor*[self.get_empty_rec()]  # inicijalizacija datoteke podrazumeva unos bloka koji sadrzi prazne slogove
            self.write_block(f, block)

    def insert_record(self, rec):
        if self.find_by_id(rec.get("evidencioni broj")):  # provera da li vec postoji slog sa zadatim id-jem - svakom unosu prethodi pretraga!
            print("Already exists with ID {}".format(rec.get("evidencioni broj")))
            return

        with open(self.filename, "rb+") as f:
            f.seek(-self.block_size, 2)  # citamo poslednji blok
            block = self.read_block(f)

            for i in range(self.blocking_factor):
                if block[i].get("evidencioni broj") == self.empty_key:  # trazimo prvi prazan slog
                    block[i] = rec
                    break

            i += 1

            if i == self.blocking_factor:  # provera da li smo popunili trenutni blok ili ne
                f.seek(-self.block_size, 1)
                self.write_block(f, block)
                block = self.blocking_factor*[self.get_empty_rec()]
                self.write_block(f, block)
            else:
                block[i] = self.get_empty_rec()
                f.seek(-self.block_size, 1)
                self.write_block(f, block)

    def __is_last(self, block):
        for i in range(self.blocking_factor):  # da li blok sadrzi neki slog koji je prazan?
            if block[i].get("evidencioni broj") == self.empty_key:
                return True
        return False

    def print_file(self):
        i = 0
        with open(self.filename, "rb") as f:
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
            while True:
                block = self.read_block(f)

                for j in range(self.blocking_factor):
                    if block[j].get("evidencioni broj") == id:
                        return (i, j)
                    elif block[j].get("evidencioni broj") == self.empty_key:  # ukoliko smo naisli na prazan slog - stigli smo do kraja datoteke
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
            while True:
                f.seek(block_idx * self.block_size)
                block = self.read_block(f)

                i = rec_idx
                while i < self.blocking_factor-1:  # brisemo block[rec_idx] tako sto sve nakon njega pomeramo za jedno mesto ka levo
                    block[i] = block[i+1]
                    i += 1

                if self.__is_last(block):  # ako je poslednji blok - upisemo novi sadrzaj i zavrsavamo
                    f.seek(-self.block_size, 1)
                    self.write_block(f, block)
                    break

                next_block = self.read_block(f)  # ako nije poslednji blok, onda pomeranje mora da se nastavi i u narednim blokovima, dok ne stignemo do poslednjeg
                block[self.blocking_factor-1] = next_block[0]  # poslednji iz trenutnog bloka = prvi iz narednog bloka
                f.seek(-2*self.block_size, 1)
                self.write_block(f, block)

                block_idx += 1
                rec_idx = 0

        if next_block and next_block[0].get("evidencioni broj") == self.empty_key:  # ako smo vrsili pomeranje iz poslednjeg bloka, i ako je sada kod njega na prvom mestu prazan slog - mozemo osloboditi memoriju
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
        return {"evidencioni broj": self.empty_key}