#!/usr/bin/env python

#First import the netcdf4 library
from netCDF4 import Dataset  # http://code.google.com/p/netcdf4-python/
import numpy as np  # http://code.google.com/p/netcdf4-python/
import matplotlib
import math
import os
#matplotlib.use("GTKAgg")
from pylab import *
#import matplotlib.pyplot as plt
import pdb
import netCDF4 as nc
import sys
import argparse
from m6toolbox  import section2quadmesh
from static_shelf_comparison import *

##########################################################  Main Program   #########################################################################
####################################################################################################################################################




def parseCommandLine():
        """
        Parse the command line positional and optional arguments.
        This is the highest level procedure invoked from the very end of the script.
        """

        parser = argparse.ArgumentParser(description=
        '''
        Plot snapshots of either surface or vertical sections, for Tech paper.
        ''',
        epilog='Written by Alon Stern, Dec. 2016.')
	
	#Adding an extra boolian type argument
        parser.register('type','bool',str2bool) # add type keyword to registries



	#Adding arguments:

	#Saving figure
	parser.add_argument('-save_figure', type='bool', default=False,
		                        help=''' When true, the figure produced by the script is saved''')

	#Using Multiple fields
	parser.add_argument('-use_multiple_fields', type='bool', default=False,
		                        help=''' When true, the script uses multiple fields, seperated by _ for fieldname, units, scale....''')
	
	#parser.add_argument('', type='bool', default=,
	#	                        help='''    ''')

	#General flags
	parser.add_argument('-rotated', type='bool', default=True,
		                        help=''' Rotates the figures so that latitude runs in the vertical (involves switching x and y. ''')
	
	parser.add_argument('-use_ALE', type='bool', default=True,
		                        help='''When true, it uses the results of the ALE simulations. When false, layed simulations are used.    ''')
	
	parser.add_argument('-use_simulations_with_wind', type='bool', default=False,
		                        help='''When true, use the newer simulations with wind on from the start.   ''')
	
	parser.add_argument('-use_Revision', type='bool', default=True,
		                        help='''When true, it uses the results of the Revision simulations (including new drag and rolling)    ''')
	
	parser.add_argument('-use_Mixed_Melt', type='bool', default=False,
		                        help=''' When true, figure plots using Mixed_melt_data ''')
	
	parser.add_argument('-use_days_title', type='bool', default=False,
		                        help=''' When true, the day number is used as a title for the figures. ''')
	#What to plot?
	parser.add_argument('-plot_horizontal_field', type='bool', default=True,
		                        help='''    ''')
	#Which simulation to use
	parser.add_argument('-simulation', type=str, default='Collapse',
		                        help='''String determines which simulation to run. Options are Collapse, fixed_01, after_melt_fixed_01, high_melt. ''')

	#Using Multiple Anomaly
	parser.add_argument('-multiple_plot_anomaly', type=str, default="None",
		                        help=''' When true, the script uses multiple values of plot_anomaly...''')
	
	#Using Multiple Dir_slice_num
	parser.add_argument('-multiple_dir_slice_num', type=str, default="None",
		                        help=''' When true, the script uses multiple values of dir_slice_num...''')

	#Multiple vmax
	parser.add_argument('-multiple_vmax', type=str, default="None",
		                        help=''' If present, it provides values for vmax when script uses multiple fields.''')


	#Multiple vmin
	parser.add_argument('-multiple_vmin', type=str, default="None",
		                        help=''' If present, it provides values for vmin when script uses multiple fields.''')


	#Multiple vanom
	parser.add_argument('-multiple_vanom', type=str, default="None",
		                        help=''' If present, it provides values for vanom when script uses multiple fields.''')

	#Which file type to use
	parser.add_argument('-extension', type=str, default='icebergs_month.nc',
		                        help='''String determines which file type to used. icebergs_month.nc, prog.nc, ocean_month.nc, ocean_month_z.nc ''')

	#Which time slices to use
	parser.add_argument('-time_ind1', type=int, default=1,
		                        help='''Time index of snapshot 1  ''')
	parser.add_argument('-time_ind2', type=int, default=2,
		                        help='''Time index of snapshot 2  ''')
	parser.add_argument('-time_ind3', type=int, default=3,
		                        help='''Time index of snapshot 3  ''')
	
	#Plotting parameters
	parser.add_argument('-cmap', type=str, default='jet',
		                        help='''Colormap to use when producing the figure ''')

	parser.add_argument('-field', type=str, default='temp',
		                        help=''' Which field is being plotted  ''')

	parser.add_argument('-vmin', type=float, default=0.0,
		                        help='''Minimum value used for plotting''')

	parser.add_argument('-vmax', type=float, default=1.0,
		                        help='''Maximum values used for plotting''')

	parser.add_argument('-vanom', type=float, default=0.3,
		                        help='''This is the color scale when plot_anomaly=True. Goes from [-vanom vanom]''')

	parser.add_argument('-flipped', type='bool', default=False,
		                        help=''' The panel is flipped over so that it faces the other way.''')
	
	parser.add_argument('-mask_using_bergs', type='bool', default=False,
		                        help='''When true, the iceberg is masked out using the iceberg file (when you only want the ocean)''')

	parser.add_argument('-plot_anomaly', type='bool', default=False,
		                        help=''' If true, then figure plots the anomaly from the initial value, using color scale -vanom ''')

	parser.add_argument('-vertical_coordinate', type=str, default='layers',
			help='''Describes which type of ocean_month file is being used. Options: layers, z''')

	parser.add_argument('-time_slice', type=str, default='',
			help='''Time slice tells the code whether to do a time mean or a snapshot. Options: mean, None (default is snapshot)''')

	parser.add_argument('-xmin', type=float, default=0.0,
		                        help='''Minimum x used for plotting (only applies to vertical sectins for now)''')

	parser.add_argument('-xmax', type=float, default=960.0,
		                        help='''Minimum x used for plotting (only applies to vertical sectins for now)''')

	parser.add_argument('-ylim_min', type=float, default=240.0,
		                        help='''Minimum y used for plotting (only applies to horizontal sections)''')

	parser.add_argument('-ylim_max', type=float, default=440.0,
		                        help='''Minimum y used for plotting (only applies to horizontal sections)''')

	parser.add_argument('-dir_slice_num', type=int, default=1,
		                        help='''The index of the transect used (in the direction not plotted''')
	
	parser.add_argument('-dashed_num', type=int, default=1,
		                        help='''The index where the dashed line is plotted''')
	parser.add_argument('-dashed_num_hor', type=int, default=1,
		                        help='''The index where the horizontal dashed line is plotted''')


	parser.add_argument('-colorbar_units', type=str, default='',
		                        help='''The units for the colorbar''')
	
	parser.add_argument('-second_colorbar_units', type=str, default='',
		                        help='''The units for the colorbar''')
	
	parser.add_argument('-plot_second_colorbar', type='bool', default=False,
		                        help=''' If true, then plots two colorbars ''')
	
	parser.add_argument('-plot_xz_direction', type='bool', default=False,
		                        help=''' If true, then plots xz profile''')

	parser.add_argument('-plot_topog', type='bool', default=True,
		                        help=''' If true, then plots xz profile''')
	
	parser.add_argument('-mask_out_ocean', type='bool', default=False,
		                        help=''' If true, then masks out the ocean''')

        optCmdLineArgs = parser.parse_args()
        return optCmdLineArgs



def main(args):
	#parser = argparse.ArgumentParser()
	#args = parser.parse_args()


	#Plotting flats
	print args.save_figure
	save_figure=args.save_figure

	#General flags
	rotated=args.rotated
	use_ALE=args.use_ALE
	use_Revision=args.use_Revision
	use_days_title=args.use_days_title
	use_Mixed_Melt=args.use_Mixed_Melt

	#What to plot?
        plot_horizontal_field=args.plot_horizontal_field
	number_of_plots=3

	#Which simulation to use
	simulation=args.simulation

	#Defining path
	use_Wind_flag=''
	if args.use_simulations_with_wind is True:
		use_Wind_flag='Wind_'
		berg_path='/lustre/f1/unswept/Alon.Stern/MOM6-examples_Alon/ice_ocean_SIS2/Lagrangian_ISOMIP/Bergs/'
		Geometry_path=berg_path+'Static_with_Wind/' 
	else:
		berg_path='/lustre/f1/unswept/Alon.Stern/MOM6-examples_Alon/ice_ocean_SIS2/Tech_ISOMIP/Bergs/'
		Geometry_path=berg_path+'Melt_on_high_melt_with_decay/'

	ALE_flag=''
	Revision_flag=''
	xz_flag=''
	if use_ALE is True:
		ALE_flag='ALE_z_'
		if use_Revision is True:
			Revision_flag='Revision_'
			berg_path=berg_path+Revision_flag
		berg_path=berg_path+ALE_flag
	Mixed_Melt_flag=''
	if use_Mixed_Melt is True:
		Mixed_Melt_flag='Mixed_Melt_'
		berg_path=berg_path+Mixed_Melt_flag
	if simulation=='high_melt':
		Berg_path=berg_path+'Melt_on_high_melt_with_decay/'
		Berg_path_init=berg_path+'Melt_on_high_melt_with_decay_initialize/'
	elif simulation=='fixed_01':
		Berg_path=berg_path+'fixed_speed_Moving_berg_trimmed_shelf_from_zero_small_step_u01/'
		Berg_path_init=berg_path+'fixed_speed_Moving_berg_trimmed_shelf_from_zero_small_step_u01/'
	elif simulation=='after_melt_fixed_01':
		Berg_path=berg_path+'After_melt_fixed_speed_small_step_u01/'
		Berg_path_init=berg_path+'After_melt_fixed_speed_small_step_u01/'
	elif simulation=='Collapse':
		Berg_path=berg_path+'After_melt_Collapse_diag_Strong_Wind/'
		Berg_path_init=berg_path+'After_melt_Collapse_diag_Strong_Wind/'
	elif simulation=='Splitting':
		Berg_path=berg_path+'After_melt_Collapse_diag_Strong_Wind_Splitting/'
		Berg_path_init=berg_path+'After_melt_Collapse_diag_Strong_Wind_Splitting/'
	elif simulation=='Drift':
		Berg_path=berg_path+'After_melt_drift_diag_Strong_Wind/'
		Berg_path_init=berg_path+'After_melt_drift_diag_Strong_Wind/'
	elif simulation=='Wind_Collapse':
		Berg_path=berg_path+'After_Collapse/'
		#Berg_path=berg_path+'Exp1/'
		#Berg_path_init=berg_path+'After_Collapse/'
		Berg_path_init=berg_path+'After_Static/'
	elif simulation=='Wind_Collapse5':
		Berg_path=berg_path+'After_Collapse5/'
		Berg_path_init=berg_path+'After_Static/'
	elif simulation=='Wind_Static':
		Berg_path=berg_path+'After_Static/'
		#Berg_path=berg_path+'Exp1/'
		#Berg_path_init=berg_path+'After_Collapse/'
		Berg_path_init=berg_path+'After_Static/'
	elif simulation=='Wind_Broken_Compare':
		Berg_path=berg_path+'After_Collapse/'
		#Berg_path2=berg_path+'After_Broken/'
		Berg_path2=berg_path+'Broken_with_Wind/'
		#Berg_path=berg_path+'Exp1/'
		#Berg_path_init=berg_path+'After_Collapse/'
		Berg_path_init=berg_path+'After_Static/'
		number_of_plots=2
	else:
		return


	extension=args.extension
	
	#Init file
	#filename_init=Berg_path_init+'00110101.ocean_month.nc'
	filename_init=Berg_path_init+'00110101.' +extension
	print filename_init

	#Geometry files
	ocean_geometry_filename=Geometry_path +'ocean_geometry.nc'
	ice_geometry_filename=Geometry_path+'/MOM_Shelf_IC.nc'
	ISOMIP_IC_filename=Geometry_path+'ISOMIP_IC.nc'


	#Berg files
	if simulation=='high_melt':
		Berg_ocean_file1=Berg_path+'00010101.'
		Berg_ocean_file2=Berg_path+'00060101.'
		Berg_ocean_file2=Berg_path+'00060101.'
	if simulation=='fixed_01':
		Berg_ocean_file1=Berg_path+'00010101.' 
		Berg_ocean_file1=Berg_path+'00010107.' 
		Berg_ocean_file2=Berg_path+'00010107.' 
		Berg_ocean_file3=Berg_path+'00010206.' 
	if simulation=='after_melt_fixed_01':
		Berg_ocean_file1=Berg_path+'00060101.'
		Berg_ocean_file2=Berg_path+'00060101.'
		Berg_ocean_file3=Berg_path+'00060101.'
	if simulation=='Collapse':
		Berg_ocean_file1=Berg_path+'00060101.'
		Berg_ocean_file2=Berg_path+'00060101.'
		Berg_ocean_file3=Berg_path+'00060101.'
	if simulation=='Splitting':
		Berg_ocean_file1=Berg_path+'00060101.'
		Berg_ocean_file2=Berg_path+'00060101.'
		Berg_ocean_file3=Berg_path+'00060101.'
	if simulation=='Drift':
		Berg_ocean_file1=Berg_path+'00060101.'
		Berg_ocean_file2=Berg_path+'00060101.'
		Berg_ocean_file3=Berg_path+'00060101.'
	if (simulation=='Wind_Collapse' or simulation=='Wind_Static') or (simulation=='Wind_Collapse5'):
		Berg_ocean_file1=Berg_path+'00110101.'
		Berg_ocean_file2=Berg_path+'00110101.'
		Berg_ocean_file3=Berg_path+'00110101.'
	if simulation=='Wind_Broken_Compare':
		Berg_ocean_file1=Berg_path+'00110101.'
		Berg_ocean_file2=Berg_path2+'00060101.'
		Berg_ocean_file3=Berg_path+'00110101.'

	Berg_ocean_file_list=np.array([Berg_ocean_file1 +extension ,Berg_ocean_file2+ extension ,Berg_ocean_file3 + extension])
	Iceberg_file_list=np.array([Berg_ocean_file1 +'icebergs_month.nc' ,Berg_ocean_file2+ 'icebergs_month.nc' ,Berg_ocean_file3 + 'icebergs_month.nc'])
	
	Berg_icebergs_file=Berg_path+'00010101.icebergs_month.nc'
#
	#Berg_ocean_file='/lustre/f1/unswept/Alon.Stern/MOM6-examples_Alon/ice_ocean_SIS2/Tech_ISOMIP/Bergs/Melt_on_with_decay/'+ '00010101.ocean_month.nc'

	#Load static fields
	(depth, shelf_area, ice_base, x,y, xvec, yvec)=load_static_variables(ocean_geometry_filename,ice_geometry_filename,ISOMIP_IC_filename,rotated=rotated)	
      	grounding_line=find_grounding_line(depth, shelf_area, ice_base, x,y, xvec, yvec)
	ice_front=find_ice_front(depth,shelf_area,x,y, xvec, yvec)
	
	#Defining figure characteristics
	#fig=plt.figure(figsize=(10,10),facecolor='grey')
	#fig = plt.figure(facecolor='black')
	#ax = fig.add_subplot(111,axisbg='gray')
	#time_slice_num=np.array([8, 24, 24])  #When using prog -fixed or high_melt
	#time_slice_num=np.array([220,580,580]) #When using ocean_month -fixed or high_melt
	#time_slice_num=np.array([14, 29, 59])  #When using prog -after_melt
	#time_slice_num=np.array([29,59,119])  #When using prog -after_melt  (ALE)
	#time_slice_num=np.array([19,39,79])  #When using prog -after_melt  (ALE)
	#time_slice_num=np.array([360,720,1439]) #When using ocean_month -after_melt
	time_slice_num=np.array([args.time_ind1, args.time_ind2, args.time_ind3])  #When using prog -after_melt
	
	letter_labels=np.array(['(a)','(b)','(c)','(d)','(e)'])
	title=''

	#Loading  some of the arguments from the parser
	cmap=args.cmap
	field=args.field
	vmin=args.vmin
	vmax=args.vmax
	vanom=args.vanom
	flipped=args.flipped
	time_slice=args.time_slice
	plot_anomaly=args.plot_anomaly
	vertical_coordinate=args.vertical_coordinate
	dir_slice_num=args.dir_slice_num
	dashed_num=args.dashed_num
	dashed_num_hor=args.dashed_num_hor
	colorbar_units = args.colorbar_units
	if args.use_multiple_fields is True:
		multiple_colorbar_units = colorbar_units
		multiple_fields = field
		multiple_vmax = args.multiple_vmax
		multiple_vmin = args.multiple_vmin
		multiple_vanom = args.multiple_vanom
		multiple_plot_anomaly = args.multiple_plot_anomaly
		multiple_dir_slice_num = args.multiple_dir_slice_num

	######################################################################################################################
	################################  Plotting melt comparison  ##########################################################
        ######################################################################################################################
        
        if plot_horizontal_field is True:
		fig, axes = plt.subplots(nrows=1,ncols=number_of_plots)
		fig.set_size_inches(15.0,10.0, forward=True)
		#fig=plt.figure(figsize=(15,10),facecolor='grey')
		ylim_min=args.ylim_min
		ylim_max=args.ylim_max
		for n in range(number_of_plots):
			#flipped=False
			#field='spread_area'  ;vmin=0.0  ; vmax=1.0
			#field='melt_m_per_year'  ;vmin=0.0  ; vmax=5.000
			#field='temp'  ;vmin=-2.0  ; vmax=-1.5
			#field='temp'  ;vmin=-1.8  ; vmax=-1.2  # After melt
			#field='u'  ;vmin=-0.05  ; vmax=0.05 ; # After melt
			#field='temp'  ;vmin=-1.8  ; vmax=-0.8  # After melt (ALE)
			
			#field='sst'  ;vmin=-1.8  ; vmax=-1.2
			#field='ustar_iceberg'  ;vmin=0  ; vmax=0.01
			#field='spread_uvel' ;vmin=-0.01  ; vmax=0.01
			filename=Berg_ocean_file_list[n]

			print filename
			(data1,time)=load_and_compress_data(filename,field=field,time_slice='',time_slice_num=time_slice_num[n]\
					,rotated=rotated,direction='xy',dir_slice=None, dir_slice_num=dir_slice_num, return_time=True,depth=depth, ice_base=ice_base)
			if simulation=='after_melt_fixed_01' or simulation=='Collapse' :
				time=time-1825
				print 'Subtracting t0', time

			if plot_anomaly is True:
				#(data0,time)=load_and_compress_data(filename,field=field,time_slice='',time_slice_num=0\
				#	,rotated=rotated,direction='xy',dir_slice=None, dir_slice_num=dir_slice_num, return_time=True)
				(data0,time)=load_and_compress_data(filename_init,field=field,time_slice='',time_slice_num=-1\
					,rotated=rotated,direction='xy',dir_slice=None, dir_slice_num=dir_slice_num, return_time=True,depth=depth, ice_base=ice_base)
				data1= data1-data0
				vmin=-vanom  ; vmax=vanom
				cmap='bwr'


			time_str=str(int(np.round(time)))
			ax=plt.subplot(1,number_of_plots,n+1)
			if args.mask_using_bergs is True:
				iceberg_filename=Iceberg_file_list[n]
				print iceberg_filename
				#ice_data=load_and_compress_data(iceberg_filename,field='spread_area',time_slice='',time_slice_num=time_slice_num[n],\
				#		rotated=rotated,direction='xy',dir_slice=None, dir_slice_num=dir_slice_num)
				#data1=mask_ice(data1,ice_data,tol=0.9)
				
				ice_data=load_and_compress_data(iceberg_filename,field='spread_mass',time_slice='',time_slice_num=time_slice_num[n],\
						rotated=rotated,direction='xy',dir_slice=None, dir_slice_num=dir_slice_num)
				data1=mask_ice(data1,ice_data,tol=1e4)
				
			        e=load_and_compress_data(filename,field='e',time_slice='',time_slice_num=time_slice_num[n]\
					,rotated=rotated,direction='xy',dir_slice=None, dir_slice_num=dir_slice_num, return_time=False)
				
				#greydata=plot_data_field(e,x,y,-150.0, 50.0,flipped,colorbar=False,cmap='Greys',title=title,xlabel='x (km)',ylabel='',ylim_min=ylim_min,\
				#	ylim_max=ylim_max,colorbar_units=args.colorbar_units,return_handle=True)  
				greydata=plot_data_field(e,x,y,-220.0, 0.0,flipped,colorbar=False,cmap='Greys',title=title,xlabel='x (km)',ylabel='',ylim_min=ylim_min,\
					ylim_max=ylim_max,colorbar_units=colorbar_units,return_handle=True)  
			if args.mask_out_ocean is True:
				data1=mask_ocean(data1,shelf_area)
				iceberg_filename=Iceberg_file_list[2]
				ice_data=load_and_compress_data(iceberg_filename,field='spread_area',time_slice='',time_slice_num=time_slice_num[2],\
						rotated=rotated,direction='xy',dir_slice=None, dir_slice_num=dir_slice_num)
				data1=mask_ocean(data1,ice_data, tol=0.99)
                		plt.plot(xvec,grounding_line, linewidth=3.0,color='black')
                		#plt.plot(xvec,ice_front, linewidth=3.0,color='black')

			if use_days_title is True:
				title='Time = '+ time_str + ' days'
			datamap=plot_data_field(data1,x,y,vmin,vmax,flipped,colorbar=False,cmap=cmap,title=title,xlabel='x (km)',ylabel='',ylim_min=ylim_min,\
					ylim_max=ylim_max,colorbar_units=colorbar_units,return_handle=True)  

			text(0.1,1,letter_labels[n], ha='right', va='bottom',transform=ax.transAxes,fontsize=20)
			if n==0:
				plt.ylabel('y (km)',fontsize=20)
			if n>0:
				ax.set_yticks([])
			if (n==2) and ( (args.field=='spread_area') or (args.field=='temp')) and (simulation=='Collapse'):
				plt.plot(np.array([xvec[dashed_num], xvec[dashed_num]]), np.array([130., 460.]),'--', color='k',linewidth=3 )
			if (n==0) and ( (args.field=='spread_area') or (args.field=='temp')) and (simulation=='Wind_Collapse'):
				plt.plot(np.array([xvec[dashed_num], xvec[dashed_num]]), np.array([130., 460.]),'--', color='k',linewidth=3 )
				plt.plot(np.array([0.0 ,  80.0]),  [yvec[dashed_num_hor], yvec[dashed_num_hor]], '--', color='darkblue',linewidth=3 )
				print("Dashed lines at: ", yvec[dashed_num_hor] , xvec[dashed_num])
		#Creating colorbar
		fig.subplots_adjust(right=0.85)
		if args.plot_second_colorbar is True:	
			cbar_ax = fig.add_axes([0.88,0.52 , 0.025, 0.4])
		else:
			cbar_ax = fig.add_axes([0.88,0.12 , 0.025, 0.75])
		cbar=fig.colorbar(datamap, cax=cbar_ax)
		cbar.set_label(colorbar_units, rotation=90,fontsize=20)
		cbar.ax.tick_params(labelsize=20)

		if args.plot_second_colorbar is True:	
			cbar_ax = fig.add_axes([0.88,0.05 , 0.025, 0.4])
			#cbar_ax = fig.add_axes([0.01,0.12 , 0.025, 0.45])
			if args.mask_using_bergs is True:
				cbar=fig.colorbar(greydata, cax=cbar_ax)
				cbar.set_label(args.second_colorbar_units, rotation=90,fontsize=20)
				cbar.ax.tick_params(labelsize=20)

		#For plotting purposes
		field=field + '_z' +str(dir_slice_num)

		####################################################################################################################################################
		####################################################  Cross Section     ############################################################################
		###################################################################################################################################################
	else:
		fig=plt.figure(figsize=(10,10),facecolor='grey')
		ax = fig.add_subplot(111,axisbg='gray')
		if rotated is True:
			direction='yz'
			dist=yvec
		else:
			direction='xz'
			dist=xvec
			xz_flag='XZ'

		if args.plot_xz_direction is True:
			direction='xz'
			dist=xvec

		for n in range(3):
			#plot_anomaly=False
			#vertical_coordinate='layers'  #'z'
			#vertical_coordinate='z'
			#time_slice=None
			#field='u'  ; vmin=-0.1  ; vmax=0.1    ; vanom=0.3 ; cmap='seismic'
			#field='v'  ; vmin=-0.1  ; vmax=0.1    ; vanom=0.3 ; cmap='seismic'
			#field='temp'  ; vmin=-2.0  ; vmax=1.0 ; vanom=0.3 ; cmap='jet'
			#field='salt'  ; vmin=34  ; vmax=34.7  ;vdiff=0.05  ; vanom=0.05 ; cmap='jet'

			#If you are using multiple fields this code gets run.
			if args.use_multiple_fields  is True:
				if '_' in multiple_fields:
					field = multiple_fields.split('_')[n]
					if field =="Kd":
						field =  field + "_" + multiple_fields.split('_')[n+1]
						print "Field", field
				if '_' in multiple_colorbar_units:
					colorbar_units = multiple_colorbar_units.split('_')[n]
				if '_' in multiple_plot_anomaly:
					plot_anomaly = (multiple_plot_anomaly.split('_')[n] =="True")
				if '_' in multiple_vmax:
					multiple_vmax = float(multiple_vmax.split('_')[n])
				if '_' in multiple_vmin:
					multiple_vmin = float(multiple_vmin.split('_')[n])
				if '_' in multiple_vanom:
					multiple_vanom = float(multiple_vanom.split('_')[n])
				if '_' in multiple_dir_slice_num:
					dir_slice_num = int(multiple_dir_slice_num.split('_')[n])
				



				
			
			filename=Berg_ocean_file_list[n]
			filename_layers = filename
			if n==0:
				filename_init_layers = filename_init
			if vertical_coordinate=='z':
				filename=filename.split('.nc')[0] + '_z.nc'
				if n==0:
					filename_init=filename.split('.nc')[0] + '_z.nc'
			if vertical_coordinate=='zold':
				filename=filename.split('.nc')[0] + '_zold.nc'
				if n==0:
					filename_init=filename_init.split('.nc')[0] + '_zold.nc'

			print filename

			(data1,time)=load_and_compress_data(filename,field , time_slice, time_slice_num=time_slice_num[n],\
					direction=direction ,dir_slice=None, dir_slice_num=dir_slice_num,rotated=rotated, return_time=True)
			if simulation=='after_melt_fixed_01' or simulation=='Collapse' :
				#time=time-1824.5
				time=time-1825.
				print 'Subtracting t0', time

			print "Data.shape", data1.shape
			time_str=str(int(np.round(time)))
			elevation1 = get_vertical_dimentions(filename,vertical_coordinate, time_slice, time_slice_num=time_slice_num[n],\
					direction=direction ,dir_slice=None, dir_slice_num=dir_slice_num,rotated=rotated)
			(y1 ,z1 ,data1) =interpolated_onto_vertical_grid(data1, elevation1, dist, vertical_coordinate)
			

			data1[np.where(data1>100)]=np.NaN
			data1[np.where(data1<-100)]=np.NaN
			data1=np.ma.array(data1, mask=np.isnan(data1))

			if plot_anomaly is True:
				time_init_num=0
				data0=load_and_compress_data(filename_init,field , time_slice=None, time_slice_num=time_init_num, \
						direction=direction ,dir_slice=None, dir_slice_num=dir_slice_num,rotated=rotated)
				elevation0 = get_vertical_dimentions(filename_init,vertical_coordinate, time_slice=None, time_slice_num=time_init_num, \
						direction=direction ,dir_slice=None, dir_slice_num=dir_slice_num,rotated=rotated)

				(y0 ,z0 ,data0) =interpolated_onto_vertical_grid(data0, elevation0, dist, vertical_coordinate)
				cutoff=-10000
				data1[np.where(data1<cutoff)]=np.NaN
				data0[np.where(data1<cutoff)]=np.NaN
				data1[np.where(data0<cutoff)]=np.NaN
				data0[np.where(data0<cutoff)]=np.NaN

				data1=data1-data0
				vmin=-vanom  ; vmax=vanom

				data1=np.ma.array(data1, mask=np.isnan(data1))
				cmap = matplotlib.cm.bwr
				cmap.set_bad('lightgrey',1)
			else:
				vmax=args.vmax
				vmin=args.vmin
					

			ax=plt.subplot(3,1,n+1)
			if use_days_title is True:
				title='Time = '+ time_str + ' days'
			plot_data_field(data1, y1, z1, vmin, vmax, flipped=False, colorbar=True, cmap=cmap,title=title,ylabel='Depth (m)', colorbar_units=colorbar_units)
			#xmin=450.  ;xmax=750.
			plt.xlim([args.xmin,args.xmax])
			
			if vertical_coordinate=='layers': 
				surface=np.squeeze(elevation1[0,:])
				plot(dist, surface,'black')
			else:
				#plotting ice shelf base
				elevation2 = get_vertical_dimentions(filename_layers,'layers', time_slice, time_slice_num=time_slice_num[n],\
						direction=direction ,dir_slice=None, dir_slice_num=dir_slice_num,rotated=rotated)
				surface=np.squeeze(elevation2[0,:])
				plot(dist, surface,color= 'black', linestyle=':')
				#Plotting original ice base
				if plot_anomaly is True:
					elevation2 = get_vertical_dimentions(filename_init_layers,'layers', time_slice, time_slice_num=time_init_num,\
						direction=direction ,dir_slice=None, dir_slice_num=dir_slice_num,rotated=rotated)
					surface=np.squeeze(elevation2[0,:])
					plot(dist, surface,color= 'black')

			if args.plot_topog is True:
				print("Yolo", depth.shape, len(dist))
				if direction == 'yz': 
					topog=np.squeeze(depth[:,dir_slice_num])
				else:
					topog=np.squeeze(depth[dir_slice_num,:])
				plt.plot(dist, -topog, 'black')
			#data1_tmp=data1
			#tol=0.000000000001
			#data1[np.where(abs(data1)<tol)]=10000.
			#data1[np.where(abs(data1)>tol)]=-10000.
			#masked_array = np.ma.array (data1, mask=np.isnan(data1))
			#levels1=np.array([0.05,999.])
			#cNorm2=mpl.colors.Normalize(vmin=400, vmax=1000)
			#print y1.shape,z1.shape
			#CS = contourf(y1, z1[, data1_tmp,levels=levels1, hatches=[' '], fill=False,cmap='Greys',norm=cNorm2 )
			#print data1
			
			text(0.075,1.0,letter_labels[n], ha='right', va='bottom',transform=ax.transAxes,fontsize=20)
			if n==2:
				if direction=='yz':
					plt.xlabel('y (km)',fontsize=20)
				else:
					plt.xlabel('x (km)',fontsize=20)
			if n<2:
				ax.set_xticks([])
		
		#For plotting purposes
		field=field+'_'+ vertical_coordinate + '_x' +str(dir_slice_num)
	if plot_anomaly is True:
		field=field+'_anomaly'


	mask_flag = ''
	if args.mask_using_bergs is True:
		mask_flag = 'mask'


	#plt.tight_layout()


	if save_figure==True:
		output_file='Figures/snapshots_'+ use_Wind_flag + xz_flag + Revision_flag +ALE_flag+Mixed_Melt_flag +simulation +'_'+ field +'_'+ mask_flag+ '.png'
		plt.savefig(output_file,dpi=300,bbox_inches='tight')
		print 'Saving ' ,output_file
		#print 'Saving file not working yet'

	#fig.set_size_inches(9,4.5)
	plt.show()
	print 'Script complete'



if __name__ == '__main__':
	optCmdLineArgs= parseCommandLine()
	main(optCmdLineArgs)
	#sys.exit(main())














