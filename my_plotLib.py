# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 17:12:21 2015

@author: b.ellinger
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import simps
import re
import csv
from datetime import datetime as dt


# ----------------------------------------------------------------------------------------
# LOAD DATA
# ----------------------------------------------------------------------------------------
def load_data(text_data):
    # here we load the data out of the desired file and search for the specific column-entries of the Vars we wanna use
    forces = {"fx":[],"fy":[],"fz":[]}
    angles = {"hip":[], "knee":[]}

    # open file for searching
    content = open(text_data, 'r')
    fObj = csv.reader(content, delimiter=';')
    for a in range(15):
        header = fObj.__next__()
        for b in range(len(header)):
            if re.search(r"[Ff]x\d", header[b]):
                stopper = a
                forces["fx"].append(b)
            elif re.search(r"[Ff]y\d", header[b]):
                #forces["fy"].append(b)
                forces["fz"].append(b)
            elif re.search(r"[Ff]z[3-4]", header[b]):
                forces["fz"].append(b)
            elif re.search(r"H*fte\sFlexion", header[b]):
                angles["hip"].append(b)
            elif re.search(r"Knie\sFlexion", header[b]):
                angles["knee"].append(b)

    content.close()


    data_osp = np.genfromtxt(text_data, skip_header=stopper+1, delimiter=";")
    #data_osp = np.matrix(data_osp)
    return [data_osp,forces,angles]



# ----------------------------------------------------------------------------------------
# CALCULATE KISTLER
# ----------------------------------------------------------------------------------------
def calc_kistler(data_matrix, angle_dict, joint_choice, angle_step, forces_dict):
    # -------------------------------------------------------------------------
    # Calculaing the difference between every single data-point
    # this wil be used for defining the alteration of the joint angles
    # -------------------------------------------------------------------------
    if joint_choice == 1:
    # hip difference calculation; I'm taking the absolute values and calculate a mean value of the flexion between right
    # and left side
        difference_angle = np.zeros([len(data_matrix)-1, 2])
        difference_angle[:,0] = np.abs(data_matrix[0:-1,angle_dict["hip"][0]]) - np.abs(data_matrix[1::,angle_dict["hip"][0]])
        difference_angle[:,1] = np.abs(data_matrix[0:-1,angle_dict["hip"][1]]) - np.abs(data_matrix[1::,angle_dict["hip"][1]])
        mean_diff = np.mean(np.abs(difference_angle), axis=1)


    elif joint_choice == 2:
    # knee difference calculation; I'm taking the absolute values and calculate a mean value of the flexion between right
    # and left side
        difference_angle = np.zeros([len(data_matrix)-1, 2])
        difference_angle[:,0] = np.abs(data_matrix[0:-1,angle_dict["knee"][0]]) - np.abs(data_matrix[1::,angle_dict["knee"][0]])
        difference_angle[:,1] = np.abs(data_matrix[0:-1,angle_dict["knee"][1]]) - np.abs(data_matrix[1::,angle_dict["knee"][1]])
        mean_diff = np.mean(np.abs(difference_angle), axis=1)
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # I -- FORCE
    # this is Fz for all data points; 1500Hz
    # -------------------------------------------------------------------------
    Fz_tot = np.sum(data_matrix[:, forces_dict["fz"]],axis=1)
    Fz_tot = Fz_tot / 0.94
    interval = 5
    for f in range(len(Fz_tot)):
        difference = np.mean(Fz_tot[f:f+interval]) - np.mean(Fz_tot[f+interval:f+2*interval])
        if difference > 3:
            print(f)
            # mass = np.mean(Fz_tot[f/2:(f/2)+200]) / 9.81
            mass = np.mean(Fz_tot[f:f+200]) / 9.81
            print("Mass ="+str(mass)+" in interval: "+str(f/2)+" : "+str((f/2)+200))
            break
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # II -- SPEED and speed-dependent parameters
    # calculating the velocity throughout integration of discrete values
    # -------------------------------------------------------------------------
    accel_tot = 1/1500 * ((Fz_tot/mass) - 9.81) # 1/1500 is measure frequdncy
    speed_tot=[]
    for c in range(len(accel_tot)):
        speed_tot.append(simps(accel_tot[0:c+1]))

    speed_tot = np.array(speed_tot)
    impulse_tot = speed_tot * mass
    power_tot = Fz_tot * speed_tot
    power_rel = power_tot / mass
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # III -- ALTERATION of joint angles
    # here we detect the time points having the desired steps in degree-terms
    # --- IMPROVE IT ---
    # -------------------------------------------------------------------------
    step_sum = mean_diff[0]
    time_point = []
    for row in range(len(mean_diff)):
        step_sum = step_sum + mean_diff[row]
        if step_sum >= angle_step:
            time_point.append(row)
            step_sum = mean_diff[row]

    Fz,Fy,Fx = np.zeros([len(time_point), 1]),np.zeros([len(time_point), 1]),np.zeros([len(time_point), 1])
    F_tot = np.zeros([len(time_point), 3])
    curr_angle = np.zeros([len(time_point), 1])
    if joint_choice == 1:
        curr_angle = np.mean([data_matrix[time_point, angle_dict["knee"][0]], data_matrix[time_point, angle_dict["knee"][1]]], axis=0)
    elif joint_choice == 2:
        curr_angle = np.mean([data_matrix[time_point, angle_dict["hip"][0]], data_matrix[time_point, angle_dict["hip"][1]]], axis=0)
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # IV -- CUTTED PARAMETERS
    # defining the parameters which are cutted throughout myoMOTION data
    # -------------------------------------------------------------------------
    Fz = Fz_tot[time_point]
    impulse = impulse_tot[time_point]
    power = power_tot[time_point]
    speed = speed_tot[time_point]
    power_rel_myo = power_rel[time_point]


    # reshaping variables in form "data x 1"
    curr_angle, Fz, speed, impulse, power = curr_angle.reshape(len(curr_angle),1), Fz.reshape(len(curr_angle),1), speed.reshape(len(curr_angle),1), impulse.reshape(len(curr_angle),1), power.reshape(len(curr_angle),1)
    Fz_tot, speed_tot, impulse_tot, power_tot = Fz_tot.reshape(len(Fz_tot),1), speed_tot.reshape(len(Fz_tot),1), impulse_tot.reshape(len(Fz_tot),1), power_tot.reshape(len(Fz_tot),1)
    power_rel, power_rel_myo = power_rel.reshape(len(Fz_tot),1), power_rel_myo.reshape(len(curr_angle),1)
    return [curr_angle,Fz,Fz_tot,speed,speed_tot,impulse,impulse_tot,power,power_tot,power_rel,power_rel_myo]
    # -------------------------------------------------------------------------



# ----------------------------------------------------------------------------------------
# PLOT DATA
# ----------------------------------------------------------------------------------------
def plot_data(force_myo, impulse_myo, speed_myo, power_myo, curr_angle, force_tot, impulse_tot, speed_tot, power_tot,
              plotselection, plotcut, plotall_myo, plotall_tot):

    # setting time points for cutting data
    t_unload_tot, t_unload_myo = np.where(force_tot < 10)[0][0], np.where(force_myo < 10)[0][0]
    minus_myo = round(len(force_myo)*0.17)
    cut_tot, cut_myo = np.argmax(force_tot[(t_unload_tot - 400):t_unload_tot]), np.argmax(force_myo[t_unload_myo-minus_myo:t_unload_myo])
    cut_tot, cut_myo = t_unload_tot - (400 - cut_tot), t_unload_myo - (minus_myo - cut_myo)

    # defining time ranges for x-Axis
    time_tot, time_myo = np.arange(0,len(force_tot)), np.arange(0,len(force_myo))

    if plotcut == 1: # cutted plots - till first force maximum
        if plotall_tot == 1:
            fig1 = plt.figure("Alle Plots - geschnitten (Kistler-basiert)")

            f_tot_plot = fig1.add_subplot(221)
            f_tot_plot = plt.ylabel("N"),plt.xlabel("t [Hz]"),plt.title("Kraft")
            f_tot_plot = plt.plot(time_tot[0:cut_tot],force_tot[0:cut_tot])

            p_tot_plot = fig1.add_subplot(222)
            p_tot_plot = plt.ylabel("Ns"),plt.xlabel("t [Hz]"),plt.title("Impuls")
            p_tot_plot = plt.plot(time_tot[0:cut_tot],impulse_tot[0:cut_tot])

            v_tot_plot = fig1.add_subplot(223)
            v_tot_plot = plt.ylabel("m/s"),plt.xlabel("t [Hz]"),plt.title("Geschwindigkeit")
            v_tot_plot = plt.plot(time_tot[0:cut_tot],speed_tot[0:cut_tot])

            w_Tot_plot = fig1.add_subplot(224)
            w_Tot_plot = plt.ylabel("W"),plt.xlabel("t [Hz]"),plt.title("Leistung")
            w_Tot_plot = plt.plot(time_tot[0:cut_tot],power_tot[0:cut_tot])

        elif plotall_myo == 1:
            fig2 = plt.figure("Alle Plots - geschnitten (myoMOTION-basiert)")

            f_tot_plot = fig2.add_subplot(221)
            f_tot_plot = plt.ylabel("N"),plt.xlabel("t [Hz]"),plt.title("Kraft")
            f_tot_plot = plt.plot(time_myo[0:cut_myo],force_myo[0:cut_myo])

            p_tot_plot = fig2.add_subplot(222)
            p_tot_plot = plt.ylabel("Ns"),plt.xlabel("t [Hz]"),plt.title("Impuls")
            p_tot_plot = plt.plot(time_myo[0:cut_myo],impulse_myo[0:cut_myo])

            v_tot_plot = fig2.add_subplot(223)
            v_tot_plot = plt.ylabel("m/s"),plt.xlabel("t [Hz]"),plt.title("Geschwindigkeit")
            v_tot_plot = plt.plot(time_myo[0:cut_myo],speed_myo[0:cut_myo])

            w_Tot_plot = fig2.add_subplot(224)
            w_Tot_plot = plt.ylabel("W"),plt.xlabel("t [Hz]"),plt.title("Leistung")
            w_Tot_plot = plt.plot(time_myo[0:cut_myo],power_myo[0:cut_myo])

        elif plotselection == 1:
            plt.figure("Kraft - geschnitten (myoMOTION-basiert)")
            plt.ylabel("N"), plt.xlabel("t [deg]"), plt.title("Kraft")
            plt.plot(time_myo[0:cut_myo], force_myo[0:cut_myo])
        elif plotselection == 2:
            plt.figure("Impuls - geschnitten (myoMOTION-basiert)")
            plt.ylabel("Ns"), plt.xlabel("t [deg]"), plt.title("Impuls")
            plt.plot(time_myo[0:cut_myo], impulse_myo[0:cut_myo])
        elif plotselection == 3:
            plt.figure("Geschwindigkeit - geschnitten (myoMOTION-basiert)")
            plt.ylabel("m/s"), plt.xlabel("t [deg]"), plt.title("Geschwindigkeit")
            plt.plot(time_myo[0:cut_myo], speed_myo[0:cut_myo])
        elif plotselection == 4:
            plt.figure("Leistung - geschnitten (myoMOTION-basiert)")
            plt.ylabel("W"), plt.xlabel("t [deg]"), plt.title("Leistung")
            plt.plot(time_myo[0:cut_myo], power_myo[0:cut_myo])
        elif plotselection == 5:
            plt.figure("Kraft - geschnitten (Kistler-basiert)")
            plt.ylabel("N"), plt.xlabel("t [Hz]"), plt.title("Kraft")
            plt.plot(time_tot[0:cut_tot], force_tot[0:cut_tot])
        elif plotselection == 6:
            plt.figure("Impuls - geschnitten (Kistler-basiert)")
            plt.ylabel("Ns"), plt.xlabel("t [Hz]"), plt.title("Impuls")
            plt.plot(time_tot[0:cut_tot], impulse_tot[0:cut_tot])
        elif plotselection == 7:
            plt.figure("Geschwindigkeit - geschnitten (Kistler-basiert)")
            plt.ylabel("m/s"), plt.xlabel("t [Hz]"), plt.title("Geschwindigkeit")
            plt.plot(time_tot[0:cut_tot], speed_tot[0:cut_tot])
        elif plotselection == 8:
            plt.figure("Leistung - geschnitten (Kistler-basiert)")
            plt.ylabel("W"), plt.xlabel("t [Hz]"), plt.title("Leistung")
            plt.plot(time_tot[0:cut_tot], power_tot[0:cut_tot])


    elif plotcut == 2: # uncutted plots - whole Data stream either Kistler or myoMOTION based

        if plotall_tot == 1:
            fig3 = plt.figure("Alle Plots - ungeschnitten (Kistler-basiert)")
#            fig3 = plt.figure("plots")

            f_tot_plot = fig3.add_subplot(221)
            f_tot_plot = plt.ylabel("N"),plt.xlabel("t [Hz]"),plt.title("Kraft")
            f_tot_plot = plt.plot(time_tot,force_tot)

            p_tot_plot = fig3.add_subplot(222)
            p_tot_plot = plt.ylabel("Ns"),plt.xlabel("t [Hz]"),plt.title("Impuls")
            p_tot_plot = plt.plot(time_tot,impulse_tot)

            v_tot_plot = fig3.add_subplot(223)
            v_tot_plot = plt.ylabel("m/s"),plt.xlabel("t [Hz]"),plt.title("Geschwindigkeit")
            v_tot_plot = plt.plot(time_tot,speed_tot)

            w_Tot_plot = fig3.add_subplot(224)
            w_Tot_plot = plt.ylabel("W"),plt.xlabel("t [Hz]"),plt.title("Leistung")
            w_Tot_plot = plt.plot(time_tot,power_tot)

        elif plotall_myo == 1:
            fig4 = plt.figure("Alle Plots - ungeschnitten (myoMOTION-basiert)")

            f_tot_plot = fig4.add_subplot(221)
            f_tot_plot = plt.ylabel("N"),plt.xlabel("t [deg]"),plt.title("Kraft")
            f_tot_plot = plt.plot(time_myo,force_myo)

            p_tot_plot = fig4.add_subplot(222)
            p_tot_plot = plt.ylabel("Ns"),plt.xlabel("t [deg]"),plt.title("Impuls")
            p_tot_plot = plt.plot(time_myo,impulse_myo)

            v_tot_plot = fig4.add_subplot(223)
            v_tot_plot = plt.ylabel("m/s"),plt.xlabel("t [deg]"),plt.title("Geschwindigkeit")
            v_tot_plot = plt.plot(time_myo,speed_myo)

            w_Tot_plot = fig4.add_subplot(224)
            w_Tot_plot = plt.ylabel("W"),plt.xlabel("t [deg]"),plt.title("Leistung")
            w_Tot_plot = plt.plot(time_myo,power_myo)

        elif plotselection == 1:
            plt.figure("Kraft - ungeschnitten (myoMOTION-basiert)")
            plt.ylabel("N"), plt.xlabel("t [deg]"), plt.title("Kraft")
            plt.plot(time_myo, force_myo)
        elif plotselection == 2:
            plt.figure("Impuls - ungeschnitten (myoMOTION-basiert)")
            plt.ylabel("Ns"), plt.xlabel("t [deg]"), plt.title("Impuls")
            plt.plot(time_myo, impulse_myo)
        elif plotselection == 3:
            plt.figure("Geschwindigkeit - ungeschnitten (myoMOTION-basiert)")
            plt.ylabel("m/s"), plt.xlabel("t [deg]"), plt.title("Geschwindigkeit")
            plt.plot(time_myo, speed_myo)
        elif plotselection == 4:
            plt.figure("Leistung - ungeschnitten (myoMOTION-basiert)")
            plt.ylabel("W"), plt.xlabel("t [deg]"), plt.title("Leistung")
            plt.plot(time_myo, power_myo)
        elif plotselection == 5:
            plt.figure("Kraft - ungeschnitten (Kistler-basiert)")
            plt.ylabel("N"), plt.xlabel("t [Hz]"), plt.title("Kraft")
            plt.plot(time_tot, force_tot)
        elif plotselection == 6:
            plt.figure("Impuls - ungeschnitten (Kistler-basiert)")
            plt.ylabel("Ns"), plt.xlabel("t [Hz]"), plt.title("Impuls")
            plt.plot(time_tot, impulse_tot)
        elif plotselection == 7:
            plt.figure("Geschwindigkeit - ungeschnitten (Kistler-basiert)")
            plt.ylabel("m/s"), plt.xlabel("t [Hz]"), plt.title("Geschwindigkeit")
            plt.plot(time_tot, speed_tot)
        elif plotselection == 8:
            plt.figure("Leistung - ungeschnitten (Kistler-basiert)")
            plt.ylabel("W"), plt.xlabel("t [Hz]"), plt.title("Leistung")
            plt.plot(time_tot, power_tot)


    plt.legend()
    plt.show()


# ----------------------------------------------------------------------------------------
# EXPORT DATA
# ----------------------------------------------------------------------------------------
def export_data(export_name, curr_angle, force_myo, impulse_myo, speed_myo, power_myo,
                force_tot, impulse_tot, speed_tot, power_tot, power_rel_tot, power_rel_myo):

    # setting time points for cutting data
    cut_tot, cut_myo = np.argmax(force_tot[0:np.argmax(speed_tot)]), np.argmax(force_myo[0:np.argmax(speed_myo)])
    Fz_tot_max, impulse_tot_max,speed_tot_max,power_tot_max = np.max(force_tot[0:np.argmax(speed_tot)]), np.max(impulse_tot), np.max(speed_tot), np.max(power_tot)
    Fz_myo_max, impulse_myo_max,speed_myo_max,power_myo_max = np.max(force_myo[0:np.argmax(speed_myo)]), np.max(impulse_myo), np.max(speed_myo), np.max(power_myo)
    power_rel_tot_max, power_rel_myo_max = np.max(power_rel_tot), np.max(power_rel_myo)
    tot_max, tot_myo = [Fz_tot_max, impulse_tot_max,speed_tot_max,power_tot_max,power_rel_tot_max], [Fz_myo_max, impulse_myo_max,speed_myo_max,power_myo_max,power_rel_myo_max]
    tot_max, tot_myo = np.array(tot_max), np.array(tot_myo)
    tot_max, tot_myo = tot_max.round(decimals=3), tot_myo.round(decimals=3)

    # calculation jump height using flight time method
    t1, t2 = np.where(force_tot < 10)[0][0], np.where(force_tot < 10)[0][-1]
    delta_t = (t2 - t1) / 1500
    height = 9.81 * (0.5*delta_t)**2 * 0.5
    height = round(height, 3)

    # date and time values for file header specs
    date = str(dt.now())
    date = date.split(' ')

    # combining the huge single arrays to one huge array
    time_range = np.arange(len(force_tot))
    time_range = time_range.reshape(len(time_range),1)
    all_tot = np.concatenate((time_range, force_tot, impulse_tot, speed_tot, power_tot, power_rel_tot), axis=1)
    all_myo = np.concatenate((curr_angle, force_myo, impulse_myo, speed_myo, power_myo, power_rel_myo), axis=1)
#    all_tot, all_myo = all_tot.round(decimals=3), all_myo.round(decimals=3)

    with open(export_name+'.csv', 'w+') as fileID:
        fileID.write("Datum\t" + date[0] + "\nZeit\t" + date[1].split('.')[0] + "\n\n")
        fileID.write("KSP-h(max)[m]\tZeile-Schnitt(alle_Daten)\tZeile_Schnitt(MM-Daten)\n" + str(height) +"\t" + str(cut_tot) + "\t" + str(cut_myo)+"\n\n\n" +
                    "Kistler-basierte Maximalwerte\n")
        fileID.write("Fz_max[N]\tI_max[Ns]\tv_max[m/s]\tP_abs_max[W]\tP_rel_max[W]\n")
        tot_max.tofile(fileID, sep="\t", format="%s")
        fileID.write("\n" + "myoMOTION-basierte Maximalwerte\n")
        fileID.write("Fz_max[N]\tI_max[Ns]\tv_max[m/s]\tP_abs_max[W]\tP_rel_max[W]\n")
        tot_myo.tofile(fileID, sep="\t", format="%s")
        fileID.write("\n\n\n")

    all_tot, all_myo = np.round(all_tot, 3), np.round(all_myo, 3)
    with open(export_name+'.csv', 'ab') as output:
        np.savetxt(output, all_tot, delimiter="\t", header = "Zeit[Hz]\tKraft[N]\tImpuls[Ns]\tGeschw[m/s]\tP_abs[W]\tP_rel[W]", fmt="%f")
        np.savetxt(output, all_myo, delimiter="\t", header = "\n\n\nWinkel[°]\tKraft[N]\tImpuls[Ns]\tGeschw[m/s]\tP_abs[W]\tP_rel[W]", fmt="%f")
