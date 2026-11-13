from datetime import datetime
import json
import os
import tkinter as tk
from tkinter import messagebox, simpledialog


class bbclist:
    def __init__(self, capacita=4):
        self.capacita = capacita
        self._size = 0
        self.data = [None] * self.capacita

    def zvetsit(self, new_capacita):
        new_data = [None] * new_capacita
        for gec in range(self._size):
            new_data[gec] = self.data[gec]
        self.data = new_data
        self.capacita = new_capacita

    def add(self, vec):
        if self._size == self.capacita:
            self.zvetsit(self.capacita + 2)
        self.data[self._size] = vec
        self._size += 1

    def get(self, index):
        if index < 0 or index >= self._size:
            raise IndexError("Index mimo rozsah.")
        return self.data[index]
    
    def remove_at(self, index):
        if index < 0 or index >= self._size:
            raise IndexError("Index je mimo rozsah pole.")
        removed = self.data[index]
        for i in range(index, self._size - 1):
            self.data[i] = self.data[i + 1]
        self.data[self._size - 1] = None
        self._size -= 1
        return removed

    def size(self):
        return self._size
    
    def is_empty(self):
        return self._size == 0


class BBC:
    def __init__(self, date_obj):
        self.date = date_obj  
        self.entries = bbclist()  
        self.next = None
        self.prev = None


class spojogec:
    def __init__(self):
        self.head = None
        self.tail = None
        self.pocet = 0

    def is_empty(self):
        return self.head is None
    
    def count(self):
        return self.pocet
    
    def add(self, gec):
        new_BBC = BBC(gec)
        if self.is_empty():
            self.head = new_BBC
            self.tail = new_BBC
        else:
            self.tail.next = new_BBC
            new_BBC.prev = self.tail
            self.tail = new_BBC
        self.pocet += 1
        return new_BBC

    def odstranBBC(self, bbc):
        if not bbc:
            return
        if bbc.prev:
            bbc.prev.next = bbc.next
        else:
            self.head = bbc.next
         
        if bbc.next:
            bbc.next.prev = bbc.prev
        else:
            self.tail = bbc.prev
         
        self.pocet -= 1




class DiaryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dalauan Diary")
        self.root.geometry("1000x600")

        self.dny = spojogec()
        self.tentoDen = None

        
        self.lbl_date = tk.Label(root, text="denik je prazdny")
        self.lbl_date.pack(pady=10)

        self.lbl_info = tk.Label(root, text="Celkem dnů: 0",)
        self.lbl_info.pack()

       
        self.listbox_entries = tk.Listbox(root, width=100, height=12)
        self.listbox_entries.pack(pady=10)

        
        frame_nav = tk.Frame(root)
        frame_nav.pack(pady=5)

        tk.Button(frame_nav, text="<< Začátek", command=self.op_start).grid(row=0, column=0, padx=5)
        tk.Button(frame_nav, text="< Předchozí", command=self.op_previous).grid(row=0, column=1, padx=5)
        tk.Button(frame_nav, text="Další >", command=self.op_next).grid(row=0, column=2, padx=5)
        tk.Button(frame_nav, text="Konec >>", command=self.op_end).grid(row=0, column=3, padx=5)

        
        frame_actions = tk.Frame(root)
        frame_actions.pack(pady=10)

        tk.Button(frame_actions, text="Nový záznam/den", bg="#d4edda", command=self.op_new).grid(row=0, column=0, padx=5)
        tk.Button(frame_actions, text="Smazat záznam", bg="#f8d7da", command=self.op_delete).grid(row=0, column=1, padx=5)
        tk.Button(frame_actions, text="Uložit", command=self.op_save).grid(row=0, column=2, padx=5)
        tk.Button(frame_actions, text="Načíst", command=self.op_load).grid(row=0, column=3, padx=5)

        self.refresh_ui()

    def refresh_ui(self):
        
        self.listbox_entries.delete(0, tk.END)

        if self.tentoDen is None or self.dny.is_empty():
            self.lbl_date.config(text="dneska tu nic neni")
            self.lbl_info.config(text="Celkem dnů v deníku: 0")
            return

        self.lbl_date.config(text=f"Aktuální den: {self.tentoDen.date.strftime('%d.%m.%Y')}")
        self.lbl_info.config(text=f"Celkem dnů: {self.dny.count()} | Záznamů tento den: {self.tentoDen.entries.size()}")

        for i in range(self.tentoDen.entries.size()):
            entry_text = self.tentoDen.entries.get(i)
            self.listbox_entries.insert(tk.END, f"[{i + 1}] {entry_text}")

    def op_start(self):
        if not self.dny.is_empty():
            self.tentoDen = self.dny.head
            self.refresh_ui()

    def op_end(self):
        if not self.dny.is_empty():
            self.tentoDen = self.dny.tail
            self.refresh_ui()

    def op_previous(self):
        if self.tentoDen and self.tentoDen.prev:
            self.tentoDen = self.tentoDen.prev
            self.refresh_ui()
        else:
            messagebox.showinfo("Info", "Toto je první den.")

    def op_next(self):
        if self.tentoDen and self.tentoDen.next:
            self.tentoDen = self.tentoDen.next
            self.refresh_ui()
        else:
            messagebox.showinfo("Info", "Toto je poslední den.")

    def op_new(self):
        date_str = simpledialog.askstring("Nový den", "Zadejte datum (formát dd.mm.yyyy):")
        if not date_str:
            return
        try:
            entered_date = datetime.strptime(date_str.strip(), "%d.%m.%Y").date()
        except ValueError:
            messagebox.showerror("Chyba", "Neplatný formát data!")
            return

        text_content = simpledialog.askstring("Záznam", "Zadejte text zápisu:")
        if not text_content:
            return

        
        target_node = self.dny.find_by_date(entered_date) if hasattr(self.dny, "find_by_date") else None
        
        
        if not target_node:
            curr = self.dny.head
            while curr:
                if curr.date == entered_date:
                    target_node = curr
                    break
                curr = curr.next

        if target_node:
            target_node.entries.add(text_content.strip())
            self.tentoDen = target_node
        else:
            node = self.dny.add(entered_date)
            node.entries.add(text_content.strip())
            self.tentoDen = node

        self.refresh_ui()
        messagebox.showinfo("Úspěch", "Záznam byl přidán.")

    def op_delete(self):
        if not self.tentoDen or self.tentoDen.entries.is_empty():
            messagebox.showwarning("Varování", "V aktuálním dni nejsou žádné záznamy.")
            return

        selection = self.listbox_entries.curselection()
        if not selection:
            messagebox.showwarning("Varování", "Vyberte záznam v seznamu k smazání.")
            return

        idx = selection[0]
        confirm = messagebox.askyesno("Potvrzení", "Opravdu chcete smazat vybraný záznam?")
        if confirm:
            self.tentoDen.entries.remove_at(idx)
            
            if self.tentoDen.entries.is_empty():
                next_n = self.tentoDen.next
                prev_n = self.tentoDen.prev
                self.dny.odstranBBC(self.tentoDen)
                if next_n:
                    self.tentoDen = next_n
                elif prev_n:
                    self.tentoDen = prev_n
                else:
                    self.tentoDen = None

            self.refresh_ui()

    def op_save(self):
        filename = "denik.json"
        data_to_save = []
        curr = self.dny.head
        while curr:
            entries_list = [curr.entries.get(i) for i in range(curr.entries.size())]
            data_to_save.append({
                "date": curr.date.strftime("%d.%m.%Y"),
                "entries": entries_list
            })
            curr = curr.next

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Uloženo", f"Deník byl uložen do {filename}.")
        except Exception as e:
            messagebox.showerror("Chyba", str(e))

    def op_load(self):
        filename = "denik.json"
        if not os.path.exists(filename):
            messagebox.showwarning("Chyba", "Soubor neexistuje.")
            return

        try:
            with open(filename, "r", encoding="utf-8") as f:
                data_loaded = json.load(f)

            new_dny = spojogec()
            for day_data in data_loaded:
                date_obj = datetime.strptime(day_data["date"], "%d.%m.%Y").date()
                node = new_dny.add(date_obj)
                for entry in day_data["entries"]:
                    node.entries.add(entry)

            self.dny = new_dny
            self.tentoDen = self.dny.head if not self.dny.is_empty() else None
            self.refresh_ui()
            messagebox.showinfo("Načteno", "Deník byl úspěšně načten.")
        except Exception as e:
            messagebox.showerror("Chyba", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = DiaryGUI(root)
    root.mainloop()