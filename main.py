# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 10:22:12 2015

@author: b.ellinger
"""

import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from my_plotLib import*


fg_color = '#638494'#'#148,197,222'

class MainWindow(tk.Frame):
    # ----------------------------------------------------------------------------------------
    # FUNCTIONALITY DEFINING
    # ----------------------------------------------------------------------------------------
    def open_data(self):
        filename = askopenfilename(filetypes=[("Text Files","*.txt"),("Text Files","*.csv")])
        self.import_file.set(filename)
        self.history.set("Zur Berechnung gewählte Datei\n"+filename)


    def result_data(self):
        filename = asksaveasfilename(filetypes=[("Text Files","*.csv")])
        self.export_file.set(filename)
        self.history.set("Gewählter Speicherort der Daten\n"+filename)


    def load_data(self):
        # here we get the Entry of the Import Field and load all the data
        x = self.import_file.get()
        self.data, self.force_name, self.angle_names = load_data(x)

        if type(self.data).__module__ == np.__name__:
            self.history.set("Daten erfolgreich geladen von: \n \t" + x + "\n" + "Groesse der Matrix: " + str(self.data.shape))
            self.import_file.set(x)
        else:
            self.history.set("Unkown Data")


    def berechnen(self):
        scale, part = self.angle_scale.get(), self.joint.get()
        if part != 1 or part!=2:
            self.history.set("Bitte die Winkelreferenz bestimmen: Knie oder Hüfte")

        self.curr_angle,self.Fz,self.Fz_tot,self.speed,self.speed_tot,self.impulse,self.impulse_tot,self.power,self.power_tot,self.power_rel,self.power_rel_myo = calc_kistler(self.data, self.angle_names, part, scale, self.force_name)

       # [curr_angle,Fz,Fz_tot,speed,speed_tot,impulse,impulse_tot,power,power_tot]
       # --> Output from lib
        self.history.set("Berechnungen abgeschlossen. Beispielhaft sind die ersten Werte von Fz zu sehen:\n" + str(self.Fz_tot[0:5,:]))

    def plot_all(self):
#       (force, impulse, speed, power, curr_angle, force_tot, impulse_tot, speed_tot, power_tot)
#       --> Input from lib
        plotselection, plotcut, plotall_myo, plotall_tot = self.plot1.get(), self.plot2.get(), self.plot3.get(), self.plot4.get()

        if plotall_myo == 0 and plotall_tot == 0:
            if plotcut == 0:
                self.history.set("Bitte entscheiden Sie ob Sie die Daten geschnitten oder ungeschnitten plotten möchte.")
            elif plotselection == 0:
                self.history.set("Bitte entscheiden Sie, welche myoMOTION-basierten Daten Sie plotten möchten.")
            elif plotcut != 0 and plotselection != 0:
                self.history.set("Alle notwendigen Plot-Einstellungen getroffen. Sie können nun plotten.")

                plot_data(self.Fz, self.impulse, self.speed, self.power, self.curr_angle,
                      self.Fz_tot,self.impulse_tot,self.speed_tot,self.power_tot,
                      plotselection, plotcut, plotall_myo, plotall_tot)

        elif plotall_myo == 1 or plotall_tot == 1:
            plot_data(self.Fz, self.impulse, self.speed, self.power, self.curr_angle,
                      self.Fz_tot,self.impulse_tot,self.speed_tot,self.power_tot,
                      plotselection, plotcut, plotall_myo, plotall_tot)


    def export_results(self):
        y = self.export_file.get()
        export_data(y, self.curr_angle, self.Fz, self.impulse, self.speed, self.power,
                    self.Fz_tot, self.impulse_tot, self.speed_tot, self.power_tot,
                    self.power_rel, self.power_rel_myo)
        self.history.set("Ergebnisse wurden erfolgreich exportiert nach: \n \t " + y)




    # ----------------------------------------------------------------------------------------
    # WIDGET DEFINING
    # ----------------------------------------------------------------------------------------
    def create_widgets(self):
        # ----------------------------------------------------------------------------------------
        # Variables
        self.history = tk.StringVar()
        self.joint = tk.IntVar()
        self.import_file = tk.StringVar()
        self.export_file = tk.StringVar()
        self.angle_scale = tk.IntVar()
        self.plot1,self.plot2,self.plot3,self.plot4 = tk.IntVar(),tk.IntVar(),tk.IntVar(),tk.IntVar()
        self.import_file.set("...")
        self.history.set("""
        Bitte wählen Sie eine zu importierende Datei. Das Dateiformat muss ASCII-codiert sein
        (*.txt, *.csv). Die Deziamltrennung in dieser Datei muss ein Punkt sein,
        z.B. 2.56 statt 2,56.""")
        # ----------------------------------------------------------------------------------------


        # ----------------------------------------------------------------------------------------
        # OPENING
        info_frame = tk.Frame(self, relief = "ridge", bd=5, bg="#555")
        info_frame.place(x=30,y= 10,height=120,width=540)
        info_label= tk.Label(info_frame, bg=fg_color,bd =6, fg='#DDEEFF', text = """
            Diese Auswerteroutine ermöglicht die Auswertung von Counter-Movement Sprüngen. Das Besondere ist die
            kombinierte  Auswertung der Kistler-KMP Daten und der Intertialsensorik-Daten von
            Noraxons myoMOTION. Die Parameter der Kraftdaten werden auf die Änderungsrate der
            Flexionswinkel in Knie oder Hüfte kalkuliert.
            """)

        info_label.pack(side='left',anchor='n',fill="both", expand=True)
        outer_frame = tk.Frame(self, relief="sunken", bd=7, bg='#333333') #'#778899')
        outer_frame.place(x=25, y=150,width=550,height=500)
#        outer_label1 = tk.Label(outer_frame, bg='#008899')
#        outer_label1.place(height=40,width=.98*550)
        # ----------------------------------------------------------------------------------------



        # ----------------------------------------------------------------------------------------
        # Date File Import
        label = tk.Label(self, text = 'Importiere Daten aus:   ')
        label.place(x=50, y=170, height=20, width=140)
        entry = tk.Entry(self, textvariable=self.import_file)
        entry.place(x=200, y=170, width=250, height=20)
        file_im = tk.Button(self, text="...", command=self.open_data)
        file_im.place(x=455, y=170, width=20,height=20)
        im_button = tk.Button(self, text="Import", command=self.load_data)
        im_button.place(x=480, y=170, width=70, height=20)
        # ----------------------------------------------------------------------------------------


        # ----------------------------------------------------------------------------------------
        # Result File Export
        label_export = tk.Label(self, text = 'Exportiere Resultat nach:   ')
        label_export.place(x=50, y=210, height=20, width = 140)
        entry_export = tk.Entry(self, textvar=self.export_file)
        entry_export.place(x=200, y=210, width=250, height=20)
        file_ex = tk.Button(self, text="...", command=self.result_data)
        file_ex.place(x=455, y=210, width=20,height=20)
        ex_button = tk.Button(self, text="Export", command=self.export_results)
        ex_button.place(x=480, y=210, width=70, height=20)
        # ----------------------------------------------------------------------------------------


        # ----------------------------------------------------------------------------------------
        # Exit
        exit_button = tk.Button(self, text="Beenden", command=root.destroy)
        exit_button.place(x=470, y=.9*y, height=40, width=80)
        # ----------------------------------------------------------------------------------------


        # ----------------------------------------------------------------------------------------
        # Calculation Panel
#        calc_label = tk.Label(self, bg='#778899')
#        calc_label.place(x=-10, y=.34*y, width=x, height=75)
        choose_joint1 = tk.Radiobutton(self, text="Hüfte", variable=self.joint, value=1, compound="center",bg='#DDD')
        choose_joint2 = tk.Radiobutton(self, text="Knie",variable=self.joint, value=2,compound="center",bg='#DDD')
        choose_joint1.place(x=50, y=.31*y, width=80)
        choose_joint2.place(x=50, y=.35*y, width=80)
        scale_joint = tk.Scale(self, from_=1, to=10, variable=self.angle_scale,
                               label="Gelenwinkelkschritt [deg]", orient="horizontal",bg='#DDD')
        scale_joint.place(x=225, y=.31*y, width=150)
        calculate = tk.Button(self, text="Berechnen",command=self.berechnen)
        calculate.place(x=450, y=.31*y, height=60, width=100)
        # ----------------------------------------------------------------------------------------


        # ----------------------------------------------------------------------------------------
        # Plotting Panel
        plot_frame = tk.Frame(self,  bd=5, bg="#555", relief='ridge')
        plot_frame.place(x=50, y=.40*y, height=170, width=500)
        plot_label = tk.Label(plot_frame, bg=fg_color, fg="#DDD", text="Einstellungen für Plots")
        plot_label.pack(side='top',fill='both')#, expand='True')
        parameter = ["Kraft","Impuls","Geschwindigkeit","Leistung"]
#        plots_cut=[self.plot1,self.plot21,self.plot31,self.plot41]
#        plots_tot=[self.plot2,self.plot22,self.plot32,self.plot42]
        i = 0
        for elem in range(len(parameter)):
            tk.Label(self, text=parameter[elem],bg=fg_color, fg="#DDD").place(x=.1*x+i, y=.44*y,
                height=15, width=100)
            tk.Radiobutton(self, text = "myoMOTION",bg='#DDD',variable=self.plot1, value=elem+1).place(x=.1*x+i, y=.46*y, height=25, width=100)
            tk.Radiobutton(self, text = "Kistler \t        ",bg='#DDD', variable=self.plot1, value=elem+5).place(x=.1*x+i, y=.49*y, height=25, width=100)
            i += 125

        plot_cut = tk.Radiobutton(self, text="geschnitten    ", bg='#DDD', variable=self.plot2, value=1)
        plot_cut.place(x=.37*x, y=.55*y, height=20, width=120)
        plot_uncut = tk.Radiobutton(self, text="ungeschnitten", bg='#DDD', variable=self.plot2, value=2)
        plot_uncut.place(x=.37*x, y=.575*y, height=20, width=120)
        plot_uncut = tk.Checkbutton(self, text="Alle Plots\nmyoMOTION", bg='#DDD', variable=self.plot3)
        plot_uncut.place(x=.58*x, y=.55*y, height=40, width=95)
        plot_uncut = tk.Checkbutton(self, text="Alle Plots\nKistler", bg='#DDD', variable=self.plot4)
        plot_uncut.place(x=.73*x, y=.55*y, height=40, width=80)
        plot_button = tk.Button(self, text="Ergebnisse Plotten", bg='#DDD', command=self.plot_all)
        plot_button.place(x=.1*x, y=.55*y, height=40, width=150)
        # ----------------------------------------------------------------------------------------


        # ----------------------------------------------------------------------------------------
        # History Panel
        history_frame = tk.Frame(self,  bd=5, bg="white", relief='ridge')
        history_frame.place(x=50, y=515, height=120, width=500)
        Uplabel_history = tk.Label(history_frame, bg=fg_color, fg="#DDD", text="Statusmeldungen")
        Uplabel_history.pack(side='top', fill='both')
        label_history = tk.Label(history_frame, bg="#555", fg='#DDEEFF', anchor="n", textvariable=self.history)
        label_history.pack(fill="both", expand="yes")
        # ----------------------------------------------------------------------------------------


        # ----------------------------------------------------------------------------------------
        # Velamed-Panel
        image_label = tk.Label(self, text="Powered by:",bg='#9C9C9C', fg=fg_color, font=('Verdana',10,'bold'))
        image_label.place(x=5, y= 660, height=20)
#
        photo = tk.PhotoImage(file="logo.png")
        photo_label = tk.Label(self, image=photo,bg="#141414")
        photo_label.place(x=5,y=685,height=100, width=300)
        photo_label.photo = photo
        # ----------------------------------------------------------------------------------------



    # ----------------------------------------------------------------------------------------
    # INITIALIZE
    # ----------------------------------------------------------------------------------------
    def __init__(self):
        tk.Frame.__init__(self,bg='#9C9C9C',relief="flat", bd=10)
        self.pack(expand="yes", fill="both")
        self.create_widgets()



# ----------------------------------------------------------------------------------------
# WINDOW SETTINGS
# ----------------------------------------------------------------------------------------
x = 620; y = 800
root = tk.Tk()
root.geometry(str(x)+"x"+str(y)); root.resizable(width="false", height="true")
root.title("Auswerteroutine: myoMOTION <--> Kistler v1.01")
root.configure(background="grey")


#root.tk.iconbitmap(file="images/logo_osp.ico")
# implementing OSP image in title
#image_OSP = Image.open("images/logo_osp.ico")
#render_OSP = ImageTk.PhotoImage(image_OSP)
#title_panel = tk.Label(root, text="test")#image=render_OSP)
#title_panel.image = render_OSP
#title_panel.pack()

app = MainWindow()
app.mainloop()
