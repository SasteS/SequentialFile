from record import Record
from constants import *
from sequential_file import Sequential_file
from serial_file import Serial_File
import os

ukupan_broj_slogova = 0
broj_logicki_obrisanih = 0

def read_txt(fn):
    rows = []
    with open(fn, "r") as f:
        for line in f.readlines():
            cols = line.split()
            rows.append({
                "evidencioni broj": int(cols[0]),
                "registarska oznaka": cols[1],
                "datum i vreme": cols[2],
                "oznaka parking mesta": cols[3],
                "duzina boravka": cols[4],
                "status": 1
            })
    return rows

def main():
    print("------------- SEQUENTIAL FILE HANDLING -------------")
    izbori("", None)

def izbori(file_name, binary_file):
    print("1 - Formiranje prazne datoteke.\n2 - Otvaranje datoteke unosenjem naziva.\n3 - Prikaz naziva aktivne datoteke.")
    izbor = input("Izbor: ")
    while izbor != "1" and izbor != "2" and izbor != "3":
        print("Wrong input!")
        izbor = input("Izbor: ")

    data_file = file_name
    if izbor == "1":
       izbor_jedan(binary_file)
    elif izbor == "2":
        izbor_dva(binary_file)
    else:
        # broj_logicki_obrisanih = 0
        izbor_tri(data_file, binary_file)

def izbor_jedan(binary_file):
    file_name = input("Unesite naziv datoteke: ")
    #path = os.path.relpath(file_name)
    f = open(file_name, "x")
    #os.mkdir(path)
    print("Created directory " + file_name, end="\n\n")
    print("----------------------------------------------------")

    upit_za_slogove(file_name, binary_file)

    #izbori(file_name)

def izbor_dva(binary_file):
    file_name = input("Unesite naziv datoteke: ")
    if os.path.isfile(file_name):
        print("Selected directory: " + file_name, end="\n\n")
        print("----------------------------------------------------")
#--------------------------------------------------------------------------------------------------        
        rec = Record(ATTRIBUTES, FORMAT, CODING) #napravljen objekat koji definise slog
        #data_file = "data_file.dat"

        binary_file = Sequential_file(file_name, rec, F)
        binary_file.initialize_file()

        # rows = read_txt("in.txt")
        # for i in range(0, len(rows)):
        #     binary_file.insert_record(rows[i])

        binary_file.print_file() # samo proverea da li dobro formira
        print("----------------------------------------------------")
#--------------------------------------------------------------------------------------------------
        upit_za_slogove(file_name, binary_file)

        #izbori(file_name)
    else:
        print("File doesn't exist", end="\n\n")
        print("----------------------------------------------------")
        izbori("", None)

def izbor_tri(data_file, binary_file):
    print("Aktivna datoteka: " + data_file, end="\n\n")
    print("----------------------------------------------------")
    
    if data_file != "":
        upit_za_slogove(data_file, binary_file)
    else:
        izbori(data_file, None)

def upit_za_slogove(data_file, binary_file):
    print("Da li zelite da donosite izmene u datoteci?")
    izbor = input("Input(y/n): ")
    while izbor != "y" and izbor != "n":
        izbor = input("Input(y/n): ")
    
    if izbor == "y":
        print("Unesite 4 za unos novog sloga u datoteku.\nUnesite 5 za unos novih slogova iz pripremljene datoteke.\nUnesite 6 za trazenje sloga u aktivnoj datoteci.\nUnesite 7 za promenu vrednosti \"duzina boravka\" sloga u aktivnoj datoteci.\nUnesite 8 za prikaz svih slogova sa adresom bloka i rednim brojem sloga u bloku.\nUnesite 9 za pokretanje logickog brisanja.")
        izbor = input("Input: ")
        while izbor != "4" and izbor != "5" and izbor != "6" and izbor != "6" and izbor != "7" and izbor != "8" and izbor != "9":
            izbor = input("Input: ")
        
        if izbor == "4":
            unos_sloga_real_time(data_file, binary_file)
        elif izbor == "5":
            unos_slogova_iz_fajla(data_file, binary_file)
        elif izbor == "6":
            trazenje_i_prikaz_sloga(data_file, binary_file)
        elif izbor == "7":
            promena_vrednosti_sloga(data_file, binary_file)
        elif izbor == "8":
            prikaz_svih_slogova(data_file, binary_file)
        elif izbor == "9":
            meni_za_logicko_brisanje(data_file, binary_file, [])
    else:
        print("----------------------------------------------------")
        izbori(data_file, binary_file)

def meni_za_logicko_brisanje(data_file, binary_file, list_of_ids):
    print("----------------------------------------------------")
    id = int(input("kljuc sloga za brisanje: "))
    list_of_ids.append(id)
    opet = input("Dodati jos kljuceva?(y/n)")
    if opet == "y":
        print(list_of_ids)
        meni_za_logicko_brisanje(data_file, binary_file, list_of_ids)
    else:
       #f = open("serial.dat", 'x')
        Serial_Record = Record(SERIALATTRIBUTES, SERIALFORMAT, CODING)
        serial_file = Serial_File("serial.dat", Serial_Record, F)

        serial_file.init_file()
        serial_file.print_file()

        for id in list_of_ids:
            serial_file.insert_record({"evidencioni broj" : int(id)})
        serial_file.print_file() #provere radi

        list_of_records = []
        with open("serial.dat", "rb") as f:
            while True:
                block = serial_file.read_block(f)
                prekid = False
                for j in range(serial_file.blocking_factor):
                    if block[j].get("evidencioni broj") != -1:
                        list_of_records.append(block[j])
                    else: 
                        prekid = True
                        break
                if prekid == True:
                    break
            f.close()
        #print(list_of_records)
        suzena_lista = []
        for record in list_of_records:
            if binary_file.find_by_id(record.get("evidencioni broj")) != None:
                with open(data_file, "rb") as f:
                    f.seek(8)
                    while True:
                        block = binary_file.read_block(f)

                        if not block:
                            break
                            
                        nadjen = False
                        for j in range(F):
                            if block[j].get("evidencioni broj") == record.get("evidencioni broj"):                                
                                temp = block[j]
                                temp["status"] = 2

                                binary_file.delete_by_id(block[j].get("evidencioni broj"))
                                binary_file.insert_record(temp)
                                suzena_lista.append(block[j].get("evidencioni broj"))
                                nadjen = True
                                # with open(data_file, "rb+") as f:
                                #     header = f.read(8)
                                #     lista = list(struct.unpack("ii", header))
                                #     ukupan_broj_slogova = lista[0]
                                #     broj_logicki_obrisanih = lista[1]
                                #     f.close()
                                # broj_logicki_obrisanih += 1
                                break
                        
                        if nadjen == True:
                            break
                    f.close()
        with open(data_file, "rb+") as f:
            header = f.read(8)
            lista = list(struct.unpack("ii", header))
            ukupan_broj_slogova = lista[0]
            broj_logicki_obrisanih = lista[1]
            f.close()
        #broj_logicki_obrisanih += 1

        broj_logicki_obrisanih += len(suzena_lista)
        print(broj_logicki_obrisanih)

        if broj_logicki_obrisanih / ukupan_broj_slogova * 100 > 30:
            ukupan_broj_slogova -= broj_logicki_obrisanih
            broj_logicki_obrisanih = 0
            print(suzena_lista)
            for id in suzena_lista:
                binary_file.delete_by_id(id)
                

        with open(data_file, "rb+") as f:      
                header = [ukupan_broj_slogova, broj_logicki_obrisanih]
                br_slogova=[int(i) for i in header]
                r = struct.pack("ii", *br_slogova)
                f.read(8)
                f.seek(0)
                f.write(r)
                f.close()
    
    binary_file.print_file()
    print("----------------------------------------------------")
    izbori(data_file, binary_file)
        # with open(data_file, "rb") as f:
        #     while True:
        #         block = binary_file.read_block(f)
        #         prekid = False
        #         for j in range(binary_file.blocking_factor):
        #             for record in list_of_records:    
        #                 if block[j].get("evidencioni broj") == record.get("evidencioni broj"):
                            
        #                 else: 
        #                     prekid = True
        #                     break
        #             if prekid == True:
        #                 break

def prikaz_svih_slogova(data_file, binary_file):
    print("----------------------------------------------------")
    with open(data_file, "rb") as f:
            header = f.read(8)
            lista = list(struct.unpack("ii", header))
            print("Header " + str(lista))
            f.seek(8)
            i = 0
            while True:
                block = binary_file.read_block(f)

                if not block:
                    break

                i += 1
                #binary_file.print_block(block)
                for j in range(F):
                    print("Block {}".format(i) + " index " + str(j) + " " + str(block[j]))
                print()
    upit_za_slogove(data_file, binary_file)

def promena_vrednosti_sloga(data_file, binary_file):
    unos = int(input("Unesite id sloga(evidencioni broj): "))
    with open(data_file, "rb") as f:
            f.seek(8)
            i = 0
            while True:
                block = binary_file.read_block(f)

                if not block:
                    print("Unsuccessful search")
                    break
                    
                nadjen = False
                for j in range(F):
                    if block[j].get("evidencioni broj") == unos:
                        print("Pronadjen u bloku " + str(i + 1) + " na poziciji " + str(j) + ".")
                        
                        nova_duzina = input("Unesite novu vrednost za duzinu boravka: ")
                        temp = block[j]
                        temp["duzina boravka"] = nova_duzina

                        binary_file.delete_by_id(block[j].get("evidencioni broj"))
                        binary_file.insert_record(temp)
                        print("Uspesno izmenjen podatak!")
                        binary_file.print_file()
                        nadjen = True
                        break
                
                if nadjen == True:
                    break
                    # if block[j].get("evidencioni broj") > unos:
                    #     print("Something went wrong!")
                    #     break
                i += 1
    print("----------------------------------------------------")
    print("Menjaj dalje(y/n)?")
    izbor = input("Input: ")
    while izbor != "y" and izbor != "n":
        izbor = input("Input: ")
    if izbor == "y":
        promena_vrednosti_sloga(data_file, binary_file)
    else:
        print("----------------------------------------------------")
        upit_za_slogove(data_file, binary_file)

def trazenje_i_prikaz_sloga(data_file, binary_file):
    print("----------------------------------------------------")
    unos = int(input("Unesite id sloga(evidencioni broj): "))
    blok, j = binary_file.find_by_id(unos)
    print("blok: " + str(blok + 1) + "\nPozicija u bloku: " + str(j))

    blocks = []
    with open(data_file, "rb") as f:
        f.seek(8)
        while True:
            temp_block = binary_file.read_block(f)

            if not temp_block:
                break
            
            blocks.append(temp_block)

    temp = blocks[blok]
    print("----------------------------------------------------")
    print("Block {}".format(blok + 1))
    binary_file.print_block(temp)

    print("----------------------------------------------------")
    print("Trazi dalje(y/n)?")
    izbor = input("Input: ")
    while izbor != "y" and izbor != "n":
        izbor = input("Input: ")
    if izbor == "y":
        trazenje_i_prikaz_sloga(data_file, binary_file)
    else:
        print("----------------------------------------------------")
        upit_za_slogove(data_file, binary_file)

def unos_sloga_real_time(data_file, binary_file):
    print("----------------------------------------------------")
    print("Popunite polja sloga:")
    evid_br = int(input("evidencioni broj: "))
    reg_oznaka = input("registarska oznaka: ")
    date_time = input("datum i vreme: ")
    parking = input("oznaka parking mesta: ")
    duz_boravka = input("duzina boravka: ")
    status = 1
    print("----------------------------------------------------")

    record = {"evidencioni broj": evid_br, "registarska oznaka": reg_oznaka, "datum i vreme": date_time, "oznaka parking mesta": parking, "duzina boravka": duz_boravka, "status": status}
    binary_file.insert_record(record)
    binary_file.print_file()
    print("----------------------------------------------------")
    upit_za_slogove(data_file, binary_file)

def unos_slogova_iz_fajla(data_file, binary_file):
    print("----------------------------------------------------")
    file_name = input("Unesite naziv tekstualnog fajla: ")
    if os.path.isfile(file_name):
        file_data = read_txt(file_name)
        
        with open(data_file, "rb+") as f:
            ukupan_broj_slogova = len(file_data) + F #zbog onih jos par praznih slogova
            header = [ukupan_broj_slogova, broj_logicki_obrisanih]
            br_slogova=[int(i) for i in header]
            r = struct.pack("ii", *br_slogova)
            f.read(8)
            f.seek(0)
            f.write(r)
            f.close()

        for record in file_data:
            binary_file.insert_record(record)
        print("Header " + str((ukupan_broj_slogova, broj_logicki_obrisanih)))
        binary_file.print_file()
        print("----------------------------------------------------")
        upit_za_slogove(data_file, binary_file)
    else:
        print("File doesn't exist!")
        unos_slogova_iz_fajla(data_file, binary_file)

def nesto():
    rec = Record(ATTRIBUTES, FORMAT, CODING) #napravljen objekat koji definise slog
    data_file = "data_file.dat"

    binary_file = Sequential_file(data_file, rec, F)
    binary_file.initialize_file()

    rows = read_txt("in.txt")
    for i in range(0, len(rows)):
        binary_file.insert_record(rows[i])

    binary_file.print_file()

    # print(binary_file.find_by_id(643445555))
    # print(binary_file.find_by_id(888881231))

    # binary_file.delete_by_id(643445555)
    # binary_file.delete_by_id(888881231)

    # binary_file.print_file()

if __name__ == "__main__":
    main()