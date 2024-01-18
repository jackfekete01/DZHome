# Libraries
import tkinter as tk
from tkinter import ttk
from tkinter import font
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import detritalpy.detritalFuncs as dFunc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import os
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import matplotlib as mpl
import seaborn as sns
from sklearn.manifold import MDS
import detritalpy.MDAfuncs as MDA
import matplotlib.patches as patches
import math
from scipy import stats
from random import choices
from random import randrange
from random import randint
import random
import time

# Plots only appear within the Tkinter window
%matplotlib agg

class DZPlotApp:
    def __init__(self):
        self.user_input = ''
        self.user_dataFrame = ''
        self.selected_samples = ''
        self.selected_options = ''
        self.bandwidth = 10
        self.sample_plots_array = ''
        self.main_window = None

        self.create_data_load_window()

    def close_input_window(self):
        self.data_load.destroy()

    def load_excel_file(self, user_input):
        try:
            if user_input:
                self.user_dataFrame = pd.read_excel(user_input)
                print('File found within directory.')
                self.close_input_window()
                self.create_main_portal()
        except FileNotFoundError:
            print('File not found in directory.')

    def get_data_input(self):
        self.user_input = self.data_load_entry.get()
        print('User entered:', self.user_input)
        self.load_excel_file(self.user_input)

    def create_data_load_window(self):
        self.data_load = tk.Tk()
        self.data_load.title('DZHome - Data Input')
        self.data_load.geometry('500x75')

        data_load_text = tk.Label(self.data_load, text='Please enter the name of the excel file below. File must end with "xlsx".')
        data_load_text.place(x=10, y=10)

        # self.data_load_entry = tk.Entry(self.data_load, width=65)
        # self.data_load_entry.place(x=10, y=35)
        
        excel_files = [file for file in os.listdir() if file.endswith('.xlsx')]
        
        # Create a StringVar to store the selected file
        selected_file = tk.StringVar()
        
        # Create a dropdown menu (Combobox) with the list of Excel files
        data_load_dropdown = ttk.Combobox(self.data_load, textvariable=selected_file, values=excel_files, width=62)
        data_load_dropdown.place(x=10, y=35)
        
        def get_data_input():
            # Retrieve the selected file from the Combobox
            user_input = selected_file.get()

            # You can proceed with loading the selected Excel file here
            self.load_excel_file(user_input)

        data_load_button = tk.Button(self.data_load, text='Load Data', width=10, command=get_data_input)
        data_load_button.place(x=410, y=31)

        self.data_load.mainloop()
        
    def DZPlot(self):
        global user_dataFrame
        # Define functtions
        #########################################################
        #########################################################
        #########################################################
        def get_samples():
            global user_dataFrame
            df = self.user_dataFrame.copy()
            all_samples = list(set(list(df['Sample ID'])))

            # set up a new window
            sample_window = tk.Toplevel()
            sample_window.title('Sample Selection')

            # set up check lists
            checkbox_vars = []
            for i,sample in enumerate(all_samples):
                var = tk.IntVar()
                checkbox = tk.Checkbutton(sample_window, text=sample, variable=var)
                checkbox.grid(row=i, column = 0, sticky = 'w')
                checkbox_vars.append(var)

            def submit_samples():
                global selected_samples
                selected_samples = [sample for sample, var in zip(all_samples, checkbox_vars) if var.get() == 1]
                sample_window.destroy()

            submit_button = tk.Button(sample_window, text='Submit', command=submit_samples)
            submit_button.grid(row=len(all_samples), column=0, pady=10)

        def plot_type_changed():
            # Disable other checkboxes based on the selected plot type
            if plot_type_var.get() == "KDE":
                PDP_check.deselect()
                CDF_check.deselect()
            elif plot_type_var.get() == "PDP":
                KDE_check.deselect()
                CDF_check.deselect()
            elif plot_type_var.get() == "CDF":
                KDE_check.deselect()
                PDP_check.deselect()

        def get_plotting_options():
            global selected_options
            global bandwidth
            selected_options = []

            # Check the state of each plotting option checkbox
            if plot_type_var.get() == 'KDE':
                selected_options.append(('KDE',bw_entry.get()))
            elif plot_type_var.get() == 'PDP':
                selected_options.append(('PDP',0))
            elif plot_type_var.get() == 'CDF':
                selected_options.append(('CDF',0))

            return selected_options

        def get_plotting_arrays(selected_options,selected_samples):
            global graph_hold
            graph_hold = []
            for i,sample in enumerate(selected_samples):
                group = self.user_dataFrame.groupby('Sample ID')
                grouped = group.get_group(sample)
                ages = list(grouped['Best age'])
                errors = list(grouped['±'])
                option_type = selected_options[0][0]
                if option_type == 'KDE':
                    if selected_options[0][1] is None or selected_options[0][1] == '':
                        bw = 15
                    else:
                        bw = int(selected_options[0][1])
                    KDE_age, KDE = dFunc.KDEcalcAges([ages],x1=0, x2=4500, xdif=1, bw=bw, bw_x=None, cumulative=False)
                    graph_hold.append(KDE[0])

                if option_type == 'PDP':
                    PDP_age, PDP = dFunc.PDPcalcAges([ages], [errors], x1=0, x2=4500, xdif=1, cumulative=False)
                    graph_hold.append(PDP[0])

                if option_type == 'CDF':
                    CDF_age, CDF = dFunc.CDFcalcAges([ages], x1=0, x2=4500, xdif=1)
                    graph_hold.append(CDF[0])
            return graph_hold

        def get_dimensions():
            x_bound = x_bound_entry.get().strip() or None
            if x_bound is not None:
                x_bound = x_bound.split(',')
            y_bound = y_bound_entry.get().strip() or None
            if y_bound is not None:
                y_bound = y_bound.split(',')
            height = height_entry.get().strip() or None
            width = width_entry.get().strip() or None
            return [x_bound, y_bound, height, width]

        def color_scheme():
            # Open a new window
            color_scheme_window = tk.Toplevel()
            color_scheme_window.title('Color Scheme Selection')
            color_scheme_window.geometry('820x370')

            # Frame on the right side
            side_frame = tk.Frame(color_scheme_window, bg='white', width=400, height=300, bd=1, relief=tk.SOLID)
            side_frame.place(x=165,y=10)

            # Dropdown menu for colormap selection
            colormap_var = tk.StringVar()
            colormap_options = ['Pastel1', 'Pastel2', 'Paired', 'Accent', 'Dark2', 'Set1', 'Set2', 'Set3',
                                'tab10', 'tab20', 'tab20b', 'tab20c']

            colormap_label = tk.Label(color_scheme_window, text='Select Colormap:', font=('Arial', 10))
            colormap_label.place(x=10, y=10)

            colormap_dropdown = tk.OptionMenu(color_scheme_window, colormap_var, *colormap_options)
            colormap_dropdown.place(x=10, y=30)

            cmaps = {}

            gradient = np.linspace(0, 1, 256)
            gradient = np.vstack((gradient, gradient))

            def plot_color_gradients(category, cmap_list):
                # Create figure and adjust figure height to number of colormaps
                nrows = len(cmap_list)
                figh = 0.35 + 0.15 + (nrows + (nrows - 1) * 0.1) * 0.22
                fig, axs = plt.subplots(nrows=nrows + 1, figsize=(6.4, figh))
                fig.subplots_adjust(top=1 - 0.35 / figh, bottom=0.15 / figh,
                                    left=0.2, right=0.99)
                axs[0].set_title(f'{category} colormaps', fontsize=14)

                for ax, name in zip(axs, cmap_list):
                    ax.imshow(gradient, aspect='auto', cmap=mpl.cm.get_cmap(name))
                    ax.text(-0.01, 0.5, name, va='center', ha='right', fontsize=10,
                            transform=ax.transAxes)

                # Turn off *all* ticks & spines, not just the ones with colormaps.
                for ax in axs:
                    ax.set_axis_off()

                # Save colormap list for later.
                cmaps[category] = cmap_list

                # Embed the plot in the Tkinter window
                canvas = FigureCanvasTkAgg(fig, master=side_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

            plot_color_gradients('Qualitative',
                             ['Pastel1', 'Pastel2', 'Paired', 'Accent', 'Dark2',
                              'Set1', 'Set2', 'Set3', 'tab10', 'tab20', 'tab20b',
                              'tab20c'])

            def submit_color():
                global selected_colormap
                selected_colormap = colormap_var.get()
                color_scheme_window.destroy()

            # Submit button
            submit_button = tk.Button(color_scheme_window, text='Submit', command=submit_color)
            submit_button.place(x=10, y=320)

        def color_age_clean():
            cuts_raw = bins_entry.get().strip().split(',')
            colors_raw = colors_entry.get().strip().split(',')
            cuts_final = []
            for i in range(len(cuts_raw)):
                cuts_final.append(int(cuts_raw[i]))
            colors_final = []
            for i in range(len(colors_raw)):
                colors_final.append(str(colors_raw[i]))
            return [cuts_final,colors_final]

        def custom_color_clean():
            colors = color_order_entry.get().strip().split(',')
            colors_final = []
            for i in range(len(colors)):
                colors_final.append(str(colors[i]))
            return colors_final


        def generate_preview():
            selected_options = get_plotting_options()
            dimensions = get_dimensions()
            # set defaults
            if dimensions[2] is None:
                dimensions[2] = 6
            if dimensions[3] is None:
                dimensions[3] = 9
            
            global selected_samples
            sample_arrays = get_plotting_arrays(selected_options,selected_samples)

            # Color selection
            select_color_option_value = select_color_option.get()
            if select_color_option_value == 'by_sample':
                global selected_colormap
                colormap = plt.get_cmap(selected_colormap)
                colors = [colormap(i) for i in np.linspace(0, 1, len(selected_samples))]

                # Clear the contents of temp_frame
                for widget in temp_frame.winfo_children():
                    widget.destroy()
                #global sample_arrays
                #sample_arrays = get_plotting_arrays(selected_options)
                #print('Sample Arrays:',sample_arrays)
                # Now to plot
                if selected_options and selected_samples:
                    x1 = np.arange(0,4501)
                    if selected_options[0][0] == 'PDP' or selected_options[0][0] == 'KDE':
                        if len(selected_samples)>1:

                            fig, ax = plt.subplots(len(sample_arrays),sharex=True,figsize =(int(dimensions[3]),int(dimensions[2])) )
                            for i, sample_array in enumerate(sample_arrays):
                                ax[i].plot(sample_array, label=selected_samples[i],color=colors[i])
                                ax[i].fill_between(x1,sample_array,alpha=0.75,color=colors[i])
                                ax[i].legend()
                                ax[i].grid(alpha=0.5)
                                if dimensions[1] is not None or '':
                                    ax[i].set_ylim((float(dimensions[1][0]),float(dimensions[1][1])))
                            plt.xlabel('Age (Ma)')
                            if dimensions[0] is not None or '':
                                plt.xlim((int(dimensions[0][0]),int(dimensions[0][1])))

                            # Embed the plot in the Tkinter window
                            canvas = FigureCanvasTkAgg(fig, master=temp_frame)
                            canvas.draw()
                            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.NONE, expand=1)

                            # Add Matplotlib toolbar for zooming
                            toolbar_frame = tk.Frame(master=temp_frame)
                            toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
                            toolbar.update()
                            toolbar_frame.pack(side=tk.TOP, fill=tk.NONE, expand=0)

                            # Disable frame propagation
                            temp_frame.pack_propagate(False)

                            def on_key(event):
                                if event.key == "q":
                                    plt.close(fig)

                            canvas.mpl_connect("key_press_event", on_key)
                        else:

                            fig,ax = plt.subplots(len(sample_arrays),figsize =(int(dimensions[3]),int(dimensions[2])))
                            for i, sample_array in enumerate(sample_arrays):
                                ax.plot(sample_array, label=selected_samples[i],color=colors[i])
                                ax.fill_between(x1,sample_array,alpha=0.75,color=colors[i])
                                ax.legend()
                                ax.grid(alpha=0.5)
                            plt.xlabel('Age (Ma)')
                            if dimensions[0] is not None or '':
                                plt.xlim((int(dimensions[0][0]),int(dimensions[0][1])))
                            if dimensions[1] is not None or '':
                                plt.ylim((float(dimensions[1][0]),float(dimensions[1][1])))

                            # Embed the plot in the Tkinter window
                            canvas = FigureCanvasTkAgg(fig, master=temp_frame)
                            canvas.draw()
                            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.NONE, expand=1)

                            # Add Matplotlib toolbar for zooming
                            toolbar_frame = tk.Frame(master=temp_frame)
                            toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
                            toolbar.update()
                            toolbar_frame.pack(side=tk.TOP, fill=tk.NONE, expand=0)

                            # Disable frame propagation
                            temp_frame.pack_propagate(False)

                            def on_key(event):
                                if event.key == "q":
                                    plt.close(fig)

                            canvas.mpl_connect("key_press_event", on_key)
                    else:

                        fig, ax = plt.subplots(figsize =(int(dimensions[3]),int(dimensions[2])))
                        for i, sample_array in enumerate(sample_arrays):
                            ax.plot(sample_array, label=selected_samples[i],color=colors[i])
                            ax.legend()
                            ax.grid(alpha=0.5)
                        plt.xlabel('Age (Ma)')
                        if dimensions[0] is not None or '':
                            plt.xlim((int(dimensions[0][0]),int(dimensions[0][1])))

                        # Embed the plot in the Tkinter window
                        canvas = FigureCanvasTkAgg(fig, master=temp_frame)
                        canvas.draw()
                        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.NONE, expand=0)

                        # Add Matplotlib toolbar for zooming
                        toolbar_frame = tk.Frame(master=temp_frame)
                        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
                        toolbar.update()
                        toolbar_frame.pack(side=tk.TOP, fill=tk.NONE, expand=0)

                        # Disable frame propagation
                        temp_frame.pack_propagate(False)

                        def on_key(event):
                            if event.key == "q":
                                plt.close(fig)

                        canvas.mpl_connect("key_press_event", on_key)

            if select_color_option_value == 'by_age':
                age_params = color_age_clean()
                cuts = age_params[0]
                colors = age_params[1]

                # Clear the contents of temp_frame
                for widget in temp_frame.winfo_children():
                    widget.destroy()

                # Clear up colors and cuts
                cuts.append(4500)
                colors.append(colors[-1])
                # Get the arrays
                #sample_arrays = get_plotting_arrays(selected_options)

                # Now to plot
                if selected_options and selected_samples:
                    x1 = np.arange(0,4501)
                    if selected_options[0][0] == 'PDP' or selected_options[0][0] == 'KDE':
                        if len(selected_samples)>1:

                            fig, ax = plt.subplots(len(sample_arrays),sharex=True,figsize =(int(dimensions[3]),int(dimensions[2])) )
                            for i, sample_array in enumerate(sample_arrays):
                                for w in range(len(cuts)-1):
                                    label = selected_samples[i] if w==0 else '_nolegend_'
                                    ax[i].plot(x1[cuts[w]:cuts[w+1]],sample_array[cuts[w]:cuts[w+1]], label=label,color=colors[w])
                                    ax[i].fill_between(x1[cuts[w]:cuts[w+1]],sample_array[cuts[w]:cuts[w+1]],alpha=0.75,color=colors[w])
                                ax[i].legend(handlelength=0)
                                ax[i].grid(alpha=0.5)
                                if dimensions[1] is not None or '':
                                    ax[i].set_ylim((float(dimensions[1][0]),float(dimensions[1][1])))
                            plt.xlabel('Age (Ma)')
                            if dimensions[0] is not None or '':
                                plt.xlim((int(dimensions[0][0]),int(dimensions[0][1])))

                            # Embed the plot in the Tkinter window
                            canvas = FigureCanvasTkAgg(fig, master=temp_frame)
                            canvas.draw()
                            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.NONE, expand=1)

                            # Add Matplotlib toolbar for zooming
                            toolbar_frame = tk.Frame(master=temp_frame)
                            toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
                            toolbar.update()
                            toolbar_frame.pack(side=tk.TOP, fill=tk.NONE, expand=0)

                            # Disable frame propagation
                            temp_frame.pack_propagate(False)

                            def on_key(event):
                                if event.key == "q":
                                    plt.close(fig)

                            canvas.mpl_connect("key_press_event", on_key)
                        else:

                            fig,ax = plt.subplots(len(sample_arrays),figsize =(int(dimensions[3]),int(dimensions[2])))
                            for i, sample_array in enumerate(sample_arrays):
                                for w in range(len(cuts)-1):
                                    label = selected_samples[i] if w==0 else '_nolegend_'
                                    ax.plot(x1[cuts[w]:cuts[w+1]],sample_array[cuts[w]:cuts[w+1]], label=label,color=colors[w])
                                    ax.fill_between(x1[cuts[w]:cuts[w+1]],sample_array[cuts[w]:cuts[w+1]],alpha=0.75,color=colors[w])
                                ax.legend(handlelength=0)
                                ax.grid(alpha=0.5)
                            plt.xlabel('Age (Ma)')
                            if dimensions[0] is not None or '':
                                plt.xlim((int(dimensions[0][0]),int(dimensions[0][1])))
                            if dimensions[1] is not None or '':
                                plt.ylim((float(dimensions[1][0]),float(dimensions[1][1])))

                            # Embed the plot in the Tkinter window
                            canvas = FigureCanvasTkAgg(fig, master=temp_frame)
                            canvas.draw()
                            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.NONE, expand=1)

                            # Add Matplotlib toolbar for zooming
                            toolbar_frame = tk.Frame(master=temp_frame)
                            toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
                            toolbar.update()
                            toolbar_frame.pack(side=tk.TOP, fill=tk.NONE, expand=0)

                            # Disable frame propagation
                            temp_frame.pack_propagate(False)

                            def on_key(event):
                                if event.key == "q":
                                    plt.close(fig)

                            canvas.mpl_connect("key_press_event", on_key)
                    else:

                        fig, ax = plt.subplots(figsize =(int(dimensions[3]),int(dimensions[2])))
                        line_styles = [(0, ()),(0, (1, 1)),(0, (1, 10)),
                                      (0, (1, 1)),(5, (10, 3)),(0, (5, 10)),
                                      (0, (5, 5)),(0, (5, 1)),(0, (3, 10, 1, 10)),
                                      (0, (3, 5, 1, 5)),(0, (3, 1, 1, 1)),(0, (3, 5, 1, 5, 1, 5)),
                                      (0, (3, 10, 1, 10, 1, 10)),(0, (3, 1, 1, 1, 1, 1))]
                        for i, sample_array in enumerate(sample_arrays):
                            for w in range(len(cuts)-1):
                                label = selected_samples[i] if w==0 else '_nolegend_'
                                ax.plot(x1[cuts[w]:cuts[w+1]],sample_array[cuts[w]:cuts[w+1]], label=label,color=colors[w],linestyle=line_styles[i])
                                ax.legend()
                                ax.grid(alpha=0.5)
                        plt.xlabel('Age (Ma)')
                        if dimensions[0] is not None or '':
                            plt.xlim((int(dimensions[0][0]),int(dimensions[0][1])))

                        # Embed the plot in the Tkinter window
                        canvas = FigureCanvasTkAgg(fig, master=temp_frame)
                        canvas.draw()
                        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.NONE, expand=0)

                        # Add Matplotlib toolbar for zooming
                        toolbar_frame = tk.Frame(master=temp_frame)
                        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
                        toolbar.update()
                        toolbar_frame.pack(side=tk.TOP, fill=tk.NONE, expand=0)

                        # Disable frame propagation
                        temp_frame.pack_propagate(False)

                        def on_key(event):
                            if event.key == "q":
                                plt.close(fig)

                        canvas.mpl_connect("key_press_event", on_key)

            if select_color_option_value == 'custom':

                colors = custom_color_clean()

                while len(colors) < len(selected_samples):
                    colors.append('tab:blue')

                # Clear the contents of temp_frame
                for widget in temp_frame.winfo_children():
                    widget.destroy()

                #sample_arrays = get_plotting_arrays(selected_options,selected_samples)
                # Now to plot
                if selected_options and selected_samples:
                    x1 = np.arange(0,4501)
                    if selected_options[0][0] == 'PDP' or selected_options[0][0] == 'KDE':
                        if len(selected_samples)>1:

                            fig, ax = plt.subplots(len(sample_arrays),sharex=True,figsize =(int(dimensions[3]),int(dimensions[2])) )
                            for i, sample_array in enumerate(sample_arrays):
                                ax[i].plot(sample_array, label=selected_samples[i],color=colors[i])
                                ax[i].fill_between(x1,sample_array,alpha=0.75,color=colors[i])
                                ax[i].legend()
                                ax[i].grid(alpha=0.5)
                                if dimensions[1] is not None or '':
                                    ax[i].set_ylim((float(dimensions[1][0]),float(dimensions[1][1])))
                            plt.xlabel('Age (Ma)')
                            if dimensions[0] is not None or '':
                                plt.xlim((int(dimensions[0][0]),int(dimensions[0][1])))

                            # Embed the plot in the Tkinter window
                            canvas = FigureCanvasTkAgg(fig, master=temp_frame)
                            canvas.draw()
                            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.NONE, expand=1)

                            # Add Matplotlib toolbar for zooming
                            toolbar_frame = tk.Frame(master=temp_frame)
                            toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
                            toolbar.update()
                            toolbar_frame.pack(side=tk.TOP, fill=tk.NONE, expand=0)

                            # Disable frame propagation
                            temp_frame.pack_propagate(False)

                            def on_key(event):
                                if event.key == "q":
                                    plt.close(fig)

                            canvas.mpl_connect("key_press_event", on_key)
                        else:

                            fig,ax = plt.subplots(len(sample_arrays),figsize =(int(dimensions[3]),int(dimensions[2])))
                            for i, sample_array in enumerate(sample_arrays):
                                ax.plot(sample_array, label=selected_samples[i],color=colors[i])
                                ax.fill_between(x1,sample_array,alpha=0.75,color=colors[i])
                                ax.legend()
                                ax.grid(alpha=0.5)
                            plt.xlabel('Age (Ma)')
                            if dimensions[0] is not None or '':
                                plt.xlim((int(dimensions[0][0]),int(dimensions[0][1])))
                            if dimensions[1] is not None or '':
                                plt.ylim((float(dimensions[1][0]),float(dimensions[1][1])))

                            # Embed the plot in the Tkinter window
                            canvas = FigureCanvasTkAgg(fig, master=temp_frame)
                            canvas.draw()
                            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.NONE, expand=1)

                            # Add Matplotlib toolbar for zooming
                            toolbar_frame = tk.Frame(master=temp_frame)
                            toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
                            toolbar.update()
                            toolbar_frame.pack(side=tk.TOP, fill=tk.NONE, expand=0)

                            # Disable frame propagation
                            temp_frame.pack_propagate(False)

                            def on_key(event):
                                if event.key == "q":
                                    plt.close(fig)

                            canvas.mpl_connect("key_press_event", on_key)
                    else:

                        fig, ax = plt.subplots(figsize =(int(dimensions[3]),int(dimensions[2])))
                        for i, sample_array in enumerate(sample_arrays):
                            ax.plot(sample_array, label=selected_samples[i],color=colors[i])
                            ax.legend()
                            ax.grid(alpha=0.5)
                        plt.xlabel('Age (Ma)')
                        if dimensions[0] is not None or '':
                            plt.xlim((int(dimensions[0][0]),int(dimensions[0][1])))

                        # Embed the plot in the Tkinter window
                        canvas = FigureCanvasTkAgg(fig, master=temp_frame)
                        canvas.draw()
                        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.NONE, expand=0)

                        # Add Matplotlib toolbar for zooming
                        toolbar_frame = tk.Frame(master=temp_frame)
                        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
                        toolbar.update()
                        toolbar_frame.pack(side=tk.TOP, fill=tk.NONE, expand=0)

                        # Disable frame propagation
                        temp_frame.pack_propagate(False)

                        def on_key(event):
                            if event.key == "q":
                                plt.close(fig)

                        canvas.mpl_connect("key_press_event", on_key)

        # Interface Layout
        #########################################################
        #########################################################
        #########################################################
        # Main plot window
        plot_window = tk.Toplevel()
        plot_window.title('DZHome - Plot Window')
        plot_window.geometry('1250x700')

        # Holding frame for plot preview
        temp_frame = tk.Frame(plot_window,width=865,height=650,borderwidth=1.,relief = 'solid')
        temp_frame.place(x=10,y=25)
        temp_frame.configure(bg='white')

        # Preview label
        preview_label = tk.Label(plot_window,text='Preview Window',font=('Arial',12))
        preview_label.place(x=275,y=0)

        # Sample select label
        sample_select_label = tk.Label(plot_window,text='1) Select Samples.',font=('Arial',11))
        sample_select_label.place(x=900,y=25)

        # Sample select button
        sample_select_button = tk.Button(plot_window,text='Select Samples',width=15,command=get_samples)
        sample_select_button.place(x=900,y=50)

        # Plot type label
        plot_type_label = tk.Label(plot_window,text='2) Select Plot Type.',font=('Arial',11))
        plot_type_label.place(x=900,y=100)

        # Plot type varialbe
        plot_type_var = tk.StringVar()

        # KDE checkbox
        KDE_check = tk.Radiobutton(plot_window,text='KDE',font=('Arial',10),variable=plot_type_var,command=plot_type_changed,value='KDE')
        KDE_check.place(x=900,y=125)

        # Bandwidth entry and label
        bw_entry = tk.Entry(plot_window,text='BW:',width=3,font=('Arial',10))
        bw_entry.place(x=930,y=150)
        bw_label = tk.Label(plot_window,text='BW:',font=('Arial',10))
        bw_label.place(x=900,y=150)

        # PDP checkbox
        PDP_check = tk.Radiobutton(plot_window,text='PDP',font=('Arial',10),variable=plot_type_var,command=plot_type_changed,value='PDP')
        PDP_check.place(x=975,y=125)

        # CDF checkbox
        CDF_check = tk.Radiobutton(plot_window,text='CDF',font=('Arial',10),variable=plot_type_var,command=plot_type_changed,value='CDF')
        CDF_check.place(x=1050,y=125)

        # Plot dimensions labels
        plot_dim_label = tk.Label(plot_window,text='3) Plot Dimensions:',font=('Arial',11))
        plot_dim_label.place(x=900,y=185)
        x_bound_label = tk.Label(plot_window,text='x-bounds:',font=('Arial',10))
        x_bound_label.place(x=900,y=210)
        x_bound_entry = tk.Entry(plot_window,width=12)
        x_bound_entry.place(x=965,y=210)

        y_bound_label = tk.Label(plot_window,text='y-bounds:',font=('Arial',10))
        y_bound_label.place(x=1045,y=210)
        y_bound_entry = tk.Entry(plot_window,width=12)
        y_bound_entry.place(x=1110,y=210)

        height_label = tk.Label(plot_window,text='height:',font=('Arial',10))
        height_label.place(x=900,y=240)
        height_entry = tk.Entry(plot_window,width=15)
        height_entry.place(x=945,y=240)

        width_label = tk.Label(plot_window,text='width:',font=('Arial',10))
        width_label.place(x=1045,y=240)
        width_entry = tk.Entry(plot_window,width=16)
        width_entry.place(x=1085,y=240)

        # Plot colors labels and entries
        plot_color_label = tk.Label(plot_window,text='4) Plot Colors:',font=('Arial',11))
        plot_color_label.place(x=900,y=275)

        select_color_option = tk.StringVar()

        color_by_sample_check = tk.Radiobutton(plot_window,text='Color by Sample',font=('Arial',11),variable=select_color_option,value='by_sample')
        color_by_sample_check.place(x=900,y=300)
        color_by_sample_button = tk.Button(plot_window,text='Select Color Scheme',width=15,command=color_scheme)
        color_by_sample_button.place(x=1045,y=300)

        color_by_age_check = tk.Radiobutton(plot_window,text='Color by Age',font=('Arial',11),variable=select_color_option,value='by_age')
        color_by_age_check.place(x=900,y=330)
        bins_label = tk.Label(plot_window,text='Age bins:',font=('Arial',10))
        bins_label.place(x=900,y=360)
        bins_entry = tk.Entry(plot_window,width=30)
        bins_entry.place(x=975,y=360)
        colors_label = tk.Label(plot_window,text='Colors:',font=('Arial',10))
        colors_label.place(x=900,y=385)
        colors_entry = tk.Entry(plot_window,width=30)
        colors_entry.place(x=975,y=385)

        custom_colors_check = tk.Radiobutton(plot_window,text='Custom Colors',font=('Arial',11),variable=select_color_option,value='custom')
        custom_colors_check.place(x=900,y=410)
        color_order_label = tk.Label(plot_window,text='Color Order:',font=('Arial',10))
        color_order_label.place(x=900,y=440)
        color_order_entry = tk.Entry(plot_window,width=28)
        color_order_entry.place(x=975,y=440)

        # Generate preview button
        preview_button = tk.Button(plot_window,text='Generate Preview',font=('Arial',12),width=14,command=generate_preview)
        preview_button.place(x=900,y=475)
        
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################        
        
    # define stats
    def DZStats(self):
        # Place Holders
        bw = 10
        selected_options = ''
        selected_samples = ''  # Initialize as an empty list

        # Functions
        def get_samples():
            global selected_samples
            df = self.user_dataFrame.copy()
            all_samples = list(set(list(df['Sample ID'])))

            # set up a new window
            sample_window = tk.Toplevel()
            sample_window.title('Sample Selection')

            # set up check lists
            checkbox_vars = []
            for i, sample in enumerate(all_samples):
                var = tk.IntVar()
                checkbox = tk.Checkbutton(sample_window, text=sample, variable=var)
                checkbox.grid(row=i, column=0, sticky='w')
                checkbox_vars.append(var)

            def submit_samples():
                global selected_samples  # Use nonlocal to modify the outer variable
                selected_samples = [sample for sample, var in zip(all_samples, checkbox_vars) if var.get() == 1]
                sample_window.destroy()

            submit_button = tk.Button(sample_window, text='Submit', command=submit_samples)
            submit_button.grid(row=len(all_samples), column=0, pady=10)

        def get_plotting_options():
            global selected_options
            global bandwidth
            selected_options = []

            # Check the state of each plotting option checkbox
            if plot_type_var.get() == 'KDE':
                selected_options.append(('KDE', BW_entry.get()))
            elif plot_type_var.get() == 'PDP':
                selected_options.append(('PDP', 0))
            elif plot_type_var.get() == 'CDF':
                selected_options.append(('CDF', 0))

            return selected_options

        def get_plotting_arrays(selected_options):
            graph_hold = [[], []]
            global selected_samples
            for i, sample in enumerate(selected_samples):
                group = self.user_dataFrame.groupby('Sample ID')
                grouped = group.get_group(sample)
                ages = list(grouped['Best age'])
                errors = list(grouped['±'])
                option_type = selected_options[0][0]
                if option_type == 'KDE':
                    if selected_options[0][1] is None or selected_options[0][1] == '':
                        bw = 15
                    else:
                        bw = int(selected_options[0][1])
                    KDE_age, KDE = dFunc.KDEcalcAges([ages], x1=0, x2=4500, xdif=1, bw=bw, bw_x=None, cumulative=False)
                    graph_hold[0].append(KDE[0])

                if option_type == 'PDP':
                    PDP_age, PDP = dFunc.PDPcalcAges([ages], [errors], x1=0, x2=4500, xdif=1, cumulative=False)
                    graph_hold[0].append(PDP[0])

                CDF_age, CDF = dFunc.CDFcalcAges([ages], x1=0, x2=4500, xdif=1)
                graph_hold[1].append(CDF[0])
            return graph_hold

        def comparison():
            global selected_options
            global selected_samples
            graph_hold = get_plotting_arrays(selected_options)
            PA_array = graph_hold[0]
            CDF_array = graph_hold[1]
            comp_type = calc_type_var.get()
            # set up the dataframe
            temp_df = pd.DataFrame()
            if comp_type == 'DMAX':
                for i,CDF1 in enumerate(CDF_array):
                    temp_list = []
                    for w,CDF2 in enumerate(CDF_array):
                        dmax = dFunc.calcDmax(CDF1,CDF2)
                        temp_list.append(dmax)
                    temp_df[i] = temp_list

            if comp_type == 'VMAX':
                for i,CDF1 in enumerate(CDF_array):
                    temp_list = []
                    for w,CDF2 in enumerate(CDF_array):
                        vmax = dFunc.calcVmax(CDF1,CDF2)
                        temp_list.append(vmax)
                    temp_df[i] = temp_list

            if comp_type == 'SIM':
                for i,PA1 in enumerate(PA_array):
                    temp_list = []
                    for w,PA2 in enumerate(PA_array):
                        sim = dFunc.calcSimilarity(PA1,PA2)
                        temp_list.append(sim)
                    temp_df[i] = temp_list

            if comp_type == 'LIKE':
                for i,PA1 in enumerate(PA_array):
                    temp_list = []
                    for w,PA2 in enumerate(PA_array):
                        like = dFunc.calcLikeness(PA1,PA2)
                        temp_list.append(like)
                    temp_df[i] = temp_list

            if comp_type == 'R2':
                for i,PA1 in enumerate(PA_array):
                    temp_list = []
                    for w,PA2 in enumerate(PA_array):
                        R2 = dFunc.calcR2(PA1,PA2)
                        temp_list.append(R2)
                    temp_df[i] = temp_list


            temp_df.columns = selected_samples
            temp_df.index = selected_samples
            return temp_df



        def generate_plots():
            global selected_samples

            # Check if any samples are selected before trying to generate plots
            if not selected_samples:
                tk.messagebox.showinfo("Error", "Please select samples before generating plots.")
                return

            selected_options = get_plotting_options()
            graph_hold = get_plotting_arrays(selected_options)
            PA = graph_hold[0]

            # Clear the existing canvas
            if hasattr(stat_window, 'canvas'):
                stat_window.canvas.get_tk_widget().destroy()

            # Plot the probability plots
            if not hasattr(stat_window, 'ax'):
                stat_window.fig, stat_window.ax = plt.subplots(figsize=(6, 2.5))
                stat_window.ax.set_xlabel('Age (Ma)')

            # Clear existing lines from the plot
            stat_window.ax.clear()

            for i, sample_array in enumerate(PA):
                stat_window.ax.plot(sample_array, label=selected_samples[i])

                stat_window.ax.legend()
            stat_window.ax.grid(alpha=0.5)

            # Embed the plot in a Tkinter window
            canvas = FigureCanvasTkAgg(stat_window.fig, master=Prob_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.NONE, expand=1)

            # Store the canvas as an attribute of the main window
            stat_window.canvas = canvas
            ############################################################################################

            CDF_arrays = graph_hold[1]

            # Clear the existing canvas in the CDF frame
            if hasattr(stat_window, 'cdf_canvas'):
                stat_window.cdf_canvas.get_tk_widget().destroy()

            # Plot the CDF plots
            if not hasattr(stat_window, 'cdf_ax'):
                stat_window.cdf_fig, stat_window.cdf_ax = plt.subplots(figsize=(6, 2.5))
                stat_window.cdf_ax.set_xlabel('Age (Ma)')

            # Clear existing lines from the plot
            stat_window.cdf_ax.clear()

            for i, sample_array in enumerate(CDF_arrays):
                stat_window.cdf_ax.plot(sample_array, label=selected_samples[i])

            stat_window.cdf_ax.legend()
            stat_window.cdf_ax.grid(alpha=0.5)

            # Embed the plot in a Tkinter window
            cdf_canvas = FigureCanvasTkAgg(stat_window.cdf_fig, master=CDF_frame)
            cdf_canvas.draw()
            cdf_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.NONE, expand=1)

            # Store the canvas as an attribute of the main window
            stat_window.cdf_canvas = cdf_canvas

            # Plot heatmap
            #####################################################
            temp_df = comparison()
            mask = np.triu(np.ones_like(temp_df), k=1)

            # Create a new figure and axis
            stat_window.hmap_fig, stat_window.hmap_ax = plt.subplots(figsize=(5.9, 3.9))

            # Plot the heatmap using Seaborn
            sns.heatmap(temp_df, cmap='magma', annot=True, fmt=".2f", linewidths=.5, mask=mask, ax=stat_window.hmap_ax,vmax=1.0,vmin=0)

            # Remove existing colorbar
            if hasattr(stat_window, 'hmap_cbar'):
                stat_window.hmap_cbar.remove()

            # Clear the existing canvas in the HMap frame
            if hasattr(stat_window, 'hmap_canvas'):
                stat_window.hmap_canvas.get_tk_widget().destroy()

            # Embed the plot in a Tkinter window
            hmap_canvas = FigureCanvasTkAgg(stat_window.hmap_fig, master=HMap_frame)
            hmap_canvas.draw()
            hmap_canvas.get_tk_widget().place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            #hmap_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.NONE, expand=1)

            # Store the canvas as an attribute of the main window
            stat_window.hmap_canvas = hmap_canvas

            # Plot MDS
            ###########################################################################

            # Clear the existing canvas in the MDS frame
            if hasattr(stat_window, 'mds_canvas'):
                stat_window.mds_canvas.get_tk_widget().destroy()

            # Plot the MDS
            if not hasattr(stat_window, 'mds_ax'):
                stat_window.mds_fig, stat_window.mds_ax = plt.subplots(figsize=(2.5,3.85))

            # Clear existing lines from the plot
            stat_window.mds_ax.clear()

            # Convert to a numpy array
            comp_matrix = temp_df.values

            # Correct for R2, sim, and likeness
            calc_type = calc_type_var.get()
            if calc_type == 'SIM' or calc_type == 'LIKE' or calc_type == 'R2':
                diff_matrix = 1-comp_matrix
                comp_matrix = diff_matrix

            # Initialize MDS with the number of dimensions you want (e.g., 2 for a 2D plot)
            mds = MDS(n_components=2, dissimilarity="precomputed", random_state=42)

            # Fit the MDS model to the similarity matrix
            embedding = mds.fit_transform(comp_matrix)

            # Get the stress value
            stress_value = mds.stress_

            # Plot the MDS embedding
            stat_window.mds_ax.scatter(embedding[:, 0], embedding[:, 1])

            # Add labels or annotations with sample IDs
            for i, label in enumerate(selected_samples):
                x, y = embedding[i, 0], embedding[i, 1]
                stat_window.mds_ax.annotate(label, (x, y), textcoords="offset points", xytext=(5,5), ha='center')

            # Add text with the stress value to the figure
            stat_window.mds_ax.annotate(f"Stress: {stress_value:.4f}", xy=(0.5, 1.05), xycoords='axes fraction', ha='center', va='center')

            # Grid lines
            stat_window.mds_ax.grid(alpha=0.5)

            # Embed the plot in a Tkinter window
            mds_canvas = FigureCanvasTkAgg(stat_window.mds_fig, master=MDS_frame)
            mds_canvas.draw()
            mds_canvas.get_tk_widget().place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            
        # Interface layout
        ##################################

        # main window
        stat_window = tk.Toplevel()
        stat_window.title('DZHome - Stat Window')
        stat_window.geometry('1250x700')

        # CDF frame
        CDF_frame = tk.Frame(stat_window,width=595,height=250,borderwidth=1,relief='solid')
        CDF_frame.place(x=635,y=435)
        CDF_frame.configure(bg='white')

        # Prob frame
        Prob_frame = tk.Frame(stat_window,width=595,height=250,borderwidth=1,relief='solid')
        Prob_frame.place(x=15,y=435)
        Prob_frame.configure(bg='white')

        # MDS frame
        HMap_frame = tk.Frame(stat_window,width=595,height=395,borderwidth=1,relief='solid')
        HMap_frame.place(x=15,y=15)
        HMap_frame.configure(bg='white')

        # Heatmap frame
        MDS_frame = tk.Frame(stat_window, width = 300, height=395,borderwidth=1,relief='solid')
        MDS_frame.place(x=635,y=15)
        MDS_frame.configure(bg='white')

        # Sample select button
        sample_select_button = tk.Button(stat_window,text='Select Samples',width=20,font=('Arial',12),command=get_samples)
        sample_select_button.place(x=975,y=275)

        # Generate button
        generate_plots_button = tk.Button(stat_window,text='Generate Plots',width=20,font=('Arial',12),command=generate_plots)
        generate_plots_button.place(x=975,y=315)
        # Set the function to generate plots when the button is clicked
        generate_plots_button.config(command=generate_plots)

        # Options label
        options_label = tk.Label(stat_window,text='Dist. Options',font=('Arial',14))
        options_label.place(x=1015,y=40)

        # Plot type varialbe
        plot_type_var = tk.StringVar()

        # KDE Radiobutton
        KDE_radio = tk.Radiobutton(stat_window,text='KDE',font=('Arial',10),variable=plot_type_var,value='KDE')
        KDE_radio.place(x=975,y=75)

        #KDE bandthwidth entry
        KDE_bw = tk.Label(stat_window,text='BW:',font=('Arial',10))
        KDE_bw.place(x=1035,y=77)
        BW_entry = tk.Entry(stat_window,width=4)
        BW_entry.place(x=1073,y=77)

        # PDP Radiobutton
        PDP_radio = tk.Radiobutton(stat_window,text='PDP',font=('Arial',10),variable=plot_type_var,value='PDP')
        PDP_radio.place(x=1125,y=75)

        # Comparison label
        comp_label = tk.Label(stat_window,text='Comp. Options',font=('Arial',14))
        comp_label.place(x=1015,y=125)

        # Calc type variable
        calc_type_var = tk.StringVar()

        # Dmax Radiobutton
        Dmax_radio = tk.Radiobutton(stat_window,text='DMax',font=('Arial',10),variable=calc_type_var,value='DMAX')
        Dmax_radio.place(x=975,y=150)

        # Vmax Radiobutton
        Vmax_radio = tk.Radiobutton(stat_window,text='VMax',font=('Arial',10),variable=calc_type_var,value='VMAX')
        Vmax_radio.place(x=975,y=180)

        # # Kuiper Radiobutton
        # kuiper_radio = tk.Radiobutton(stat_window,text='Kuiper',font=('Arial',10),variable=calc_type_var,value='KUIPER')
        # kuiper_radio.place(x=975,y=210)

        # Similarity Radiobutton
        sim_radio = tk.Radiobutton(stat_window,text='Similiarity',font=('Arial',10),variable=calc_type_var,value='SIM')
        sim_radio.place(x=1075,y=150)

        # Likeness Radiobutton
        like_radio = tk.Radiobutton(stat_window,text='Likeness',font=('Arial',10),variable=calc_type_var,value='LIKE')
        like_radio.place(x=1075,y=180)

        # R2 Radiobutton
        R2_radio = tk.Radiobutton(stat_window,text='R2',font=('Arial',10),variable=calc_type_var,value='R2')
        R2_radio.place(x=1075,y=210)   
        
########################################################################################
########################################################################################
########################################################################################
########################################################################################
######################################################################################## 

    def DZMDA(self):
        # Placeholders
        selected_samples = ''
        selected_MDA = ''
        results_df = ''

        # Functions
        #####################################
        def get_samples():
            global selected_samples
            df = self.user_dataFrame.copy()
            all_samples = list(set(list(df['Sample ID'])))

            # set up a new window
            sample_window = tk.Toplevel()
            sample_window.title('Sample Selection')

            # set up check lists
            checkbox_vars = []
            for i, sample in enumerate(all_samples):
                var = tk.IntVar()
                checkbox = tk.Checkbutton(sample_window, text=sample, variable=var)
                checkbox.grid(row=i, column=0, sticky='w')
                checkbox_vars.append(var)

            def submit_samples():
                global selected_samples  # Use nonlocal to modify the outer variable
                selected_samples = [sample for sample, var in zip(all_samples, checkbox_vars) if var.get() == 1]
                sample_window.destroy()

            submit_button = tk.Button(sample_window, text='Submit', command=submit_samples)
            submit_button.grid(row=len(all_samples), column=0, pady=10)

        def get_plot_data(selected_samples):

            final_ages = [np.nan]
            final_errors = [np.nan]
            for i,sample in enumerate(selected_samples):
                group = self.user_dataFrame.groupby('Sample ID')
                grouped = group.get_group(sample)
                # First handle the ages
                ages = list(grouped['Best age'])
                sorted_ages = sorted(ages)[:5]
                for entry in sorted_ages:
                    final_ages.append(entry)
                final_ages.append(np.nan)

                # Now handle the errors
                errors = list(grouped['±'])
                temp_d = {}
                for age,error in zip(ages,errors):
                    temp_d[age] = error
                for age in sorted_ages:
                    error = temp_d[age]
                    final_errors.append(error)
                final_errors.append(np.nan)
            return final_ages,final_errors

        def get_MDAs():
            global selected_samples
            global selected_MDA
            all_ages = []
            all_errors = []
            for i, sample in enumerate(selected_samples):
                group = self.user_dataFrame.groupby('Sample ID')
                grouped = group.get_group(sample)
                ages = list(grouped['Best age'])
                errors = list(grouped['±'])
                all_ages.append(ages)
                all_errors.append(errors)
            all_ages = np.asarray(all_ages,dtype='object')
            all_errors = np.asarray(all_errors,dtype='object')

            all_MDAs = []
            all_sig = []

            if 'YSG' in selected_MDA:
                # Youngest single grain calc
                YSGs = np.asarray(MDA.YSG(all_ages,all_errors))
                all_MDAs.append(np.round(YSGs[:,0],2))
                all_sig.append(np.round(YSGs[:,1],2))

            if 'YC1s' in selected_MDA:
                # Youngest cluster 1 sigma calc
                YC1s = np.asarray(MDA.YC1s(all_ages,all_errors))
                all_MDAs.append(np.round(YC1s[:,0],2))
                all_sig.append(np.round(YC1s[:,1],2))

            if 'YC2s' in selected_MDA:
                # Youngest cluster 2 sigma calc
                YC2s = np.asarray(MDA.YC2s(all_ages,all_errors))
                all_MDAs.append(np.round(YC2s[:,0],2))
                all_sig.append(np.round(YC2s[:,1],2))

            if 'YDZ' in selected_MDA:
                # Youngest detrital zircon age calc
                YDZ = np.asarray(MDA.YDZ(all_ages,all_errors))
                all_MDAs.append(np.round(YDZ[:,0],2))
                all_sig.append(np.round(YDZ[:,1],2))

            if 'Y3Za' in selected_MDA:
                # Weighted mean average of youngest three zircons, no overlap
                Y3Za = np.asarray(MDA.Y3Za(all_ages,all_errors))
                all_MDAs.append(np.round(Y3Za[:,0],2))
                all_sig.append(np.round(Y3Za[:,1],2))

            if 'Y3Zo' in selected_MDA:
                # Weighted mean average of youngest three zircons, with overlap
                Y3Zo = np.asarray(MDA.Y3Zo(all_ages,all_errors))
                all_MDAs.append(np.round(Y3Zo[:,0],2))
                all_sig.append(np.round(Y3Zo[:,1],2))

            if 'YPP' in selected_MDA:
                # Youngest graphical peak
                YPP = np.asarray(MDA.YPP(all_ages,all_errors))
                all_MDAs.append(np.round(YPP,2))
                all_sig.append([0]*len(YPP))

            if 'YSP' in selected_MDA:
                # Youngest statstical population
                YSP = np.asarray(MDA.YSP(all_ages,all_errors))
                all_MDAs.append(np.round(YSP[:,0],2))
                all_sig.append(np.round(YSP[:,1],2))

            if 'TAU Method' in selected_MDA:
                # Tau method
                TAU = np.asarray(MDA.tauMethod(all_ages,all_errors))
                all_MDAs.append(np.round(TAU[:,0],2))
                all_sig.append(np.round(TAU[:,1],2))

            # Create results_df
            columns_list = ['Sample ID']
            for option in selected_MDA:
                columns_list.append(option)
                columns_list.append(str(option)+' 2sig')
            global results_df
            results_df = pd.DataFrame(columns = columns_list)
            results_df['Sample ID'] = selected_samples
            for i,option in enumerate(selected_MDA):
                results_df[option] = all_MDAs[i]
                results_df[str(option)+' 2sig'] = all_sig[i]

            # Assuming you want to set a fixed width for each column (e.g., 100 pixels)
            column_width = 100

            treeview = ttk.Treeview(results_frame, columns=list(results_df.columns), show='headings')

            for col in results_df.columns:
                treeview.heading(col, text=col)
                treeview.column(col, width=column_width)

            for index, row in results_df.iterrows():
                treeview.insert('', 'end', values=tuple(row))

            vsb = ttk.Scrollbar(results_frame, orient='vertical', command=treeview.yview)
            treeview.configure(yscrollcommand=vsb.set)

            hsb = ttk.Scrollbar(results_frame, orient='horizontal', command=treeview.xview)
            treeview.configure(xscrollcommand=hsb.set)

            treeview.grid(row=0, column=0, sticky='nsew')
            vsb.grid(row=0, column=1, sticky='ns')
            hsb.grid(row=1, column=0, sticky='ew')

            results_frame.grid_rowconfigure(0, weight=1)
            results_frame.grid_columnconfigure(0, weight=1)

            # Plot MDA fig

            # Get the data
            sorted_ages,sorted_errors = get_plot_data(selected_samples)

            # Make the scatter plot with error bars
            fig, ax = plt.subplots(figsize=(9.25,7.25))
            ax.scatter(np.arange(len(sorted_ages)), sorted_ages, s=15, color='black')
            ax.errorbar(np.arange(len(sorted_ages)), sorted_ages, yerr=sorted_errors, capsize=5, linestyle='None', color='black')
            ax.grid(axis='y', alpha=0.50)
            ax.invert_yaxis()
            ax.set_ylabel('Age (Ma)',fontsize=15)

            # Add vertical dashed lines at intervals
            for i in range(0, len(sorted_ages)+1, 6):
                ax.axvline(i, linestyle='--', color='black', alpha=0.75)

            # Plot the MDAs as rectangles on the same figure
            values = np.arange(0, len(sorted_ages)+1, 6)
            handles = []
            labels = []
            for mda in selected_MDA:
                if mda == 'YSG':
                    for i in range(len(selected_samples)):
                        y_loc = results_df.loc[i][mda] - (results_df.loc[i][str(mda)+' 2sig']/2)
                        x_loc = values[i]
                        height = 6
                        width = results_df.loc[i][str(mda)+' 2sig']

                        rect = patches.Rectangle((x_loc,y_loc),height,width, edgecolor='red', facecolor='red', alpha=0.5,label=mda)
                        ax.add_patch(rect)

                    # Collect handles and labels for legend
                    handles.append(rect)
                    labels.append(mda)

                if mda == 'YC1s':
                    for i in range(len(selected_samples)):
                        y_loc = results_df.loc[i][mda] - (results_df.loc[i][str(mda)+' 2sig']/2)
                        x_loc = values[i]
                        height = 6
                        width = results_df.loc[i][str(mda)+' 2sig']

                        rect = patches.Rectangle((x_loc,y_loc),height,width, edgecolor='tab:blue', facecolor='tab:blue', alpha=0.5,label=mda)
                        ax.add_patch(rect)

                    # Collect handles and labels for legend
                    handles.append(rect)
                    labels.append(mda)

                if mda == 'YC2s':
                    for i in range(len(selected_samples)):
                        y_loc = results_df.loc[i][mda] - (results_df.loc[i][str(mda)+' 2sig']/2)
                        x_loc = values[i]
                        height = 6
                        width = results_df.loc[i][str(mda)+' 2sig']

                        rect = patches.Rectangle((x_loc,y_loc),height,width, edgecolor='green', facecolor='green', alpha=0.5,label=mda)
                        ax.add_patch(rect)

                    # Collect handles and labels for legend
                    handles.append(rect)
                    labels.append(mda)

                if mda == 'YDZ':
                    for i in range(len(selected_samples)):
                        y_loc = results_df.loc[i][mda] - (results_df.loc[i][str(mda)+' 2sig']/2)
                        x_loc = values[i]
                        height = 6
                        width = results_df.loc[i][str(mda)+' 2sig']

                        rect = patches.Rectangle((x_loc,y_loc),height,width, edgecolor='orange', facecolor='orange', alpha=0.5,label=mda)
                        ax.add_patch(rect)

                    # Collect handles and labels for legend
                    handles.append(rect)
                    labels.append(mda)

                if mda == 'Y3Za':
                    for i in range(len(selected_samples)):
                        y_loc = results_df.loc[i][mda] - (results_df.loc[i][str(mda)+' 2sig']/2)
                        x_loc = values[i]
                        height = 6
                        width = results_df.loc[i][str(mda)+' 2sig']

                        rect = patches.Rectangle((x_loc,y_loc),height,width, edgecolor='indigo', facecolor='indigo', alpha=0.5,label=mda)
                        ax.add_patch(rect)

                    # Collect handles and labels for legend
                    handles.append(rect)
                    labels.append(mda)

                if mda == 'Y3Zo':
                    for i in range(len(selected_samples)):
                        y_loc = results_df.loc[i][mda] - (results_df.loc[i][str(mda)+' 2sig']/2)
                        x_loc = values[i]
                        height = 6
                        width = results_df.loc[i][str(mda)+' 2sig']

                        rect = patches.Rectangle((x_loc,y_loc),height,width, edgecolor='goldenrod', facecolor='goldenrod', alpha=0.5,label=mda)
                        ax.add_patch(rect)

                    # Collect handles and labels for legend
                    handles.append(rect)
                    labels.append(mda)

                if mda == 'YPP':
                    for i in range(len(selected_samples)):
                        y_loc = results_df.loc[i][mda] - (results_df.loc[i][str(mda)+' 2sig']/2)
                        x_loc = values[i]
                        height = 6
                        width = results_df.loc[i][str(mda)+' 2sig']

                        rect = patches.Rectangle((x_loc,y_loc),height,width, edgecolor='navy', facecolor='navy', alpha=0.5,label=mda)
                        ax.add_patch(rect)

                    # Collect handles and labels for legend
                    handles.append(rect)
                    labels.append(mda)

                if mda == 'YSP':
                    for i in range(len(selected_samples)):
                        y_loc = results_df.loc[i][mda] - (results_df.loc[i][str(mda)+' 2sig']/2)
                        x_loc = values[i]
                        height = 6
                        width = results_df.loc[i][str(mda)+' 2sig']

                        rect = patches.Rectangle((x_loc,y_loc),height,width, edgecolor='forestgreen', facecolor='forestgreen', alpha=0.5,label=mda)
                        ax.add_patch(rect)

                    # Collect handles and labels for legend
                    handles.append(rect)
                    labels.append(mda)

                if mda == 'TAU Method':
                    for i in range(len(selected_samples)):
                        y_loc = results_df.loc[i][mda] - (results_df.loc[i][str(mda)+' 2sig']/2)
                        x_loc = values[i]
                        height = 6
                        width = results_df.loc[i][str(mda)+' 2sig']

                        rect = patches.Rectangle((x_loc,y_loc),height,width, edgecolor='violet', facecolor='violet', alpha=0.5,label=mda)
                        ax.add_patch(rect)

                    # Collect handles and labels for legend
                    handles.append(rect)
                    labels.append(mda)

            # Outside the loop, add a legend with the collected handles and labels
            ax.legend(handles, labels)

            # Destroy previous widgets in the frame
            for widget in plot_frame.winfo_children():
                widget.destroy()

            # Embed the matplotlib plot into the Tkinter frame
            canvas1 = FigureCanvasTkAgg(fig, master=plot_frame)
            canvas1.draw()
            canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            # Add the toolbar if needed (optional)
            toolbar1 = NavigationToolbar2Tk(canvas1, plot_frame)
            toolbar1.update()
            canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Interface layout
        ######################################

        # Main window
        mda_window = tk.Toplevel()
        mda_window.title('DZHome - MDA Window')
        mda_window.geometry('1400x800')

        # Plot frame
        plot_frame = tk.Frame(mda_window,width=950,height=770,borderwidth=1,relief='solid')
        plot_frame.place(x=435,y=15)
        plot_frame.configure(bg='white')

        # Table frame
        results_frame = tk.Frame(mda_window,borderwidth=1,relief='solid')
        results_frame.place(x=15,y=435,width=400,height=350)
        results_frame.configure(bg='white')

        # Table label
        table_label = tk.Label(mda_window,text='MDA Results:',font=('Arial',12))
        table_label.place(x=17,y=410)

        # Sample select button
        sample_select_button = tk.Button(mda_window,text='Select Samples',width=20,font=('Arial',12),command=get_samples)
        sample_select_button.place(x=15,y=15)

        # MDA options label
        mda_options = tk.Label(mda_window,text = 'MDA Calculation Options:',font=('Arial',12))
        mda_options.place(x=15,y=65)

        # Check frame
        check_frame = tk.Frame(mda_window,width=250,height=300)
        check_frame.place(x=15,y=95)

        # Checkboxes
        MDA_options = ['YSG','YC1s','YC2s','YDZ','Y3Za','Y3Zo','YPP','YSP','TAU Method']
        # set up check lists
        checkbox_vars = []
        for i, check in enumerate(MDA_options):
            var = tk.IntVar()
            checkbox = tk.Checkbutton(check_frame, text=check, variable=var)
            checkbox.grid(row=i, column=0, sticky='w')
            checkbox_vars.append(var)

        def submit_MDA():
            global selected_MDA
            selected_MDA = [check for check, var in zip(MDA_options, checkbox_vars) if var.get() == 1]

        # Submit MDA button
        submit_MDA_button = tk.Button(mda_window,text='Submit MDA',width=20,font=('Arial',12),command=submit_MDA)
        submit_MDA_button.place(x=15,y=325)

        # Generate results button
        generate_results = tk.Button(mda_window,text='Generate Results',width=20,font=('Arial',12),command = get_MDAs)
        generate_results.place(x=225,y=15)
########################################################################################
########################################################################################
########################################################################################
########################################################################################
######################################################################################## 

    def DZHydrofrac(self):
        # Place holders
        bw = 10
        test_sample = ''
        sample_group = ''
        iterations = 25
        select_df = ''
        t_bank = ''
        g = 9.81
        qz_dens = 2650
        zr_dens = 4650
        fluid_dens = 1000
        fluid_visc = 0.001

        # Define functions
        ###################################

        # Get test sammple
        def get_test_sample():
            global test_sample
            df = self.user_dataFrame.copy()
            all_samples = list(set(list(df['Sample ID'])))

            # Set up a new window
            sample_window = tk.Toplevel()
            sample_window.title('Test Sample Selection')

            # Set up a single IntVar for all radio buttons
            selected_var = tk.IntVar()

            # Create radio buttons using the same variable
            for i, sample in enumerate(all_samples):
                radio_button = tk.Radiobutton(sample_window, text=sample, variable=selected_var, value=i)
                radio_button.grid(row=i, column=0, sticky='w')

            def submit_sample():
                global test_sample
                test_sample_index = selected_var.get()
                if test_sample_index is not None:
                    test_sample = all_samples[test_sample_index]
                sample_window.destroy()

            submit_button = tk.Button(sample_window, text='Submit', command=submit_sample)
            submit_button.grid(row=len(all_samples), column=0, pady=10)

        # Get sample group
        def get_sample_group():
            global sample_group
            df = self.user_dataFrame.copy()
            all_samples = list(set(list(df['Sample ID'])))

            # set up a new window
            sample_window = tk.Toplevel()
            sample_window.title('Sample Selection')

            # set up check lists
            checkbox_vars = []
            for i, sample in enumerate(all_samples):
                var = tk.IntVar()
                checkbox = tk.Checkbutton(sample_window, text=sample, variable=var)
                checkbox.grid(row=i, column=0, sticky='w')
                checkbox_vars.append(var)

            def submit_samples():
                global sample_group  # Use nonlocal to modify the outer variable
                sample_group = [sample for sample, var in zip(all_samples, checkbox_vars) if var.get() == 1]
                sample_window.destroy()

            submit_button = tk.Button(sample_window, text='Submit', command=submit_samples)
            submit_button.grid(row=len(all_samples), column=0, pady=10)

        # Define the shift
        def size_shift(Dm):
            Dm_m = Dm/1000
            v = ((np.sqrt(25+(1.2*(g*(qz_dens-fluid_dens)*(Dm_m**3)/(fluid_visc**2))**(2/3)))-5)**(3/2)) * (fluid_visc/Dm_m)
            qz_Em = (v/fluid_visc) + np.sqrt(((v/fluid_visc)**2) + 48*((g*(qz_dens-fluid_dens)/(fluid_visc**2))**(2/3)))
            dz_Em = (v/fluid_visc) + np.sqrt(((v/fluid_visc)**2) + 48*((g*(zr_dens-fluid_dens)/(fluid_visc**2))**(2/3)))
            SS = math.log2((zr_dens-fluid_dens)/(qz_dens-fluid_dens)) - (3/2)*math.log2(dz_Em/qz_Em)
            return SS


        def do_all():
            global test_sample
            global sample_group
            global select_df
            global iterations
            global t_bank

            # Get data
            group = self.user_dataFrame.groupby('Sample ID')
            grouped = group.get_group(test_sample)
            ages = list(grouped['Best age'])
            errors = list(grouped['±'])
            grains_um = np.asarray(grouped['Long Axis (um)'])

            # Get the test KDE
            re_KDE_age, re_KDE = dFunc.KDEcalcAges_2([ages], x1=0, x2=4500, xdif=1, bw=15, cumulative=False)
            test_KDE = re_KDE[0]

            # Convert to mm
            grains_mm = grains_um/1000

            # Now convert to phi
            grains_phi = []
            for grain in grains_mm:
                if grain>0:
                    phi = -math.log2(grain)
                    grains_phi.append(phi)
            grains_phi = np.asarray(grains_phi)

            # Calculate characteristics of zircon distribution
            p_84 = np.percentile(grains_phi,84)
            p_16 = np.percentile(grains_phi,14)
            p_95 = np.percentile(grains_phi,95)
            p_05 = np.percentile(grains_phi,5)
            sorting = ((p_84-p_16)/4) + ((p_95-p_05)/6.6)
            std = np.std(grains_phi)
            avg_grain_mm = np.mean(grains_mm)
            avg_grain_phi = np.mean(grains_phi)

            # Calculate the shift
            nums = np.linspace(2,0.037,200)
            shifts = []
            for i in range(len(nums)):
                shift = size_shift(nums[i])
                shifts.append(shift)
            init = np.zeros(len(nums))
            for i,val2 in enumerate(nums):
                diff = abs(avg_grain_mm - val2)
                init[i] = diff
            min_index = np.argmin(init)
            shift = shifts[min_index]

            # Now save in a dataframe
            select_df = pd.DataFrame(columns = ['Sample ID','Test Sample Mean Grain Size (phi)','Host Size Shift','Sorting','STD'])
            select_df.loc[0] = test_sample,avg_grain_phi,shift,sorting,std

            # Set up the grain size model
            # Set up storage for host sediment
            X = []
            Y = []
            Z = []
            grains = []
            # Set up storage for Zr grains
            z_X = []
            z_Y = []
            z_Z = []
            z_grains = []
            # Set up the shifts
            q_l = (avg_grain_phi-shift)-(std*2)
            q_r = (avg_grain_phi-shift)+(std*2)
            step = 50
            mean_shift = np.linspace(q_l,q_r,step)
            # Set up the x and y
            for i in range(0,step):
                z=i
                line_mean = mean_shift[i]
                line_sigma = 0.05
                z_sigma = 0.05
                for w in range(0,step):
                    y=w
                    for t in range(0,step):
                        x=t
                        # Now sample the Qz distribution to find the grain size
                        ind_grain_size = np.random.normal(line_mean,line_sigma,1)
                        # Derive the zircon age distribution - NEEDS WORK
                        host_mm = (10**(-line_mean/3.322))
                        if host_mm > 0.01:
                            zr_shift = size_shift(host_mm)
                            ind_zr_size = np.random.normal(line_mean+zr_shift,z_sigma,1)
                        if host_mm < 0.01:
                            ind_zr_size = np.random.normal(line_mean+clay_shift,z_sigma,1) 
                        X.append(x)
                        Y.append(y)
                        Z.append(z)
                        grains.append(ind_grain_size[0])
                        z_grains.append(ind_zr_size[0])

            print('Model Size Cube Generated')
            # Remove test sample from sample group if needed
            if test_sample in sample_group:
                sample_group.remove(test_sample)

            # Set up a new dataframe
            new_df = pd.DataFrame(columns = self.user_dataFrame.columns)
            for index in self.user_dataFrame.index:
                if str(self.user_dataFrame.loc[index,'Sample ID']) in sample_group:
                    new_df.loc[index] = self.user_dataFrame.loc[index]

            # Set up the progress bar
            progress_window = tk.Toplevel()
            progress_window.title('Generating Models')

            # Storage
            t_bank = {}
            # Now set up the loop
            ppm_step = len(ages)
            iterations = int(iter_entry.get())

            # Create the progress bar widget
            progress_var = tk.DoubleVar()
            progress_bar = ttk.Progressbar(progress_window,variable=progress_var,length=300,mode='determinate')
            progress_bar.pack(pady=10)

            def update_progress_bar(value):
                progress_var.set(value)
                progress_window.update_idletasks()


            for w in range(0,iterations):
                picks = random.sample(z_grains,ppm_step)
                new_picks = []
                for entry in picks:
                    um = (10**(-entry/3.322))*1000
                    new_picks.append(um)
                final_ages = []
                final_picks = []
                for entry in new_picks:
                    test = entry
                    five_per = test*0.05
                    test_ages = []
                    for index in new_df.index:
                        grain_length = new_df.loc[index,'Long Axis (um)']
                        if (grain_length-five_per) <= test and (grain_length + five_per) >= test:
                            test_ages.append(new_df.loc[index,'Best age'])
                    if len(test_ages) != 0:
                        final_picks.append(entry)
                    if len(test_ages) == 0:
                        continue
                    # Now covert to KDE
                    test_2 = []
                    test_2.append(test_ages)
                    test_2 = np.asarray(test_2)
                    KDE_age,KDE = dFunc.KDEcalcAges_2(test_2, x1=0, x2=4500, xdif=1, bw=15, cumulative=False)
                    # Now sample from the KDE
                    age_pick = np.random.choice(np.arange(0,4501),p = np.sum(KDE, axis = 0)/np.sum(KDE))
                    final_ages.append(age_pick)
                # Show as a KDE
                if len(final_ages)==0:
                    continue
                final = []
                final.append(final_ages)
                final = np.asarray(final)
                final_KDE_age,final_KDE = dFunc.KDEcalcAges_2(final, x1=0, x2=4500, xdif=1, bw=15, cumulative=False)
                model_coverage = len(final_ages)/ppm_step
                R2 = dFunc.calcR2(test_KDE,final_KDE[0])
                t_bank[w] = [final_picks,final_ages,final_KDE[0],model_coverage,R2]

                # Progress bar
                progress_value = (w+1)*100/iterations
                update_progress_bar(progress_value)
                progress_window.update()

            # Delete progress bar
            progress_window.destroy()


            # Plot the best results

            # Get the KDE with the highest R2 score
            max_key = max(t_bank, key = lambda k: t_bank[k][-1])
            max_KDE = t_bank[max_key][2]

            # Destroy any previous plots
            for widget in best_frame.winfo_children():
                widget.destroy()

            # Plot the results
            fig, ax = plt.subplots(figsize=(9,3.75))
            ax.plot(test_KDE,alpha=0.55,label=test_sample,color='black')
            ax.plot(max_KDE,alpha=0.85,label=str(test_sample)+' best model',color='green')
            plt.grid(alpha=0.5)
            plt.xlabel('Age (Ma)')
            plt.legend()
            plt.title('Best Model Results')

            # Add the R2 score as text outside the plot area:
            R2_text = 'R2 Score: ' + str(round(t_bank[max_key][4],3))
            ax.annotate(R2_text, xy=(0.5, 0.95), xycoords='axes fraction',
                    ha='center', va='center', fontsize=10, bbox=dict(boxstyle='round', alpha=0.1))

            # Adjust padding:
            fig.subplots_adjust(bottom=0.15)

            # Plot in the canvas
            best_canvas = FigureCanvasTkAgg(fig,master=best_frame)
            best_canvas.draw()
            best_canvas.get_tk_widget().pack(side=tk.TOP,fill=tk.BOTH,expand=1)



            # Plot all the results
            for widget in all_frame.winfo_children():
                widget.destroy()

            # Plot the results
            fig,ax = plt.subplots(figsize=(9,3.75))
            for i in range(len(t_bank)):
                if i != max_key:
                    ax.plot(t_bank[i][2],alpha=0.35,color='red')
            ax.plot(test_KDE,alpha=0.85,label=test_sample,color='black')
            plt.grid()
            plt.xlabel('Age (Ma)')
            plt.legend()
            plt.title('All Model Results')

            # Adjust padding:
            fig.subplots_adjust(bottom=0.15)

            #Plot in the canvas
            all_canvas = FigureCanvasTkAgg(fig,master=all_frame)
            all_canvas.draw()
            all_canvas.get_tk_widget().pack(side=tk.TOP,fill=tk.BOTH,expand=1)

            # Plot all the R2 scores
            all_r2 = []
            all_coverage = []
            for i in range(len(t_bank)):
                all_r2.append(t_bank[i][4])
                all_coverage.append(t_bank[i][3])

            vi_df = pd.DataFrame({'R2 Scores':all_r2, 'Model Coverage':all_coverage})

            # Clear the frame
            for widget in v_frame.winfo_children():
                widget.destroy()

            fig,ax = plt.subplots(figsize=(4.43,2.87))
            sns.violinplot(data=vi_df)
            plt.ylim([-0.1,1.1])
            plt.grid()
            plt.title('Model Data')

            # Adjust padding:
            fig.subplots_adjust(bottom=0.2)

            # Plot in the canvas
            r2_canvas = FigureCanvasTkAgg(fig,master=v_frame)
            r2_canvas.draw()
            r2_canvas.get_tk_widget().pack(side=tk.TOP,fill=tk.BOTH,expand=1)

            # Mdoel results table

            # Create the table
            table_df = pd.DataFrame(columns = ['Model Run','R2 Score','Model Coverage'])
            sorted_t_bank = dict(sorted(t_bank.items(), key=lambda item: item[1][4],reverse=True))
            for key in sorted_t_bank:
                table_df.loc[len(table_df.index)] = key,round(sorted_t_bank[key][4],3),round(sorted_t_bank[key][3],3)


            table_treeview = ttk.Treeview(r2_results,columns = list(table_df.columns),show='headings')

            for col in table_df.columns:
                table_treeview.heading(col,text=col)
                table_treeview.column(col,width=140)

            for index,row in table_df.iterrows():
                table_treeview.insert('','end',values=tuple(row))

            t_vsb = ttk.Scrollbar(r2_results,orient='vertical',command=table_treeview.yview)
            table_treeview.configure(yscrollcommand=t_vsb.set)

            t_hsb = ttk.Scrollbar(r2_results,orient='horizontal',command=table_treeview.xview)
            table_treeview.configure(xscrollcommand=t_hsb.set)

            table_treeview.grid(row=0,column=0,sticky='nsew')
            t_vsb.grid(row=0,column=1,sticky='ns')
            t_hsb.grid(row=1,column=0,sticky='ew')

            r2_results.grid_rowconfigure(0,weight=1)
            r2_results.grid_columnconfigure(0,weight=1)



        # Hydrofrac interface layout
        ###################################

        # Main window
        h_window = tk.Tk()
        h_window.title('DZHome - Hydrofrac Window')
        h_window.geometry('1400x800')

        # Frame for the best model results
        best_frame = tk.Frame(h_window,width=900,height=377.5,borderwidth=1,relief='solid')
        best_frame.place(x=15,y=15)
        best_frame.configure(bg='white')

        # Frame for all model results
        all_frame = tk.Frame(h_window,width=900,height=377.5,borderwidth=1,relief='solid')
        all_frame.place(x=15,y=407.5)
        all_frame.configure(bg='white')

        # Frame for R2 results plot
        r2_results = tk.Frame(h_window,borderwidth=1,relief='solid')
        r2_results.place(x=935,y=500,width= 445,height=285.5)
        r2_results.configure(bg='white')

        # Frame for violin plot
        v_frame = tk.Frame(h_window,width=445,height=285.5,borderwidth=1,relief='solid')
        v_frame.place(x=935,y=200.5)
        v_frame.configure(bg='white')

        # Test sample button
        test_button = tk.Button(h_window,text='Select Test Sample',width=21,font=('Arial',12),command=get_test_sample)
        test_button.place(x=935,y=15)

        # Test group button
        group_button = tk.Button(h_window,text='Select Sample Group',width=21,font=('Arial',12),command=get_sample_group)
        group_button.place(x=935,y=55)

        # Number of iterations
        iter_label = tk.Label(h_window,text='Number of Iterations:',font=('Arial',12))
        iter_label.place(x=935,y=105)
        iter_entry = tk.Entry(h_window,width=7)
        iter_entry.place(x=1085,y=105)

        # Generate button
        generate_button = tk.Button(h_window,text='Generate Results',width=21,font=('Arial',12),command = do_all)
        generate_button.place(x=935,y=135)

    def create_main_portal(self):
        self.main_window = tk.Tk()
        self.main_window.title('DZHome - Main Window')
        self.main_window.geometry('1000x600')

        welcome = tk.Label(self.main_window, text='Welcome to DZHome!', font=('Arial', 15))
        welcome.place(x=10, y=10)

        instructions = tk.Text(self.main_window, wrap='word')
        instructions.place(x=10, y=40, width=500, height=275)
        instructions_text = """DZHome is a Python software packages that can explore detrital zircon U-Pb data.  
        
        DZHome has four major functions: Plot, Stats, MDA, and Hydrofrac. Plot is plotting utility that allows users to plot age distributions in a variety of ways. Stat allows users to test metrics of similarity. MDA allows users to calculate MDAs of samples in various ways. Hydrofrac allows users to explore the amount of hydrodynamic fractionation present in samples."""
        instructions.insert('1.0', instructions_text)
        instructions.config(state='disabled')

        # DataTables
        main_table_frame = tk.Frame(self.main_window)
        main_table_frame.place(x=10, y=350, width=980, height=225)

        treeview1 = ttk.Treeview(main_table_frame, columns=list(self.user_dataFrame.columns), show='headings')
        for col in self.user_dataFrame.columns:
            treeview1.heading(col, text=col)
            treeview1.column(col, width=100)
        for index, row in self.user_dataFrame.iterrows():
            treeview1.insert('', 'end', values=tuple(row))

        vsb1 = ttk.Scrollbar(main_table_frame, orient='vertical', command=treeview1.yview)
        treeview1.configure(yscrollcommand=vsb1.set)

        hsb1 = ttk.Scrollbar(main_table_frame, orient='horizontal', command=treeview1.xview)
        treeview1.configure(xscrollcommand=hsb1.set)

        treeview1.grid(row=0, column=0, sticky='nsew')
        vsb1.grid(row=0, column=1, sticky='ns')
        hsb1.grid(row=1, column=0, sticky='ew')

        main_table_frame.grid_rowconfigure(0, weight=1)
        main_table_frame.grid_columnconfigure(0, weight=1)

        data_label = tk.Label(self.main_window, text='Data Table:')
        data_label.place(x=10, y=325)
        
        # Define the DZPlot Button
        DZPlot_button = tk.Button(self.main_window,text='Plot',font=('Arial',25),height=2,width=11,command=self.DZPlot)
        DZPlot_button.place(x=525,y=40)
        
        # Define the DZStat Button
        DZStat_button = tk.Button(self.main_window,text='Stats',font=('Arial',25),height=2,width=11,command=self.DZStats)
        DZStat_button.place(x=765,y=40)
        
        # Define the DZMDA Button
        DZMDA_button = tk.Button(self.main_window,text='MDA',font=('Arial',25),height=2,width=11,command=self.DZMDA)
        DZMDA_button.place(x=525,y=165)
        
        # Define the DZHydrofrac Button
        DZhydro_button = tk.Button(self.main_window,text='Hydrofrac',font=('Arial',25),height=2,width=11,command=self.DZHydrofrac)
        DZhydro_button.place(x=765,y=165)

        self.main_window.resizable(True, True)
        self.main_window.mainloop()

# Run the application
app = DZPlotApp()